# AI Workflow Orchestrator

A hyper-autonomous AI system agent for absolute control over a Windows environment. Multi-account LLM failover, interactive remote desktop streaming via Telegram, autonomous task scheduling, and unrestricted script execution.

## Capabilities

| Feature | Description |
|---|---|
| **Multi-Provider AI Core** | 3-account OpenRouter failover for maximum uptime |
| **Telegram Remote Desktop** | Interactive screenshot streaming with mouse movement and click controls |
| **Cron-AI Scheduler** | Autonomous background task scheduling via APScheduler |
| **Unrestricted Scraping** | Headless browsing with Playwright and BeautifulSoup |
| **Transfer Outbox** | Auto-upload of generated files to Telegram |
| **System Agent** | Root-level PowerShell and Python execution with GUI automation |
| **Remote Keyboard** | Type, copy, paste, and press keys remotely |

## Project Structure

```
ai_workflow_orchestrator/
├── agent/
│   ├── ai_controller.py       # Multi-provider AI brain with failover
│   ├── executor.py             # GUI automation execution engine
│   └── scheduler.py            # Background task scheduler
├── bot/
│   └── telegram_bot.py         # Telegram interface and remote desktop
├── orchestrator/
│   └── workflow_engine.py      # Multi-step workflow state machine
├── memory/
│   └── state_manager.py        # Persistent state and workflow logging
├── listener/
│   └── notification_listener.py # File-based task completion detection
├── config/
├── transfer/                    # Auto-sync outbox to Telegram
├── main.py                      # Entry point
├── requirements.txt
├── run_background.vbs           # Background launcher (Windows)
├── install_startup_task.ps1     # System startup registration
└── install_startup_user.ps1     # User startup registration
```

## Setup

### 1. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```
TELEGRAM_TOKEN=your_bot_token_from_botfather
USER_ID=your_telegram_user_id
OPENROUTER_API_KEY_1=your_primary_key
OPENROUTER_API_KEY_2=your_secondary_key
OPENROUTER_API_KEY_3=your_tertiary_key
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Run

```powershell
python main.py
```

For background execution on Windows:

```powershell
.\install_startup_user.ps1
```

## Telegram Commands

| Command | Action |
|---|---|
| `/start` | Confirm system is online |
| `/status` | Check workflow engine status |
| `/desktop` | Launch interactive remote desktop |
| `/type <text>` | Type text on remote machine |
| `/enter` | Press Enter key remotely |
| `/copy` | Copy selected text to clipboard |
| `/paste <text>` | Paste text remotely |
| `/jobs` | List active scheduled tasks |
| `/logs` | Download execution logs |
| `/startflow` | Start a workflow |
| `/pause` | Pause active workflow |
| `/resume` | Resume paused workflow |
| `/workflows` | List available workflows |
| `/help` | Show all commands |

Any non-command text is processed by the AI as a natural language instruction. Examples:

- *"Open Chrome and go to GitHub"*
- *"Every 30 minutes, scrape HackerNews and send me a summary"*
- *"Find all PDFs on my Desktop and upload them here"*
- *"Monitor my RAM; if it hits 90%, kill Chrome"*

## Tech Stack

- **AI**: OpenRouter (OpenAI, Meta Llama 3.3, Google Gemma 3)
- **GUI**: pyautogui + mss + Pillow
- **Scheduling**: APScheduler
- **Web**: Playwright + BeautifulSoup4
- **Interface**: python-telegram-bot v21+

## Security

This system executes LLM-generated code with full system access. Only the configured `USER_ID` can interact with the bot. All other users are silently blocked. Use only with a private Telegram bot.
