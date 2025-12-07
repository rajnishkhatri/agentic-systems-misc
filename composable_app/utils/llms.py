import os
from dotenv import load_dotenv
import logging

BEST_MODEL="gpt-4o"
DEFAULT_MODEL="gpt-4o-mini"
SMALL_MODEL="gpt-4o-mini"
EMBED_MODEL="text-embedding-3-small"

logger = logging.getLogger(__name__)

def _setup():
    source_dir = os.path.dirname(os.path.abspath(__file__))
    # Load from .env file in the composable_app directory
    env_file = os.path.join(source_dir, "..", ".env")
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from .env file")
    else:
        # Try loading from current directory as fallback
        load_dotenv()
        if os.path.exists(".env"):
            logger.info(f"Loaded environment from .env file in current directory")
        else:
            logger.warning("No .env file found. Make sure to create .env with OPENAI_API_KEY")
    
    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError(
            "Please specify the OPENAI_API_KEY in .env file or as an environment variable."
        )
    if not openai_key.startswith("sk-"):
        logger.warning(
            "OPENAI_API_KEY doesn't start with 'sk-'. Please verify your API key is correct."
        )

    logger.info(f"Defaulting to {DEFAULT_MODEL}; will use {BEST_MODEL} "
                f"for higher quality and {SMALL_MODEL} for lower latency")

def default_model_settings():
    from pydantic_ai.models.openai import OpenAIModelSettings
    model_settings = OpenAIModelSettings(
                temperature=0.25,
            )
    return model_settings

# run on module load
_setup()
