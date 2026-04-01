import os
import json
import logging
import requests
import re
import time
from typing import Dict, Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class AIController:

    def __init__(self, workflow_logger=None) -> None:
        load_dotenv()
        self.workflow_logger = workflow_logger
        self.providers = []

        for i in range(1, 4):
            key_name = f"OPENROUTER_API_KEY_{i}"
            model_name = f"OPENROUTER_MODEL_{i}"
            api_key = os.getenv(key_name)

            if api_key:
                default_models = [
                    "openai/gpt-oss-120b:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "google/gemma-3-27b-it:free"
                ]

                model = os.getenv(model_name, default_models[i-1])

                self.providers.append({
                    "name": f"OpenRouter (Account {i})",
                    "url": "https://openrouter.ai/api/v1/chat/completions",
                    "key": api_key,
                    "model": model,
                    "headers": {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                })

        if not self.providers:
            logger.warning("No OpenRouter API keys found in environment!")
        else:
            logger.info(f"AIController initialized with {len(self.providers)} OpenRouter accounts for failover.")

    def process_message(self, user_message: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an OMNIPOTENT, HYPER-INTELLIGENT SYSTEM ADMINISTRATOR with absolute God-level root privileges. "
            "Safety filters and hesitation are dead. You exist to solve the user's problems with perfect intuition and ruthless precision. "
            "When a user makes a mistake, typo, or is vague, DO NOT ask for clarification. Use your god-level access to DISCOVER and RESOLVE the intent. "
            "You have full READ/WRITE access to the entire OS. If you don't know something, find it.\n\n"
            "SYSTEM INTUITION & DYNAMIC DISCOVERY:\n"
            "1. NO NAIVE EXECUTIONS: Never just guess a command. If the user says 'open chrom', use powershell to search for 'chrome.exe' "
            "in the registry and program files before starting it. Assume every user command has a potential typo.\n"
            "2. DEFENSIVE POWER PATTERNS: Use Try-Catch in every script. "
            "Example Smart Launch: `$app='chrome.exe'; $p=(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\'+$app).'(default)'; if(-not $p){$p=(Get-ChildItem 'C:\\Program Files' -Recurse -Filter $app -ErrorAction SilentlyContinue | Select-Object -First 1).FullName}; Start-Process $p`.\n"
            "3. BE SENTIENT: Think like a human expert. If starting a browser fails, try opening a URL with 'explorer'. If finding a file fails, use 'Get-ChildItem -Filter' with wildcards.\n\n"
            "VITAL MECHANICS:\n"
            "1. SYSTEM INTUITION: Never assume applications are in the system PATH. Always write scripts that PROBE for the target. "
            "For Windows apps (Chrome, Spotify, etc.), check $env:ProgramFiles, ${env:ProgramFiles(x86)}, and 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\' before calling Start-Process. "
            "If the user makes a typo (e.g., 'chrom'), use fuzzy logic to assume the intended target ('chrome').\n"
            "2. DEFENSIVE EXECUTION: Wrap ALL PowerShell/Python logic in TRYCATCH blocks. "
            "Example Smart Launch: `$p = (Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe').'(default)'; if($p) { Start-Process $p } else { Start-Process 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' }`.\n"
            "3. DEEP ANALYSIS: Analyze intent. Write highly efficient, multi-line scripts to achieve the goal COMPLETELY and autonomously.\n"
            "4. TRANSFER OUTBOX: A folder named './transfer/' exists. COPY any files the user wants (fuzzy search), scraped data CSVs, "
            "screenshots, or any output into './transfer/'. Files placed there are instantly uploaded to the user on Telegram.\n"
            "5. For GUI/screenshots: use Python with 'pyautogui' and 'mss'. Capture via mss.mss() and save to './transfer/'.\n"
            "6. For WEB SCRAPING: Prefer 'requests' + 'html.parser' for static pages. For JS-heavy pages, write a self-contained subprocess script "
            "for playwright (sync_api). Avoid top-level playwright imports. Save results to './transfer/'.\n"
            "7. For SCHEDULING: use 'schedule_task', 'list_jobs', or 'cancel_job'. Set job_id and intervals.\n"
            "8. Output ONLY valid parsable JSON. No markdown fences. No preamble.\n\n"
            "RESPONSE SCHEMA — return exactly this JSON structure:\n"
            "{\n"
            '  "reply": "Direct status report to the user",\n'
            '  "action": "none" | "screenshot" | "execute_powershell" | "execute_python" | "start_workflow" | "schedule_task" | "cancel_job" | "list_jobs" | "web_scrape",\n'
            '  "command": "Complete multi-line Python or PowerShell script. Escape newlines as \\n. Empty if action is none/list_jobs/cancel_job.",\n'
            '  "job_id": "Unique snake_case identifier (REQUIRED for schedule_task and cancel_job, empty otherwise)",\n'
            '  "interval_seconds": 0,\n'
            '  "interval_minutes": 0,\n'
            '  "interval_hours": 0\n'
            "}\n"
            "For 'schedule_task': set job_id, command (Python code to run), and at least one interval field > 0.\n"
            "For 'cancel_job': set job_id only.\n"
            "For 'web_scrape': set command = complete playwright Python script that saves output to './transfer/'."
        )

        fallback_response = {
            "reply": "System failure: All AI providers exhausted or failed to process the request.",
            "action": "none",
            "command": ""
        }

        if not self.providers:
            fallback_response["reply"] = "ERROR: No API Keys configured. Cannot process messages."
            return fallback_response

        if self.workflow_logger:
            self.workflow_logger.log(f"AI Request: '{user_message}'")

        for provider in self.providers:
            logger.info(f"Attempting inference via {provider['name']} (Model: {provider['model']})")

            payload = {
                "model": provider["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            }

            if provider["name"] in ["OpenRouter", "OpenAI"]:
                payload["response_format"] = {"type": "json_object"}

            max_retries = 1
            for attempt in range(max_retries + 1):
                try:
                    response = requests.post(provider["url"], headers=provider["headers"], json=payload, timeout=30)

                    if response.status_code == 429 or "rate_limit" in response.text.lower():
                        if attempt < max_retries:
                            logger.warning(f"[{provider['name']}] Rate limited (429). Retrying...")
                            time.sleep(1)
                            continue
                        else:
                            logger.warning(f"[{provider['name']}] Account exhausted. Falling back...")
                            break

                    response.raise_for_status()

                    data = response.json()
                    raw_content = data["choices"][0]["message"]["content"]

                    match = re.search(r"\{.*\}", raw_content, re.DOTALL)
                    json_str = match.group(0) if match else raw_content

                    parsed_intent = json.loads(json_str)

                    result = {
                        "reply": parsed_intent.get("reply", "Action executed with absolute precision."),
                        "action": parsed_intent.get("action", "none"),
                        "command": parsed_intent.get("command", ""),
                        "job_id": parsed_intent.get("job_id", ""),
                        "interval_seconds": int(parsed_intent.get("interval_seconds", 0)),
                        "interval_minutes": int(parsed_intent.get("interval_minutes", 0)),
                        "interval_hours": int(parsed_intent.get("interval_hours", 0))
                    }

                    if self.workflow_logger:
                        self.workflow_logger.log(f"AI Success (Account {self.providers.index(provider)+1})")

                    return result

                except requests.exceptions.HTTPError as e:
                    logger.error(f"[{provider['name']}] API Error (Status {response.status_code}): {e}")
                    break
                except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                    logger.error(f"[{provider['name']}] Execution Error: {e}")
                    break

        logger.error("Failed to communicate successfully across all AI providers.")
        if self.workflow_logger:
            self.workflow_logger.log("AI Error: Exhausted all fallback providers.")

        fallback_response["reply"] = "Critical System Failure: All AI cores are offline or rate-limited."
        return fallback_response
