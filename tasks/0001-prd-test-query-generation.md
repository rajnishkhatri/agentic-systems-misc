# Product Requirements Document: Test Query Generation System

## Introduction/Overview

The Recipe Bot Test Query Generation System will create a diverse, realistic dataset of user queries to evaluate the bot's response quality across different scenarios and identify edge cases and weaknesses. The system will generate 15-20 unique combinations of key input dimensions (dietary restrictions, ingredient constraints, meal portions, complexity levels, meal types, and cuisine types) and convert each into natural language queries that mirror real user interactions.

This feature addresses the need for comprehensive testing coverage without manual query creation, enabling systematic evaluation of the Recipe Bot's capabilities and limitations.

## Goals

1. Generate 15-20 unique test queries covering diverse dimension combinations
2. Evaluate the Recipe Bot's response quality across different user scenarios
3. Identify edge cases, weaknesses, and failure modes in the current system
4. Create a reusable test dataset for ongoing quality assurance
5. Ensure test queries span all complexity levels (simple to edge cases)

## User Stories

- **As a developer**, I want to generate diverse test queries automatically so that I can quickly evaluate the Recipe Bot's performance across different scenarios without manually crafting queries.

- **As a QA engineer**, I want test queries that cover edge cases so that I can identify weaknesses before users encounter them.

- **As a product owner**, I want to understand how the bot performs with different dietary restrictions and ingredient constraints so that I can prioritize improvements.

- **As a developer**, I want test queries stored in CSV format so that I can easily load them into automated testing pipelines.

## Functional Requirements

### FR1: Dimension Definition

The system must use the following 5 key dimensions (ranked by importance):

1. **dietary_restriction** (Priority 1):
   - Values: vegetarian, vegan, gluten-free, dairy-free, keto, paleo, nut-free, low-carb, halal
   - At least 3 values must be used in the generated queries

2. **ingredient_constraints** (Priority 2):
   - Values: specific ingredients available, pantry-only, leftovers, seasonal ingredients, minimal ingredients, one-pot meals
   - At least 3 values must be used in the generated queries

3. **meal_portion** (Priority 3):
   - Values: 1 person, 2 people, 4 people, 6 people
   - **Optional dimension**: Include when relevant to the query (not required in all tuples)
   - Aligns with Recipe Bot's system prompt requirement to mention serving size

4. **complexity_level** (Priority 4):
   - Values: quick/simple (≤30 min), moderate (30-60 min), advanced/gourmet (>60 min)
   - All 3 values must be used in the generated queries

5. **meal_type** (Priority 5):
   - Values: breakfast, lunch, dinner, snack, dessert, brunch, appetizer
   - At least 3 values must be used in the generated queries

**Optional 6th dimension**:
- **cuisine_type** (Priority 6): Italian, Mexican, Indian, Japanese, Chinese, Thai, Mediterranean, American
- This dimension may be used but is not required

### FR2: Tuple Generation

The system must generate 15-20 unique tuples by:

1. Using the existing `get_agent_response()` function from `backend/utils.py`
2. Prompting an LLM to create combinations that maximize coverage across all dimensions
3. Ensuring no duplicate tuples exist
4. Including at least one tuple for each individual dimension value (from priorities 1, 2, 4, 5)
5. Generating tuples that represent realistic user scenarios (not random combinations)
6. Including `meal_portion` dimension when it naturally fits the query context (optional)

**Example tuple formats**:
```
With meal_portion:
(dietary_restriction: "vegan", ingredient_constraints: "pantry-only", meal_portion: "4 people", complexity_level: "quick/simple", meal_type: "dinner")

Without meal_portion (when not contextually relevant):
(dietary_restriction: "none", ingredient_constraints: "specific ingredients", meal_portion: "", complexity_level: "moderate", meal_type: "lunch")
```

### FR3: Natural Language Query Generation

The system must convert all 15-20 tuples into natural language user queries by:

1. Using the existing `get_agent_response()` function from `backend/utils.py`
2. Generating queries that include all complexity types:
   - **Simple/direct**: "Give me a pasta recipe"
   - **Constrained**: "I have chicken, tomatoes, and rice. What can I make?"
   - **Multi-constraint**: "Quick vegetarian dinner for 4 with no onions"
   - **Vague/exploratory**: "Something healthy and tasty"
   - **Edge cases**: Contradictory requests, unusual combinations, boundary conditions

3. Ensuring queries sound natural and realistic (as a real user would ask)
4. Varying query structure and phrasing to avoid repetitive patterns
5. Target query length: 10-30 words per query

**Example query generation**:
```
Tuple with meal_portion:
(dietary: "vegan", ingredients: "pantry-only", portion: "4 people", complexity: "quick", meal: "dinner")
Query: "I need a quick vegan dinner recipe for 4 people using only pantry staples"

Tuple without meal_portion:
(dietary: "gluten-free", ingredients: "specific ingredients", portion: "", complexity: "moderate", meal: "lunch")
Query: "I have zucchini and chicken. Can you suggest a gluten-free lunch recipe?"

Tuple with meal_portion for single serving:
(dietary: "keto", ingredients: "minimal ingredients", portion: "1 person", complexity: "quick", meal: "breakfast")
Query: "What's a simple keto breakfast I can make just for myself with minimal ingredients?"
```

### FR4: Output Format

The system must save generated queries as a CSV file in the `/data/` directory with the following structure:

**Required columns**:
- `query_id`: Sequential integer starting from 1
- `dietary_restriction`: Value from FR1 or "none"
- `ingredient_constraints`: Value from FR1 or "none"
- `meal_portion`: Value from FR1 or empty string (optional dimension)
- `complexity_level`: Value from FR1
- `meal_type`: Value from FR1
- `cuisine_type`: Value from FR1 or empty string (optional dimension)
- `natural_language_query`: The generated user query text

**File specifications**:
- Filename: `test_queries_generated_[YYYYMMDD_HHMMSS].csv`
- Include header row
- Use proper CSV escaping for queries containing commas/quotes
- UTF-8 encoding

**Example CSV format**:
```csv
query_id,dietary_restriction,ingredient_constraints,meal_portion,complexity_level,meal_type,cuisine_type,natural_language_query
1,vegan,pantry-only,4 people,quick,dinner,,"I need a quick vegan dinner recipe for 4 using only pantry staples"
2,gluten-free,specific ingredients,,moderate,lunch,Italian,"I have zucchini and chicken. Can you suggest a gluten-free Italian lunch?"
3,vegetarian,minimal ingredients,2 people,quick,breakfast,,"Quick vegetarian breakfast ideas for two people?"
```

### FR5: Quality Validation

The system must validate generated queries against these criteria:

1. **Coverage**: All dimension values (from priorities 1, 2, 4, 5) appear at least once across all queries
   - **Note**: `meal_portion` (Priority 3) is optional and does NOT require 100% coverage
   - Recommended: Include `meal_portion` in at least 40-60% of queries where contextually appropriate
2. **Naturalness**: Queries are grammatically correct and conversational
3. **Diversity**: Query structures vary (questions, statements, multi-sentence)
4. **Edge cases**: At least 3 queries (15%) test boundary conditions or contradictions
5. **Validation**: Each query must produce a valid (non-error) response from the Recipe Bot

The system must report validation results including:
- Coverage percentage for each dimension (required and optional)
- Count of queries by complexity type
- Validation pass/fail rate
- Percentage of queries that include `meal_portion` dimension

### FR6: Script Execution

The system must provide a standalone Python script that:

1. Can be executed from the command line: `python generate_test_queries.py`
2. Outputs progress messages during generation:
   - "Generating dimension tuples..."
   - "Created 15 unique tuples"
   - "Generating natural language queries..."
   - "Query 5/15 generated"
3. Reports success/failure for each query generated
4. Displays summary statistics upon completion:
   - Total queries generated
   - Coverage % for each dimension
   - Validation pass rate
   - Output file path
5. Handles errors gracefully (API failures, rate limits, etc.)

## Non-Goals (Out of Scope)

The following items are explicitly **NOT** included in this feature:

1. **Ground truth responses**: This feature will NOT generate expected/ideal responses for each query
2. **Automated evaluation metrics**: Will NOT calculate BLEU, ROUGE, or other response quality scores
3. **Query categorization system**: Will NOT create tags or categories beyond the defined dimensions
4. **Continuous query generation**: Will NOT set up automated/scheduled query generation
5. **User feedback integration**: Will NOT incorporate real user queries or feedback into generation
6. **Multi-turn conversations**: Queries will be single-turn only (no follow-up dialogue)
7. **Response storage**: Will NOT save the Recipe Bot's responses to the generated queries
8. **Performance benchmarking**: Will NOT measure response time or token usage

## Design Considerations

### Prompt Engineering

The LLM prompts for tuple and query generation should be carefully crafted to ensure diversity and realism:

1. **Tuple Generation Prompt**: Should instruct the LLM to create combinations that:
   - Cover all dimension values at least once
   - Represent realistic user scenarios
   - Include some challenging/edge case combinations
   - Avoid obviously contradictory combinations (unless intentional edge cases)

2. **Query Generation Prompt**: Should instruct the LLM to:
   - Write queries as a real user would ask them
   - Vary sentence structure and phrasing
   - Include appropriate level of detail based on complexity type
   - Match the conversational tone users would naturally use

### CSV Format Compatibility

- Follow the same structure as existing `data/sample_queries.csv` if it exists for consistency
- Ensure the CSV can be easily loaded with `pandas.read_csv()` without special parameters
- Use standard CSV conventions (comma delimiter, quoted strings, escaped quotes)

### Query Characteristics

- **Query Length**: Target 10-30 words per query to match typical user input patterns
- **Tone**: Conversational, not formal or technical
- **Specificity**: Vary from vague ("something healthy") to specific ("chicken tikka masala for 4 people")
- **Meal Portion Usage**: Include portion size naturally when users would typically specify it (e.g., family dinners, gatherings) rather than forcing it into every query

### Code Readability

- Include detailed comments in the generation script explaining:
  - Why each dimension was chosen
  - Prompt engineering strategies
  - Validation logic
- Follow existing code style from `backend/utils.py`

## Technical Considerations

### 1. LLM Integration

- Use `get_agent_response()` from `backend/utils.py` (lines 57-92)
- Maintain conversation history for multi-step generation (tuples first, then queries)
- Handle the system prompt appropriately (may need custom prompt for generation vs. recipe responses)

### 2. Model Selection

- Inherit the `MODEL_NAME` from environment variables (currently `gpt-4o-mini` by default)
- Ensure `.env` file is loaded using `load_dotenv()`
- The same model used for Recipe Bot responses will be used for query generation

### 3. Dependencies

- Ensure `litellm` and `python-dotenv` are available (already in `utils.py`)
- Use Python standard library `csv` module for output generation
- No additional external dependencies required

### 4. Error Handling

Implement robust error handling for:
- LLM API failures (network issues, rate limits, timeouts)
- Invalid LLM responses (malformed JSON, missing fields)
- CSV writing errors (file permissions, disk space)
- Validation failures (bot errors, empty responses)

Retry logic:
- Retry LLM calls up to 3 times with exponential backoff
- Log all errors with timestamps
- Continue generation even if individual queries fail (skip and report)

### 5. Determinism

- Consider adding a `--seed` command-line parameter for reproducible generation
- Document that results may vary between runs due to LLM non-determinism
- The timestamp in the filename ensures outputs don't overwrite each other

### 6. Validation Loop

After generating queries, the script should:
1. Run each query through the Recipe Bot using `get_agent_response()`
2. Check that a response was received (not empty, not error message)
3. Log any queries that fail validation
4. Report the overall validation pass rate

**Note**: Validation does NOT check response quality, only that a response was generated.

### 7. File Paths

- Use relative paths from project root: `data/test_queries_generated_[timestamp].csv`
- Create `/data/` directory if it doesn't exist
- Handle path separators correctly for cross-platform compatibility

## Success Metrics

The feature will be considered successful if it meets these quantifiable criteria:

1. **Coverage**: 100% of dimension values (from priorities 1, 2, 4, 5) appear in at least one query
   - `meal_portion` (Priority 3) is optional and not required for 100% coverage
2. **Naturalness**: Manual review confirms 90%+ of queries sound like real user inputs
3. **Diversity**: Query structure variation with at least 5 different question/statement patterns
4. **Edge cases**: At least 15% of queries (3+) test boundary conditions or challenging scenarios
5. **Validation**: 100% of queries produce valid (non-error) responses from the Recipe Bot
6. **Generation Time**: Full dataset of 15-20 queries generated in <5 minutes
7. **Reusability**: CSV can be loaded and used in automated test scripts without modification

## Open Questions

1. ~~Should we include a dimension for **serving_size**?~~ **RESOLVED**: Added as `meal_portion` (Priority 3, optional)
2. Should edge case queries intentionally try to break the bot (e.g., "vegan steak recipe", "gluten-free bread with wheat flour")?
3. Do we need to handle multi-language queries, or English only?
4. Should the script support incremental generation (add more queries to existing CSV)?
5. What's the acceptable failure rate during validation (e.g., if 1-2 queries produce errors, should we regenerate or accept them as edge cases)?
6. Should we log the LLM's intermediate outputs (tuple generation step) for debugging/transparency?
7. Should the script support custom dimension values via command-line arguments or configuration file?
8. Do we need to track token usage and costs for the generation process?
