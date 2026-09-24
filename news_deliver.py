"""Optional WhatsApp delivery via Meta's free Cloud API test number.
Setup is in the README. Off unless you pass --send-whatsapp."""

import os

import requests

GRAPH_URL = "https://graph.facebook.com/v21.0/{phone_id}/messages"


def send_whatsapp(text, token=None, phone_number_id=None, to=None):
    """Send the brief to one WhatsApp number. Returns (ok, detail)."""
    token = token or os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = phone_number_id or os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    to = to or os.environ.get("WHATSAPP_TO")
    missing = [name for name, val in [("WHATSAPP_TOKEN", token), ("WHATSAPP_PHONE_NUMBER_ID", phone_number_id), ("WHATSAPP_TO", to)] if not val]
    if missing:
        return False, f"missing env vars: {', '.join(missing)}"
    # WhatsApp text messages cap at 4096 chars; split if the brief runs long.
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or [text]
    for chunk in chunks:
        response = requests.post(
            GRAPH_URL.format(phone_id=phone_number_id),
            headers={"Authorization": f"Bearer {token}"},
            json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": chunk}},
            timeout=30,
        )
        if response.status_code != 200:
            return False, f"Meta API {response.status_code}: {response.text[:200]}"
    return True, f"sent {len(chunks)} message(s) to {to}"
