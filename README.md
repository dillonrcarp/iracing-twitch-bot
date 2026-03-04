# 🏎️ iracing-twitch-bot

A real-time Twitch chatbot designed for iRacing streamers that turns viewers into a virtual pit crew. By bridging the modern iRacing Web API (OAuth2) with a local Telemetry SDK forwarder, this bot allows viewers to engage with the stream by querying live, up-to-the-millisecond race data and historical profile stats directly in the Twitch chat [3, 4].

## 1. Project Overview
* **Goal:** Provide Twitch viewers with real-time sim-racing data (e.g., live speed, tire temps, intervals) and historical career data (e.g., iRating, recent race results) via chat commands.
* **Tech Philosophy:** Keep the tech stack simple to minimize the chance of AI-introduced bugs during development [5]. We will utilize a split architecture to accommodate the Windows-only iRacing simulator and our preferred Debian/Docker hosting environment.
* **AI Vibe Coding Ready:** This repository is structured specifically for AI-assisted development (e.g., Cursor, Windsurf, Claude Code). Please read the "Vibe Coding Rules" section before writing code [6].

## 2. Architecture & Tech Stack

Because the bot will be hosted on a **local Debian Linux machine** via Docker, but the iRacing simulator only runs on **Windows**, the application is split into two components:

1. **Twitch Bot & Web API Service (Debian/Docker Host)**
   * **Language:** Node.js or Python.
   * **Twitch Integration:** Modern Twitch EventSub WebSockets (listening to `channel.chat.message` events) [7].
   * **iRacing Web API:** Utilizes OAuth 2.0 authentication (legacy password login is deprecated) to pull profile and session data [8, 9].
   * **Containerization:** Bundled using `Dockerfile` and `docker-compose.yml` for isolated deployment [10].
2. **Live Telemetry Forwarder (Windows Host)**
   * **Language:** Python (using a local telemetry library).
   * **Function:** Runs locally on the streamer's Windows PC, reads the iRacing memory-mapped file at 60Hz, and forwards requested telemetry variables over the local network to the Debian Docker container [11].

## 3. Requirements & Command Logic
All commands must implement a **10-second cooldown timer** to prevent chat spam and avoid hitting Twitch or iRacing API rate limits [12, 13].

**Web API Commands (Historical & Session Data):**
* `!irating` / `!safety`: Fetches the streamer's current iRating, Safety Rating, and License Class.
* `!lastrace` / `!recent`: Returns the results of the streamer's most recent sessions.
* `!sof`: Calculates the average iRating of the current session split.
* `!car` / `!track`: Returns the current vehicle and circuit names/layouts.
* `!record`: Pulls the streamer's all-time fastest lap for the current car/track combo.

**Live Telemetry Commands (Real-Time In-Sim Data):**
* `!speed` / `!gear` / `!rpm`: Real-time vehicle dashboard metrics.
* `!weather`: Live track conditions (Air Temp, Track Temp, Wind Speed).
* `!inc`: Streamer's live incident count (`PlayerCarIncmidSession`).
* `!ints`: Gap intervals to the cars directly ahead and behind.
* `!sessionbest`: Streamer's fastest lap set in the *current* live session.

## 4. Setup & Security Guidelines
* **No Hardcoded Secrets:** Twitch Client IDs, Client Secrets, and iRacing OAuth tokens must NEVER be hardcoded [14]. 
* **Environment Variables:** All secrets must be stored in a `.env` file at the root directory and loaded securely into the application [15]. 
* **Version Control:** Ensure `.env` is explicitly included in the `.gitignore` and `.dockerignore` files to prevent accidental exposure [14, 15].

## 5. Development Milestones
*AI Agent: Implement the simplest next step that can be tested. Do not proceed to the next milestone until the current one is tested and confirmed working [16].*

* **Milestone 1: Scaffolding & Security**
  * Initialize the project repository and set up version control.
  * Create a `.env` template for Twitch and iRacing credentials.
  * Write the `docker-compose.yml` and `Dockerfile` for the Debian environment [10, 17].
* **Milestone 2: Twitch Chat Integration**
  * Authenticate the bot with Twitch using OAuth2 [18].
  * Connect to EventSub WebSockets and successfully log incoming chat messages to the console [7].
  * Implement a simple "ping/pong" command to verify the bot can post messages back to chat, including the 10-second cooldown logic [12].
* **Milestone 3: iRacing Web API Integration**
  * Implement the OAuth2 authentication flow for the iRacing Data API [9].
  * Map the `!irating` and `!track` commands to fetch and return actual data.
* **Milestone 4: Telemetry Forwarder (Windows to Debian Bridge)**
  * Create a lightweight Python script for the Windows sim PC to read the local memory stream [3].
  * Establish a local network connection to forward live data to the Dockerized bot on the Debian machine.
  * Implement the `!inc` and `!speed` commands to verify the data bridge is working.
* **Milestone 5: Command Expansion & Polish**
  * Flesh out the remaining commands (`!weather`, `!ints`, `!lastrace`, etc.).
  * Run a cleaning pass to fix linter errors, format code, and remove outdated comments [19].

## 6. Global AI Project Rules
*AI Agent, please adhere to the following rules for this workspace:*
1. **Tell me your plan first; don't code.** Explain what you intend to do and ask for my confirmation before creating or modifying files [20].
2. **Give me options.** If a feature is complex, give me a few options starting with the simplest approach first [21].
3. **Keep it simple.** Do the simple thing first. Avoid introducing unnecessary complex tooling or databases [5].
4. **Look for existing solutions.** Do not write duplicate code; check the codebase first [6].
5. **Read the Docs.** Always check the `/docs` folder or `.cursor/rules` for up-to-date syntax regarding Twitch EventSub and iRacing API implementations before writing API calls [22, 23].
