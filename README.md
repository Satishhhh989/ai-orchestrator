# AI Workflow Orchestrator

A hyper-autonomous AI system agent for absolute control over a Windows environment. Multi-account LLM failover, interactive remote desktop streaming via Telegram, autonomous task scheduling, and unrestricted script execution — all from your phone.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Step 1 — Install Python](#step-1--install-python)
- [Step 2 — Clone the Repository](#step-2--clone-the-repository)
- [Step 3 — Create a Telegram Bot & Get Your Token](#step-3--create-a-telegram-bot--get-your-token)
- [Step 4 — Get Your Telegram User ID](#step-4--get-your-telegram-user-id)
- [Step 5 — Get OpenRouter API Keys](#step-5--get-openrouter-api-keys)
- [Step 6 — Configure Environment Variables](#step-6--configure-environment-variables)
- [Step 7 — Install Python Dependencies](#step-7--install-python-dependencies)
- [Step 8 — Run the Application](#step-8--run-the-application)
- [Optional — Auto-Start on Boot](#optional--auto-start-on-boot)
- [Telegram Commands](#telegram-commands)
- [Natural Language Examples](#natural-language-examples)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Multi-Provider AI Core** | 3-account OpenRouter failover with automatic retry and fallback for maximum uptime |
| **Telegram Remote Desktop** | Live screenshot streaming with mouse movement, click, and navigation controls |
| **Remote Keyboard** | Type, copy, paste, and press keys on your PC remotely via Telegram |
| **Cron-AI Scheduler** | Autonomous background task scheduling via APScheduler — set and forget |
| **Unrestricted Scraping** | Headless browsing with Playwright and BeautifulSoup for any website |
| **Transfer Outbox** | Auto-upload of generated files (screenshots, CSVs, PDFs) to Telegram |
| **System Agent** | Root-level PowerShell and Python execution with full GUI automation |
| **Workflow Engine** | Multi-step workflow state machine with pause, resume, and step tracking |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     TELEGRAM (Phone)                     │
│              Your messages / commands / clicks           │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT MODULE                    │
│   Receives commands, sends replies, streams screenshots  │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────────────┐
│    AI    │ │Executor │ │Workflow│ │  Cron/Task   │
│Controller│ │(Scripts)│ │ Engine │ │  Scheduler   │
└──────────┘ └─────────┘ └────────┘ └──────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────────────────────────────────────────────────────┐
│                   WINDOWS OS (Your PC)                   │
│     PowerShell, Python, GUI Automation, File System      │
└──────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- **Operating System**: Windows 10 or Windows 11
- **Internet Connection**: Required for Telegram and OpenRouter API
- **Python**: Version 3.10 or newer
- **Git**: For cloning the repository
- **Telegram Account**: To create a bot and interact with the system

---

## Step 1 — Install Python

If you don't have Python installed, follow these steps:

### 1.1 Download Python

1. Go to the official Python downloads page: **https://www.python.org/downloads/**
2. Click the **"Download Python 3.x.x"** button (get the latest stable version, 3.10+)
3. The installer (`.exe` file) will download to your computer

### 1.2 Run the Installer

1. Open the downloaded `.exe` file
2. ** IMPORTANT**: At the very first screen, check the box that says **"Add python.exe to PATH"** — this is critical
3. Click **"Install Now"** (recommended) or choose "Customize installation" if you want to pick a specific directory
4. Wait for the installation to complete
5. Click **"Close"** when done

### 1.3 Verify Installation

Open **Command Prompt** or **PowerShell** and run:

```powershell
python --version
```

You should see output like `Python 3.12.x`. If you get an error like `'python' is not recognized`, restart your computer and try again — the PATH variable needs a restart to take effect.

Also verify pip (Python's package manager):

```powershell
pip --version
```

You should see something like `pip 24.x from ...`.

---

## Step 2 — Clone the Repository

Open **PowerShell** or **Command Prompt** and run:

```powershell
git clone https://github.com/Satishhhh989/ai-orchestrator.git
cd ai-orchestrator
```

If you don't have Git installed, download it from **https://git-scm.com/downloads** and install it. Alternatively, download the repository as a ZIP from GitHub and extract it.

---

## Step 3 — Create a Telegram Bot & Get Your Token

You need a Telegram Bot Token to connect the orchestrator to Telegram. Here's how to get one:

### 3.1 Open BotFather

1. Open **Telegram** on your phone or desktop
2. Search for **`@BotFather`** in the search bar (it has a blue verified checkmark)
3. Open the chat and click **Start**

### 3.2 Create a New Bot

1. Send the command: `/newbot`
2. BotFather will ask for a **display name** — type any name you want (e.g., `My AI Assistant`)
3. BotFather will then ask for a **username** — this must end in `bot` (e.g., `my_ai_assistant_bot`)
4. If the username is available, BotFather will respond with a message containing your **Bot Token**

### 3.3 Copy the Token

The token looks something like this:

```
7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

**Copy this entire token** — you will need it in Step 6. Do NOT share this token with anyone.

### 3.4 (Optional) Customize Your Bot

You can send these commands to BotFather to customize your bot:

- `/setdescription` — Set a description for your bot
- `/setabouttext` — Set the "About" text
- `/setuserpic` — Set a profile picture for the bot

---

## Step 4 — Get Your Telegram User ID

The bot only responds to YOUR messages. To enforce this, you need your personal Telegram User ID (a numeric ID, not your username).

### Method 1: Using @userinfobot

1. Open Telegram
2. Search for **`@userinfobot`**
3. Click **Start** or send any message
4. The bot will reply with your **User ID** — it's a number like `6577439787`
5. **Copy this number**

### Method 2: Using @RawDataBot

1. Open Telegram
2. Search for **`@RawDataBot`**
3. Click **Start** or send any message
4. Look for the `"id"` field under the `"from"` section in the JSON response
5. **Copy this number**

> **Note**: Your User ID is NOT your Telegram username (like @myname). It's a purely numeric value. Make sure to use the number, not the username.

---

## Step 5 — Get OpenRouter API Keys

The AI features are powered by **OpenRouter**, which gives you access to multiple AI models (including free-tier ones). The orchestrator supports up to **3 API keys** for failover — if one key gets rate-limited, it automatically switches to the next.

### 5.1 Create an OpenRouter Account

1. Go to **https://openrouter.ai/**
2. Click **"Sign In"** (top-right corner)
3. Sign up using **Google**, **GitHub**, or **Email**
4. Once logged in, you'll land on the OpenRouter dashboard

### 5.2 Generate an API Key

1. Go to **https://openrouter.ai/keys** (or click your profile icon → "Keys" from the dashboard)
2. Click **"Create Key"**
3. Give it a name (e.g., `orchestrator-key-1`)
4. **Copy the generated key immediately** — it looks like: `sk-or-v1-abc123...xyz789`
5. The key is shown only once. If you lose it, you'll need to create a new one

### 5.3 (Recommended) Create Multiple Keys for Failover

For maximum uptime, create **3 separate accounts** on OpenRouter (use different email addresses) and generate one API key from each:

- **Key 1** (Primary) — Used first for every request
- **Key 2** (Secondary) — Falls back to this if Key 1 is rate-limited
- **Key 3** (Tertiary) — Last resort fallback

> **Why 3 keys?** Free-tier models on OpenRouter have rate limits. With 3 accounts rotating, you get roughly 3x the free-tier capacity and near-zero downtime.

### 5.4 Available Free Models

The default models configured for each key slot are:

| Slot | Default Model | Provider |
|---|---|---|
| Key 1 | `openai/gpt-oss-120b:free` | OpenAI |
| Key 2 | `meta-llama/llama-3.3-70b-instruct:free` | Meta |
| Key 3 | `google/gemma-3-27b-it:free` | Google |

You can change these to any model available on OpenRouter. Browse models at **https://openrouter.ai/models** and filter by "Free" to see all free options.

---

## Step 6 — Configure Environment Variables

### 6.1 Create Your `.env` File

In the project root directory (`ai_workflow_orchestrator/`), copy the example file:

```powershell
copy .env.example .env
```

### 6.2 Edit the `.env` File

Open the `.env` file in any text editor (Notepad, VS Code, etc.) and fill in your values:

```env
# ──────────────────────────────────────────────
# AI Workflow Orchestrator — Environment Config
# ──────────────────────────────────────────────

# Telegram Configuration (REQUIRED)
TELEGRAM_TOKEN=your_bot_token_from_botfather
USER_ID=your_numeric_telegram_user_id

# OpenRouter AI Keys (at least 1 required for AI features)
OPENROUTER_API_KEY_1=sk-or-v1-your_primary_key_here
OPENROUTER_MODEL_1=openai/gpt-oss-120b:free

OPENROUTER_API_KEY_2=sk-or-v1-your_secondary_key_here
OPENROUTER_MODEL_2=meta-llama/llama-3.3-70b-instruct:free

OPENROUTER_API_KEY_3=sk-or-v1-your_tertiary_key_here
OPENROUTER_MODEL_3=google/gemma-3-27b-it:free

# Logging and State
LOG_LEVEL=INFO
STATE_FILE=data/state.json
ENABLE_GUI_AUTOMATION=false
```

### What Each Variable Does

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | **Yes** | The bot token from BotFather (Step 3) |
| `USER_ID` | **Yes** | Your numeric Telegram user ID (Step 4) |
| `OPENROUTER_API_KEY_1` | **Yes*** | Primary OpenRouter API key (Step 5) |
| `OPENROUTER_MODEL_1` | No | AI model for key 1 (defaults to `openai/gpt-oss-120b:free`) |
| `OPENROUTER_API_KEY_2` | No | Secondary failover API key |
| `OPENROUTER_MODEL_2` | No | AI model for key 2 (defaults to `meta-llama/llama-3.3-70b-instruct:free`) |
| `OPENROUTER_API_KEY_3` | No | Tertiary failover API key |
| `OPENROUTER_MODEL_3` | No | AI model for key 3 (defaults to `google/gemma-3-27b-it:free`) |
| `LOG_LEVEL` | No | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`) |
| `STATE_FILE` | No | Path to persist workflow state (default: `data/state.json`) |
| `ENABLE_GUI_AUTOMATION` | No | Set to `true` to enable GUI automation features (default: `false`) |

> **\*** At least one OpenRouter API key is required for AI-powered natural language processing. Without it, only direct Telegram commands (like `/desktop`, `/type`) will work.

---

## Step 7 — Install Python Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

This installs all required packages:

| Package | Purpose |
|---|---|
| `python-telegram-bot` | Telegram bot framework (v21+) |
| `psutil` | System monitoring (CPU, RAM, processes) |
| `pyautogui` | GUI automation (mouse, keyboard control) |
| `pyperclip` | Clipboard operations (copy/paste) |
| `mss` | Fast screen capture for remote desktop |
| `requests` | HTTP client for API calls |
| `python-dotenv` | Load `.env` environment variables |
| `APScheduler` | Background task scheduling (cron jobs) |
| `playwright` | Headless browser for web scraping |
| `beautifulsoup4` | HTML parsing for scraped pages |
| `Pillow` | Image processing for screenshots |

### Install Playwright Browsers

After pip install, run this to download the Chromium browser for web scraping:

```powershell
python -m playwright install chromium
```

---

## Step 8 — Run the Application

### Start Normally (Foreground)

```powershell
python main.py
```

You should see:

```
==================================================
  AI Workflow Orchestrator Starting...
==================================================

==================================================
  Telegram Bot is LIVE
  Listening for commands...
  Authorized user: <your_user_id>
  Started at: 2026-04-01 12:00:00
==================================================
```

Now open Telegram and send `/start` to your bot. If it replies "System is online", everything is working.

### Stop the Application

Press `Ctrl + C` in the terminal where it's running.

---

## Optional — Auto-Start on Boot

You can configure the orchestrator to start automatically when you log into Windows. There are two methods:

### Method A: Startup Shortcut (No Admin Required)

This creates a shortcut in your Windows Startup folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_startup_user.ps1
```

### Method B: Scheduled Task (Admin Required)

This registers a Windows Scheduled Task (more reliable, runs even without interaction):

```powershell
powershell -ExecutionPolicy Bypass -File .\install_startup_task.ps1
```

> Both methods use `run_background.vbs` to launch the bot silently (no visible terminal window). The bot runs as a background process.

### Remove Auto-Start

**Method A** — Delete the shortcut from:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AI_Workflow_Orchestrator.lnk
```

**Method B** — Remove the scheduled task:
```powershell
Unregister-ScheduledTask -TaskName "AI_Workflow_Orchestrator" -Confirm:$false
```

---

## Telegram Commands

| Command | Description |
|---|---|
| `/start` | Confirm the system is online |
| `/status` | Check workflow engine status (step, running, paused) |
| `/desktop` | Launch interactive remote desktop with navigation controls |
| `/type <text>` | Type text on the remote machine's keyboard |
| `/enter` | Press the Enter key remotely |
| `/copy` | Copy currently selected text to clipboard and send it to you |
| `/paste <text>` | Paste text on the remote machine (optionally set clipboard first) |
| `/jobs` | List all active scheduled background tasks |
| `/logs` | Download the execution log file |
| `/startflow` | Start a predefined multi-step workflow |
| `/pause` | Pause the active workflow |
| `/resume` | Resume a paused workflow |
| `/workflows` | List all available workflows |
| `/help` | Show all available commands |

---

## Natural Language Examples

Any non-command text you send is processed by the AI as a natural language instruction. The AI interprets your intent and executes the appropriate scripts:

| What You Type | What Happens |
|---|---|
| *"Open Chrome and go to GitHub"* | AI finds Chrome on your system and opens GitHub |
| *"Take a screenshot"* | Captures the screen and sends it to you |
| *"Every 30 minutes, scrape HackerNews and send me a summary"* | Schedules a recurring background task |
| *"Find all PDFs on my Desktop and upload them here"* | Searches files and sends them via transfer outbox |
| *"Monitor my RAM; if it hits 90%, kill Chrome"* | Schedules a monitoring task with conditional logic |
| *"What's the current CPU usage?"* | Runs a system info script and reports back |
| *"Download the latest Python installer"* | Opens browser and downloads file |
| *"Create a text file on Desktop with today's date"* | Generates and saves a file via PowerShell |

---

## Project Structure

```
ai_workflow_orchestrator/
├── agent/
│   ├── __init__.py
│   ├── ai_controller.py          # Multi-provider AI brain with 3-account failover
│   ├── executor.py                # System-level script execution engine
│   └── scheduler.py               # APScheduler-based cron job manager
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py            # Telegram interface, remote desktop, all commands
├── config/
│   └── settings.py                # Dataclass-based configuration from environment
├── listener/
│   ├── __init__.py
│   └── notification_listener.py   # File-based task completion detection
├── memory/
│   ├── __init__.py
│   └── state_manager.py           # Persistent state and workflow logging
├── orchestrator/
│   └── workflow_engine.py          # Multi-step workflow state machine
├── transfer/                       # Auto-sync outbox — files here upload to Telegram
├── logs/                           # Runtime logs (auto-created)
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── run_background.vbs              # Silent background launcher (Windows)
├── install_startup_task.ps1        # Register as Windows Scheduled Task
└── install_startup_user.ps1        # Register via Startup folder shortcut
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **AI Backend** | OpenRouter API — OpenAI, Meta Llama 3.3, Google Gemma 3 (free-tier) |
| **Bot Interface** | python-telegram-bot v21+ (async) |
| **GUI Automation** | pyautogui + mss + Pillow + pyperclip |
| **Task Scheduling** | APScheduler (interval-based cron) |
| **Web Scraping** | Playwright (headless Chromium) + BeautifulSoup4 |
| **Configuration** | python-dotenv + dataclass settings |
| **Logging** | Python stdlib logging (file + console) |

---

## Troubleshooting

### "python is not recognized as a command"

- You didn't check **"Add python.exe to PATH"** during installation
- Fix: Reinstall Python and check the PATH box, or manually add Python to your system PATH
- After fixing, **restart your terminal/PC**

### "TELEGRAM_TOKEN environment variable is required"

- Your `.env` file is missing or the `TELEGRAM_TOKEN` value is empty
- Make sure you created the `.env` file (not just `.env.example`) and pasted your bot token

### "USER_ID environment variable is required"

- Your `USER_ID` in `.env` is missing or set to `0`
- Get your numeric User ID from `@userinfobot` on Telegram (see Step 4)

### Bot doesn't respond to messages

1. Make sure the `USER_ID` in `.env` matches YOUR Telegram ID exactly
2. Make sure you started a chat with the bot first (send `/start`)
3. Check the terminal output for error messages
4. The bot silently ignores messages from unauthorized users

### "No OpenRouter API keys found"

- At least one `OPENROUTER_API_KEY_*` must be set in `.env`
- Without API keys, only direct commands (`/desktop`, `/type`, etc.) work — natural language processing is disabled

### Rate limiting / "All AI cores are offline"

- Free-tier OpenRouter models have rate limits
- Solution: Create 2-3 separate OpenRouter accounts and set all 3 API keys for automatic failover

### Remote Desktop `/desktop` shows error

- Make sure `mss` and `pyautogui` are installed: `pip install mss pyautogui`
- The machine must have an active desktop session (not locked/RDP disconnected)
- If running as a service, it may not have access to the desktop — use the startup shortcut method instead

### Playwright / web scraping errors

- Run `python -m playwright install chromium` to install the browser
- If behind a proxy, configure Playwright proxy settings

---

## Security

> ** WARNING**: This system executes AI-generated code with full system access. It has root-level privileges on your Windows machine.

- **Only the configured `USER_ID` can interact with the bot** — all other users are silently blocked and logged
- **Use only with a private bot** — do not add the bot to public groups
- **Never share your `.env` file** — it contains your API keys and bot token
- **The `.env` file is gitignored** — it will not be pushed to GitHub
- **Review the AI's actions** — while the system is autonomous, monitor the logs regularly

---

## License

This project is for personal use.
