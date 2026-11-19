import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


# Dynamically locate project root
def _find_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    while curr.parent != curr:
        if (curr / "pytest.ini").exists() or (curr / ".env").exists():
            return curr
        curr = curr.parent
    return Path(__file__).resolve().parent.parent


ROOT_DIR = _find_project_root()
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class EnvironmentConfig:
    """Universal environment configuration loaded from .env."""
    base_url: str
    admin_username: str
    admin_password: str
    default_clinic: str
    is_headless: bool
    browser_timeout: int
    viewport_width: int
    viewport_height: int
    auto_open_report: bool


def load_env() -> EnvironmentConfig:
    base_url = os.getenv("BASE_URL", "http://54.169.232.62/admin/")
    admin_username = os.getenv("ADMIN_USERNAME", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    default_clinic = os.getenv("DEFAULT_CLINIC", "RAC")
    is_headless = os.getenv("HEADLESS", "true").lower() != "false"
    browser_timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    viewport_width = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    viewport_height = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    auto_open_report = os.getenv("AUTO_OPEN_REPORT", "false").lower() in ("true", "1", "yes")

    if not admin_username or not admin_password:
        raise ValueError(
            "Missing ADMIN_USERNAME or ADMIN_PASSWORD in environment! "
            "Please ensure your .env file is configured."
        )

    return EnvironmentConfig(
        base_url=base_url,
        admin_username=admin_username,
        admin_password=admin_password,
        default_clinic=default_clinic,
        is_headless=is_headless,
        browser_timeout=browser_timeout,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        auto_open_report=auto_open_report,
    )


# Global singleton instance
config = load_env()
