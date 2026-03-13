import asyncio
import json
import os
import time

import aiohttp

EVENTSUB_WS_URL = "wss://eventsub.wss.twitch.tv/ws"
TWITCH_API_BASE = "https://api.twitch.tv/helix"
COOLDOWN_SECONDS = 10


class TwitchBot:
    def __init__(self):
        self.client_id = os.environ["TWITCH_CLIENT_ID"]
        self.access_token = os.environ["TWITCH_BOT_ACCESS_TOKEN"]
        self.bot_user_id = os.environ["TWITCH_BOT_USER_ID"]
        self.broadcaster_user_id = os.environ["TWITCH_BROADCASTER_USER_ID"]
        self.channel_name = os.environ["TWITCH_CHANNEL_NAME"]
        self._cooldowns: dict[str, float] = {}

    def _is_on_cooldown(self, command: str) -> bool:
        last = self._cooldowns.get(command, 0)
        return time.monotonic() - last < COOLDOWN_SECONDS

    def _set_cooldown(self, command: str) -> None:
        self._cooldowns[command] = time.monotonic()

    async def send_message(self, session: aiohttp.ClientSession, text: str) -> None:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
        }
        body = {
            "broadcaster_id": self.broadcaster_user_id,
            "sender_id": self.bot_user_id,
            "message": text,
        }
        async with session.post(
            f"{TWITCH_API_BASE}/chat/messages", headers=headers, json=body
        ) as resp:
            if resp.status not in (200, 204):
                err = await resp.text()
                print(f"[ERROR] Failed to send message: {resp.status} {err}")

    async def _subscribe(self, session: aiohttp.ClientSession, session_id: str) -> None:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
        }
        body = {
            "type": "channel.chat.message",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_user_id,
                "user_id": self.bot_user_id,
            },
            "transport": {
                "method": "websocket",
                "session_id": session_id,
            },
        }
        async with session.post(
            f"{TWITCH_API_BASE}/eventsub/subscriptions", headers=headers, json=body
        ) as resp:
            if resp.status == 202:
                print("[INFO] Subscribed to channel.chat.message")
            else:
                err = await resp.text()
                print(f"[ERROR] Subscription failed: {resp.status} {err}")

    async def _handle_notification(
        self, session: aiohttp.ClientSession, event: dict
    ) -> None:
        username = event["chatter_user_login"]
        text = event["message"]["text"]
        print(f"[CHAT] {username}: {text}")

        cmd = text.strip().lower()

        if cmd == "!ping":
            if self._is_on_cooldown("ping"):
                return
            self._set_cooldown("ping")
            await self.send_message(session, "pong!")

    async def run(self) -> None:
        ws_url = EVENTSUB_WS_URL
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.ws_connect(ws_url) as ws:
                        print(f"[INFO] Connected to {ws_url}")
                        ws_url = EVENTSUB_WS_URL  # reset to default after reconnect

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                msg_type = data["metadata"]["message_type"]

                                if msg_type == "session_welcome":
                                    session_id = data["payload"]["session"]["id"]
                                    print(f"[INFO] Session ID: {session_id}")
                                    await self._subscribe(session, session_id)

                                elif msg_type == "session_keepalive":
                                    pass  # connection healthy

                                elif msg_type == "notification":
                                    event = data["payload"]["event"]
                                    await self._handle_notification(session, event)

                                elif msg_type == "session_reconnect":
                                    ws_url = data["payload"]["session"]["reconnect_url"]
                                    print(f"[INFO] Server requested reconnect to {ws_url}")
                                    break  # reconnect on next loop iteration

                                elif msg_type == "revocation":
                                    print(f"[WARN] Subscription revoked: {data}")

                            elif msg.type in (
                                aiohttp.WSMsgType.CLOSED,
                                aiohttp.WSMsgType.ERROR,
                            ):
                                print(f"[WARN] WebSocket closed or errored: {msg}")
                                break

                except Exception as e:
                    print(f"[ERROR] Connection error: {e}. Retrying in 5s...")
                    await asyncio.sleep(5)
