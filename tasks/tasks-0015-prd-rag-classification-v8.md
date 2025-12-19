# Tasks: RAG Classification Prototype (V8)

**Based on PRD:** `tasks/0015-prd-rag-classification-v8.md`
**Goal:** Implement a RAG-based classification phase that uses historical precedents to resolve ambiguity.
**Working Directory:** `lesson-18/dispute-chatbot/`

## Relevant Files

- `pyproject.toml` - Dependency management
- `scripts/build_vector_store.py` - **(New)** Script to generate embeddings
- `backend/adapters/rag_retriever.py` - **(New)** Adapter for similarity search
- `backend/phases/classify_v8_rag.py` - **(New)** V8 classification phase
- `prompts/DisputeClassifier_identify_category_v8_rag.j2` - **(New)** Prompt template
- `synthetic_data/phase1/golden_set/natural_language_classification_v2.json` - Knowledge Base source
- `backend/data/vector_store.pkl` - **(New)** Artifact

### Notes
- Ensure `backend/data/` is in `.gitignore` if the pkl is large (it should be small enough for now, but good practice).
- `sentence-transformers` model will download on first run; cache it if possible.

### Assumptions Made
- **Environment:** Running in a python venv managed by `uv` or `pip`.
- **Paths:** All paths relative to `lesson-18/dispute-chatbot/`.
- **Model:** `all-MiniLM-L6-v2` is sufficient for prototype.

## Tasks

- [ ] 1.0 Infrastructure & Dependencies
  - [x] 1.1 Add `sentence-transformers` to `pyproject.toml` dependencies
        Input: `pyproject.toml` | Output: Added dependency | Verification: `pip install .` or `uv sync` succeeds
  - [x] 1.2 Create `backend/data/` directory for storing artifacts
        Input: None | Output: Directory created | Verification: `ls backend/data` exists
  - [x] 1.3 Verify `natural_language_classification_v2.json` availability
        Input: Path check | Output: Confirmed path | Verification: File exists at `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v2.json`

- [x] 2.0 Vector Store Creation
  - [x] 2.1 Create `scripts/build_vector_store.py`
        Input: None | Output: Script file | Verification: File created
  - [x] 2.2 Implement Data Loading
        Input: Golden Set JSON | Output: List of Dicts | Verification: `print(len(data))` matches file line count
  - [x] 2.3 Implement Embedding Generation
        Input: `sentence-transformers`, descriptions | Output: Vectors (numpy array) | Verification: Shape is (N, 384)
  - [x] 2.4 Implement Persistence
        Input: Vectors + Metadata | Output: `backend/data/vector_store.pkl` | Verification: File created and > 0 bytes

- [x] 3.0 RAG Retriever Implementation
  - [x] 3.1 Create `backend/adapters/rag_retriever.py`
        Input: None | Output: File created | Verification: File exists
  - [x] 3.2 Implement `RagRetriever` class initialization
        Input: path to pkl | Output: Object with loaded vectors | Verification: No crash on init
  - [x] 3.3 Implement `retrieve_similar`
        Input: `query_text`, `k` | Output: List of top `k` matches | Verification: Returns relevant items for "fraud" query

- [x] 4.0 Prompt Engineering (V8)
  - [x] 4.1 Create `prompts/DisputeClassifier_identify_category_v8_rag.j2`
        Input: `v7_hybrid` template | Output: New template | Verification: File exists
  - [x] 4.2 Inject Examples Section
        Input: Jinja2 loop for `examples` | Output: Rendered prompt has examples | Verification: Visual check
  - [x] 4.3 Update System Instructions
        Input: Text update | Output: Instructions to "use precedents" | Verification: Text present

- [x] 5.0 Phase V8 Implementation
  - [x] 5.1 Create `backend/phases/classify_v8_rag.py`
        Input: `v7_hybrid.py` | Output: New phase file | Verification: File exists
  - [x] 5.2 Integrate Retriever
        Input: `RagRetriever` | Output: `_run` calls `retrieve_similar` | Verification: Context updated
  - [x] 5.3 Pass Context to LLM
        Input: Retrieved items | Output: `llm_service.get_response` call includes examples | Verification: Dry run

- [x] 6.0 Evaluation
  - [x] 6.1 Create `scripts/evaluate_v8_rag_trace.py`
        Input: `evaluate_v6_trace.py` | Output: New eval script | Verification: File exists
  - [x] 6.2 Run Evaluation
        Input: Test set | Output: Accuracy report | Verification: Script runs successfully

