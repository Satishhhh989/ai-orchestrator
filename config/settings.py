import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:

    telegram_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_TOKEN", ""))
    user_id: int = field(default_factory=lambda: int(os.getenv("USER_ID", "0")))

    openrouter_api_key: str = field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY", "")
    )
    openrouter_model: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_MODEL", "openai/gpt-oss-120b:free"
        )
    )
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    state_file_path: str = field(
        default_factory=lambda: os.getenv("STATE_FILE", "data/state.json")
    )

    enable_gui_automation: bool = field(
        default_factory=lambda: os.getenv("ENABLE_GUI_AUTOMATION", "false").lower()
        == "true"
    )

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        missing = []

        if not self.telegram_token:
            missing.append("TELEGRAM_TOKEN")
        if self.user_id == 0:
            missing.append("USER_ID")

        if missing:
            print(f"Warning: Missing environment variables: {', '.join(missing)}")
            print("   Some features may not work. Check your .env file.")

    @property
    def is_ai_enabled(self) -> bool:
        return bool(self.openrouter_api_key)

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"telegram_token='***', "
            f"user_id={self.user_id}, "
            f"openrouter_api_key='{'set' if self.openrouter_api_key else 'unset'}', "
            f"openrouter_model='{self.openrouter_model}', "
            f"log_level='{self.log_level}'"
            f")"
        )
