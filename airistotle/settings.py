# Built-ins
from pathlib import Path

# Third-party
import dotenv

# AIRISTOTLE
from .logger import GlobalLogger
from .plugins import WebSearch


env = dotenv.dotenv_values(".env")
DEBUG = env.get("DEBUG", False)


def get_default(value: str) -> str:
    return value if DEBUG else ""

LOG_LEVEL = int(env.get("AIRISTOTLE_LOG_LEVEL", get_default("5")) or 10)
OPENAI_API_KEY = str(env.get("AIRISTOTLE_OPENAI_API_KEY", get_default("debug")))
GOOGLE_API_KEY = env.get("ARISTOTLE_GOOGLE_API_KEY", get_default("debug"))
GOOGLE_CSE_ID = env.get("AIRISTOTLE_GOOGLE_CSE_ID", get_default("debug"))
SERPER_API_KEY = env.get("AIRISTOTLE_SERPER_API_KEY", get_default("debug"))
SLACK_BOT_TOKEN = env.get("AIRISTOTLE_SLACK_BOT_TOKEN", get_default("debug"))
SLACK_APP_TOKEN = env.get("AIRISTOTLE_SLACK_APP_TOKEN", get_default("debug"))
SLACK_SIGNING_SECRET = env.get("AIRISTOTLE_SLACK_SIGNING_SECRET", get_default("debug"))
ASSISTANT_ID = str(env.get("AIRISTOTLE_ASSISTANT_ID", get_default("debug")))

DB_LOCATION = Path(__file__).parent / "storage" / "database.json"
LOG_FILE_LOCATION = str(Path(__file__).parent.parent / "AIRISTOTLE.log")

LOGGER = GlobalLogger("AIRISTOTLE", log_file=LOG_FILE_LOCATION, level=LOG_LEVEL)

AVAILABLE_PLUGINS = {
    WebSearch.name: WebSearch(
        openai_api_key=OPENAI_API_KEY,
        google_api_key=GOOGLE_API_KEY,
        google_cse_id=GOOGLE_CSE_ID,
    ),
}
