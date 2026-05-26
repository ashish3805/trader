import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { makeWASocket, DisconnectReason, useMultiFileAuthState, makeCacheableSignalKeyStore, fetchLatestBaileysVersion } from "baileys";
import pino from "pino";
import path from "path";
import os from "os";
import fs from "fs";
import axios from "axios";

const logger = pino({ level: "silent" });
const AUTH_DIR = path.join(os.homedir(), ".wabridge", "auth_store");
const WEBHOOK_URL = "http://localhost:6000/webhook";
const API_PORT = 3000;

// Global state for deduplication to allow self-interaction without loops
const lastSentMessages = new Set();

const bridge = {
    sock: null,
    status: "disconnected",
};

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
        // console.log(`[*] Event messages.upsert received: ${upsert.type}`);
        
        if (upsert.type === 'notify' || upsert.type === 'append') {
            for (const msg of upsert.messages) {
                const jid = msg.key.remoteJid;
                const isMe = msg.key.fromMe;
                
                const body = msg.message?.conversation || 
                             msg.message?.extendedTextMessage?.text;
                
                if (!body) continue;

                // Deduplication logic
                if (isMe) {
                    if (lastSentMessages.has(body)) {
                        console.log(`[*] Ignoring bot's own reply: ${body}`);
                        lastSentMessages.delete(body);
                        continue;
                    }
                }

                console.log(`[*] Incoming message from ${jid} (fromMe: ${isMe}): ${body}`);
                
                // Forward to ADK Bridge
                try {
                    await axios.post(WEBHOOK_URL, {
                        event: "message",
                        data: {
                            from: jid,
                            body: body,
                            pushName: msg.pushName || (isMe ? "Self" : "Unknown")
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
    console.log(`[*] Self-interaction ENABLED`);
});
