# Task List: Test Query Generation System

**Source PRD**: `0001-prd-test-query-generation.md`

## Relevant Files

- `tests/generate_test_queries.py` - Main script for generating test queries with dimension tuples and LLM integration (contains dimension configuration constants)
- `tests/test_generate_test_queries.py` - Unit tests for query generation script
- `backend/utils.py` - Existing utility module with `get_agent_response()` function (lines 57-92) to be reused
- `data/test_queries_generated_[timestamp].csv` - Output CSV file (created by script)
- `data/sample_queries.csv` - Existing sample queries file for format reference

### Notes

- Leverage existing `get_agent_response()` from `backend/utils.py` for LLM calls
- Reference implementation exists in `homeworks/hw2/generate_synthetic_queries.py` but simplified for this PRD
- Use Python standard library `csv` module (no pandas required per PRD Technical Considerations #3)
- Tests should use `pytest` framework (run with `pytest test_generate_test_queries.py`)
- The script will use `MODEL_NAME` from environment variables via `backend/utils.py`

## Tasks

- [ ] **1.0 Create Dimension Configuration Module**
  - [x] 1.1 Define dimension dictionaries for all 5 required dimensions (dietary_restriction, ingredient_constraints, meal_portion, complexity_level, meal_type) and 1 optional dimension (cuisine_type) with values from PRD FR1
  - [x] 1.2 Create constants for coverage requirements (e.g., at least 3 values for priorities 1, 2, 5; all 3 for priority 4; 40-60% for optional meal_portion)
  - [x] 1.3 Add helper function to validate dimension values match PRD specifications
  - [x] 1.4 Write unit tests for dimension configuration validation

- [ ] **2.0 Implement Tuple Generation Logic**
  - [ ] 2.1 Create function `generate_dimension_tuples()` that constructs a prompt for LLM to generate 15-20 unique tuples
  - [ ] 2.2 Design prompt to instruct LLM to maximize coverage across all dimensions while creating realistic user scenarios (reference PRD Design Considerations)
  - [ ] 2.3 Use `get_agent_response()` from `backend/utils.py` to call LLM with custom system prompt (override default recipe prompt)
  - [ ] 2.4 Parse LLM response into structured tuple format (dict or dataclass with all dimension keys)
  - [ ] 2.5 Implement deduplication logic to ensure no duplicate tuples exist
  - [ ] 2.6 Verify at least one tuple exists for each dimension value (from priorities 1, 2, 4, 5)
  - [ ] 2.7 Add retry logic (up to 3 attempts with exponential backoff) for LLM API failures
  - [ ] 2.8 Write unit tests for tuple generation (mock LLM responses)

- [ ] **3.0 Implement Natural Language Query Generation**
  - [ ] 3.1 Create function `generate_query_from_tuple(tuple)` that constructs a prompt to convert tuple to natural language
  - [ ] 3.2 Design prompt to ensure queries include all complexity types (simple, constrained, multi-constraint, vague, edge cases) as per PRD FR3
  - [ ] 3.3 Instruct LLM to vary query structure (questions, statements, multi-sentence) and match conversational tone
  - [ ] 3.4 Enforce target query length of 10-30 words in the prompt
  - [ ] 3.5 Use `get_agent_response()` to generate each query, maintaining conversation history for consistency
  - [ ] 3.6 Parse LLM response to extract clean query text
  - [ ] 3.7 Implement naturalness check (basic validation: non-empty, reasonable length, no LLM artifacts)
  - [ ] 3.8 Add retry logic for failed query generation (same pattern as tuple generation)
  - [ ] 3.9 Write unit tests for query generation (mock LLM responses with various tuple types)

- [ ] **4.0 Create CSV Output Module**
  - [ ] 4.1 Create function `write_queries_to_csv(queries, output_path)` using Python's `csv` module
  - [ ] 4.2 Implement CSV schema with columns: query_id, dietary_restriction, ingredient_constraints, meal_portion, complexity_level, meal_type, cuisine_type, natural_language_query (per PRD FR4)
  - [ ] 4.3 Generate filename with timestamp: `test_queries_generated_YYYYMMDD_HHMMSS.csv`
  - [ ] 4.4 Ensure proper CSV escaping for queries containing commas/quotes using `csv.QUOTE_MINIMAL`
  - [ ] 4.5 Set UTF-8 encoding for the output file
  - [ ] 4.6 Create `/data/` directory if it doesn't exist (use `pathlib.Path.mkdir(parents=True, exist_ok=True)`)
  - [ ] 4.7 Handle file writing errors gracefully (permissions, disk space) with informative error messages
  - [ ] 4.8 Write unit tests for CSV generation (test proper formatting, escaping, encoding)

- [ ] **5.0 Build Validation and Reporting System**
  - [ ] 5.1 Create function `validate_query(query)` that runs query through Recipe Bot using `get_agent_response()`
  - [ ] 5.2 Check that response is non-empty and doesn't contain error messages
  - [ ] 5.3 Implement function `calculate_coverage(queries)` to compute coverage percentage for each dimension
  - [ ] 5.4 Verify all dimension values (priorities 1, 2, 4, 5) appear at least once; meal_portion optional
  - [ ] 5.5 Count queries by complexity type (simple, constrained, multi-constraint, vague, edge cases)
  - [ ] 5.6 Calculate percentage of queries that include `meal_portion` dimension (should be 40-60%)
  - [ ] 5.7 Track validation pass/fail rate across all queries
  - [ ] 5.8 Create function `generate_summary_report()` to display statistics: total queries, coverage %, validation rate, output file path
  - [ ] 5.9 Log any queries that fail validation with reason
  - [ ] 5.10 Write unit tests for validation logic (mock Recipe Bot responses)

- [ ] **6.0 Create Command-Line Interface and Integration**
  - [ ] 6.1 Create `main()` function that orchestrates the entire workflow: dimension setup → tuple generation → query generation → CSV output → validation → reporting
  - [ ] 6.2 Add progress messages during execution: "Generating dimension tuples...", "Created X unique tuples", "Generating natural language queries...", "Query X/Y generated" (per PRD FR6)
  - [ ] 6.3 Implement error handling for each major step with try-except blocks
  - [ ] 6.4 Add `if __name__ == "__main__":` block to make script executable via `python generate_test_queries.py`
  - [ ] 6.5 Add optional command-line argument `--seed` for reproducible generation (future enhancement, document as TODO)
  - [ ] 6.6 Ensure script completes in <5 minutes (per PRD Success Metric #6)
  - [ ] 6.7 Add docstrings to all functions following existing code style from `backend/utils.py`
  - [ ] 6.8 Add type hints to all function signatures (use `List[Dict[str, str]]`, `Optional[int]`, etc.)
  - [ ] 6.9 Verify script uses `load_dotenv()` to load environment variables (already in `backend/utils.py`)
  - [ ] 6.10 Test full end-to-end execution manually with different LLM models
  - [ ] 6.11 Write integration tests that run the full script and verify CSV output format
