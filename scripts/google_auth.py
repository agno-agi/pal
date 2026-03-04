#!/usr/bin/env python3
#
# Generate token.json for Gmail + Calendar OAuth.
# Run on the HOST (not inside Docker) — opens a browser for Google consent.
#
# Usage:
#     python scripts/google_auth.py
#

from os import getenv
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar",
]

TOKEN_PATH = Path(__file__).parent.parent / "token.json"

client_config = {
    "installed": {
        "client_id": getenv("GOOGLE_CLIENT_ID"),
        "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
        "project_id": getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost:8080/"],
    }
}

if not client_config["installed"]["client_id"]:
    raise SystemExit("GOOGLE_CLIENT_ID not set. Export Google env vars first.")

print(f"Requesting scopes: {SCOPES}")
print("Opening browser for Google consent...")

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
# prompt='consent' forces Google to return a refresh_token even on re-auth
creds = flow.run_local_server(port=8080, bind_addr="localhost", prompt="consent")

TOKEN_PATH.write_text(creds.to_json())
print(f"\nToken saved to: {TOKEN_PATH}")
print("Gmail + Calendar scopes authorized.")
