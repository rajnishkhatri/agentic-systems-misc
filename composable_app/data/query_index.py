## make sure logging starts first
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
from llama_index.core import StorageContext, Settings, load_index_from_storage
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.llms.openai import OpenAI
from utils import llms
import logging
from pprint import pprint
import os
from agents.article import Article

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    Settings.embed_model = OpenAIEmbedding(model=llms.EMBED_MODEL, api_key=os.environ.get("OPENAI_API_KEY"))
    Settings.llm = OpenAI(model=llms.DEFAULT_MODEL, api_key=os.environ.get("OPENAI_API_KEY"))
    storage_context = StorageContext.from_defaults(persist_dir="data")
    index = load_index_from_storage(storage_context)

    retriever = index.as_retriever(similarity_top_k=3)
    response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.COMPACT  # detailed answer after compacting all the retrieved chunks
    )

    def semantic_rag(topic):
        nodes = retriever.retrieve(topic)
        response = response_synthesizer.synthesize(f"Based on the information provided, write a 2-paragraph article on {topic}",
                                                   nodes=nodes)
        response = {
            "response": response.response,
            "source_nodes": [{
                "page_number": node.metadata['bbox'][0]['page'],
                "score": node.score,
                "text_begin": node.text[:50],
                "text_end": node.text[-50:]
            } for node in response.source_nodes]
        }
        return response


    print("*** SEMANTIC RAG***")
    result = semantic_rag("What is in-context learning?")
    pprint(result)
