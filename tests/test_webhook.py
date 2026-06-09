import httpx
import sys

def test_webhook(message):
    url = "http://localhost:6000/webhook"
    payload = {
        "event": "message",
        "data": {
            "from": "test_user@s.whatsapp.net",
            "body": message,
            "pushName": "Tester"
        }
    }
    print(f"Sending message: {message}")
    try:
        response = httpx.post(url, json=payload, timeout=30)
        print(f"Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Hi"
    test_webhook(msg)
