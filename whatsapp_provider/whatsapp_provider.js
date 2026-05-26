import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { makeWASocket, DisconnectReason, useMultiFileAuthState, makeCacheableSignalKeyStore, fetchLatestBaileysVersion } from "baileys";
import pino from "pino";
import path from "path";
import os from "os";
import fs from "fs";
import axios from "axios";

const logger = pino({ level: "silent" });
const AUTH_DIR = process.env.AUTH_DIR || path.join(os.homedir(), ".wabridge", "auth_store");
const WEBHOOK_URL = process.env.WEBHOOK_URL || "http://localhost:6000/webhook";
const API_PORT = Number(process.env.PORT) || 3000;

// Global state for deduplication to allow self-interaction without loops
const lastSentMessages = new Set();

const bridge = {
    sock: null,
    status: "disconnected",
};

/**
 * Normalizes a JID by removing device identifiers.
 */
function normalizeJid(jid) {
    if (!jid) return "";
    // Remove :device suffix if present (e.g., 919876543210:1@s.whatsapp.net -> 919876543210@s.whatsapp.net)
    return jid.split(':')[0].split('@')[0] + "@" + jid.split('@')[1];
}

async function startSocket() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion();
    
    console.log(`[*] Connecting to WhatsApp (v${version.join(".")})...`);
    
    bridge.sock = makeWASocket({
        version,
        logger,
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, logger),
        },
        printQRInTerminal: true,
    });

    // Save creds
    bridge.sock.ev.on("creds.update", saveCreds);

    // Connection update
    bridge.sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === "open") {
            bridge.status = "open";
            console.log("[*] WhatsApp Connected!");
            console.log(`[*] User Details: ${JSON.stringify(bridge.sock.user)}`);
        }
        if (connection === "close") {
            bridge.status = "disconnected";
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log("[!] Disconnected. Reconnecting:", shouldReconnect);
            if (shouldReconnect) startSocket();
        }
    });

    // --- INCOMING MESSAGE WEBHOOK ---
    bridge.sock.ev.on("messages.upsert", async (upsert) => {
        if (upsert.type === 'notify' || upsert.type === 'append') {
            for (const msg of upsert.messages) {
                const jid = msg.key.remoteJid;
                const isMe = msg.key.fromMe;
                
                const body = msg.message?.conversation || 
                             msg.message?.extendedTextMessage?.text;
                
                if (!body) continue;

                // --- SMART SELF-CHAT SECURITY CHECK ---
                // We need to identify if this message is in the "Message Yourself" thread.
                // RemoteJid can be the Phone JID (@s.whatsapp.net) or the Linked ID (@lid).
                
                const myJid = normalizeJid(bridge.sock.user.id);
                const myLid = bridge.sock.user.lid ? normalizeJid(bridge.sock.user.lid) : null;
                const chatJid = normalizeJid(jid);

                const isSelfThread = (chatJid === myJid) || (myLid && chatJid === myLid);

                if (!isMe) {
                    // console.log(`[DROP] Message from someone else in chat ${chatJid}`);
                    continue;
                }

                if (!isSelfThread) {
                    console.log(`[DROP] Message sent by you to an external chat (${chatJid})`);
                    continue;
                }

                // Deduplication logic: Check if this was a bot reply we just sent
                if (lastSentMessages.has(body)) {
                    console.log(`[INTERNAL] Bot's own reply (Deduplicated): ${body.substring(0, 50)}...`);
                    lastSentMessages.delete(body);
                    continue;
                }

                console.log(`[FORWARD] Self-chat message: ${body}`);
                
                // Forward to ADK Bridge
                try {
                    await axios.post(WEBHOOK_URL, {
                        event: "message",
                        data: {
                            from: jid,
                            body: body,
                            pushName: msg.pushName || "Self"
                        }
                    });
                } catch (err) {
                    console.error(`[!] Failed to send webhook: ${err.message}`);
                }
            }
        }
    });
}

// ─── HTTP API (Drop-in replacement for wabridge) ──────
const app = new Hono();

app.get("/status", (c) => {
    return c.json({
        status: bridge.status,
        user: bridge.sock?.user?.id || null,
    });
});

app.post("/send", async (c) => {
    try {
        const { phone, message } = await c.req.json();
        const jid = phone.includes("@") ? phone : `${phone}@s.whatsapp.net`;
        
        lastSentMessages.add(message);
        await bridge.sock.sendMessage(jid, { text: message });
        return c.json({ success: true, to: jid });
    } catch (err) {
        return c.json({ error: err.message }, 500);
    }
});

app.post("/send/self", async (c) => {
    try {
        const { message } = await c.req.json();
        const myJid = bridge.sock?.user?.id.replace(/:\d+@/, "@");
        
        lastSentMessages.add(message);
        await bridge.sock.sendMessage(myJid, { text: message });
        return c.json({ success: true, to: "self" });
    } catch (err) {
        return c.json({ error: err.message }, 500);
    }
});

// Start everything
startSocket();
serve({ fetch: app.fetch, port: API_PORT }, () => {
    console.log(`[*] WhatsApp Provider running on http://localhost:${API_PORT}`);
    console.log(`[*] Webhooks forwarding to ${WEBHOOK_URL}`);
    console.log(`[*] SMART Self-interaction ENABLED (Phone & LID support)`);
});
