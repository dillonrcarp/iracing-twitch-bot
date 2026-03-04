# 🏎️ iRacing Live Stats Twitch Bot - Vibe PM PRD

## 1. Project Overview
**What we are building:** A Twitch chatbot that interacts with the iRacing Data API (OAuth2) and the local iRacing Telemetry SDK to provide live and historical streamer stats to viewers in Twitch chat. 
**Who it's for:** Viewers of the Twitch stream who want to act as a "virtual pit crew" by querying live race data.
**How it works:** The bot listens to Twitch chat for specific command prefixes (e.g., `!`). Upon detecting a command, it fetches the corresponding data either from the iRacing Web API (for historical/session data) or a live telemetry stream, and posts the formatted response back to the chat.

## 2. Architecture & Tech Stack
Because the bot will be hosted on a **local Debian Linux machine** via Docker, but the iRacing simulator only runs on **Windows**, the application must be split into a localized telemetry forwarder and a containerized central bot. Keeping the tech stack simple reduces the likelihood of the AI introducing breaking bugs [1].

*   **Twitch Bot & Web API Service (Debian/Docker Host):** 
    *   **Language:** Node.js (using `tmi.js` or EventSub) OR Python (using `iracingdataapi` and Twitch WebSockets).
    *   **Containerization:** Docker & `docker-compose.yml` to bundle the bot, its dependencies, and environment variables.
*   **Live Telemetry Forwarder (Windows Host):**
    *   **Language:** Python (using a library like `pyirsdk`) or C# (using the .NET Telemetry SDK).
    *   **Function:** Runs locally on the streamer's Windows PC, reads the iRacing memory-mapped file at 60Hz, and forwards requested telemetry variables (Speed, Gear, Fuel, RPM) over the local network (via WebSockets or UDP) to the Debian Docker container.
*   **Security & Data:** All Twitch tokens and iRacing OAuth2 tokens must be stored in a `.env` file and excluded from version control.

## 3. Requirements & Command Logic
The bot will support two categories of commands. All commands must implement a **10-second cooldown timer** to prevent spam and avoid hitting API rate limits.

**Web API Commands (Pulled from iRacing servers via Debian host):**
*   `!irating` / `!safety`: Current iRating, Safety Rating, and License Class.
*   `!lastrace` / `!recent`: Results of the streamer's most recent sessions.
*   `!sof`: Average iRating of the current session split.
*   `!car` / `!track`: Current vehicle and circuit names/layouts.
*   `!record`: Streamer's all-time fastest lap for the current car/track combo.

**Live Telemetry Commands (Pulled from Windows host, broadcast to Debian host):**
*   `!weather`: Live track conditions (`AirTemp`, `TrackTemp`, `WindVel`).
*   `!inc`: Streamer's live incident count (`PlayerCarIncmidSession`).
*   `!ints`: Gap intervals to the cars directly ahead and behind (`CarIdxF2Time`).
*   `!sessionbest`: Streamer's fastest lap set in the *current* session.

## 4. Milestones (Step-by-Step Build Plan)
*AI Agent Instruction: Implement the simplest next step that can be tested. Do not proceed to the next milestone until the current one is tested and confirmed working [2].*

*   **Milestone 1: Scaffolding & Security**
    *   Initialize the project repository and set up version control.
    *   Create a `.env` template for Twitch and iRacing credentials.
    *   Write the `docker-compose.yml` and `Dockerfile` for the Debian environment.
*   **Milestone 2: Twitch Chat Integration**
    *   Authenticate the bot with Twitch using OAuth2.
    *   Connect to the specified Twitch channel and successfully log incoming chat messages to the console.
    *   Implement a simple "ping/pong" command to verify the bot can post messages back to chat. Include the 10-second cooldown logic.
*   **Milestone 3: iRacing Web API Integration**
    *   Implement the OAuth2 authentication flow for the new iRacing Data API.
    *   Map the `!irating` and `!track` commands to fetch and return actual data.
*   **Milestone 4: Telemetry Forwarder (Windows to Debian Bridge)**
    *   Create a lightweight script to run on the Windows sim PC that reads the local memory stream.
    *   Establish a local network connection (e.g., WebSocket) to send this live data to the Dockerized bot on the Debian machine.
    *   Implement the `!inc` and `!speed` commands to verify the data bridge is working.
*   **Milestone 5: Command Expansion & Production Polish**
    *   Flesh out the remaining commands (`!weather`, `!ints`, `!lastrace`, etc.).
    *   Run a cleaning pass to fix linter errors, remove redundancies, and optimize performance.

## 5. Global AI Project Rules
*AI Agent, please adhere to the following rules for this workspace:*
1.  **Tell me your plan first; don't code.** Explain what you intend to do and ask for my confirmation before creating or modifying files [3, 4].
2.  **Give me options.** If a feature is complex, give me a few options starting with the simplest approach first [5].
3.  **No hardcoded secrets.** Never write API keys or tokens into the code. Always read from environment variables.
4.  **Test ruthlessly.** After completing a step, wait for me to test the application locally via `localhost` before continuing [6].
