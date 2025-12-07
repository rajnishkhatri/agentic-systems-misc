## make sure logging starts first
from llama_index.llms.openai import OpenAI


def setup_logging(config_file: str = "logging.json"):
    import json
    import logging.config

    # Load the JSON configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Apply the configuration
    logging.config.dictConfig(config)
setup_logging()
##

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from utils import llms
import openparse
import logging
import os

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    Settings.embed_model = OpenAIEmbedding(model=llms.EMBED_MODEL, api_key=os.environ.get("OPENAI_API_KEY"))
    Settings.llm = OpenAI(model=llms.DEFAULT_MODEL, api_key=os.environ.get("OPENAI_API_KEY"))

    DOC_PATH = "data/book.pdf"
    if not os.path.exists(DOC_PATH):
        logger.error(f"Please place a file named {DOC_PATH} or use the checked-in index as-is")
        raise Exception(f"{DOC_PATH} not found")

    parser = openparse.DocumentParser()
    parsed_doc = parser.parse(DOC_PATH)
    nodes = parsed_doc.to_llama_index_nodes()
    index = VectorStoreIndex(nodes)
    index.storage_context.persist(persist_dir="data")

