"""
One-off script to generate a Twitch user access token + refresh token
for the bot account using the Authorization Code flow.

Usage:
    1. In a separate terminal on your local machine, run:
           ssh -L 3000:localhost:3000 dillon@bot-dev
       (keeps the tunnel open — leave it running)
    2. Then run this script on the Debian server:
           python3 scripts/get_twitch_token.py

Requires TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in your .env file.
"""

import http.server
import json
import os
import sys
import urllib.parse
import urllib.request

# Parse .env file manually — no third-party deps needed
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000"
SCOPES = "user:read:chat user:write:chat user:bot"

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set in .env")
    sys.exit(1)

params = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPES,
})
auth_url = f"https://id.twitch.tv/oauth2/authorize?{params}"

# Shared state to pass the code from the HTTP handler back to main
_received_code = []


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        if "code" in query:
            _received_code.append(query["code"][0])
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this tab.</p>")
        else:
            error = query.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h1>Error: {error}</h1>".encode())

    def log_message(self, format, *args):
        pass  # suppress default request logging


print("\n=== Twitch Token Generator ===")
print("\nPREREQUISITE: Make sure you have an SSH tunnel open in another terminal:")
print("  ssh -L 3000:localhost:3000 dillon@bot-dev\n")
print("Open this URL in your browser, logged in as carprbot:\n")
print(auth_url)
print("\nWaiting for authorization callback on port 3000...")

server = http.server.HTTPServer(("0.0.0.0", 3000), CallbackHandler)
server.handle_request()  # handles exactly one request then exits

if not _received_code:
    print("\nERROR: No authorization code received.")
    sys.exit(1)

code = _received_code[0]
print("Got authorization code. Exchanging for tokens...")

token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
}).encode()

req = urllib.request.Request(
    "https://id.twitch.tv/oauth2/token",
    data=token_data,
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        token_resp = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"\nERROR: Token exchange failed: {e.code} {e.read().decode()}")
    sys.exit(1)

access_token = token_resp.get("access_token")
refresh_token = token_resp.get("refresh_token")
expires_in = token_resp.get("expires_in")
scopes = token_resp.get("scope", [])

print("\n=== SUCCESS ===")
print(f"Scopes granted: {' '.join(scopes)}")
print(f"Expires in:     {expires_in} seconds (~{expires_in // 3600}h)")
print(f"\nAdd these to your .env:\n")
print(f"TWITCH_BOT_ACCESS_TOKEN={access_token}")
print(f"TWITCH_BOT_REFRESH_TOKEN={refresh_token}")
