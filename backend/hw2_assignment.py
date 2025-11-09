#Create enum for these:dietary_restriction,meal_type,preparation_time,primary_ingredient,cuisine_type
import asyncio
from scripts.bulk_test import run_bulk_test
from enum import Enum
import litellm
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import langsmith
from langsmith import traceable
import csv
from backend.utils import get_agent_response
from pathlib import Path
# Configure LiteLLM to use LangSmith callback only for async operations
# Note: Disabled for bulk testing to avoid event loop errors

# Debug: Check LangSmith configuration
import os


MODEL_NAME = "gpt-4o-mini"
class Dimension(Enum):
    DIETARY_RESTRICTION = "dietary_restriction"
    MEAL_TYPE = "meal_type"
    PREPARATION_TIME = "preparation_time"
    PRIMARY_INGREDIENT = "primary_ingredient"
    CUISINE_TYPE = "cuisine_type"

#now lets have some examples of each dimension
#dietary_restriction: (no dairy, no meat, no nuts, no gluten, no eggs, no soy, no shellfish)
DIETARY_RESTRICTIONS = [
    "no dairy",
    "no meat",
    "no nuts",
    "no gluten",
    "no eggs",
    "no soy",
    "no shellfish",
]

# meal_type: (breakfast, lunch, dinner, snack, dessert, appetizer, potluck, party)
MEAL_TYPES = [
    "breakfast",
    "lunch",
    "dinner",
    "snack",
    "dessert",
    "appetizer",
    "potluck",
    "party",
]

# preparation_time: (under 15 mins, 30 mins, 1 hour, 2+ hours)
PREPARATION_TIMES = [
    "under 15 mins",
    "30 mins",
    "1 hour",
    "2+ hours",
]

# primary_ingredient: (chicken, beef, seafood, vegetables, pasta, rice, beans/legumes)
PRIMARY_INGREDIENTS = [
    "chicken",
    "beef",
    "seafood",
    "vegetables",
    "pasta",
    "rice",
    "beans/legumes",
]

# cuisine_type: (Indian, Chinese, Mediterranean, Continental, Mexican, Thai, Japanese, Italian)
CUISINE_TYPES = [
    "Indian",
    "Chinese",
    "Mediterranean",
    "Continental",
    "Mexican",
    "Thai",
    "Japanese",
    "Italian",
]
# Generate Unique Combinations (Tuples):
# Write a prompt for a Large Language Model (LLM) to generate 15-20
# unique combinations (tuples) of these dimension values.
DIMENSION_TUPLES_PROMPT = """
- Generate 15-20 unique and realistic recipe query combinations using the following dimensions and their values.
- Each combination should represent a common, real-world recipe search that users would actually make.
Dimensions and Values:

- dietary_restriction: (no dairy, no meat, no nuts, no gluten, no eggs, no soy, no shellfish)
- meal_type: (breakfast, lunch, dinner, snack, dessert, appetizer, potluck, party)
- preparation_time: (under 15 mins, 30 mins, 1 hour, 2+ hours)
- primary_ingredient: (chicken, beef, seafood, vegetables, pasta, rice, beans/legumes)
- cuisine_type: (Indian, Chinese, Mediterranean, Continental, Mexican, Thai, Japanese, Italian)
Rules:

Each tuple should include ALL 5 dimensions
Use "none" for dietary_restriction if there are no restrictions
Ensure logical consistency (e.g., don't pair "no meat" with "chicken" as primary ingredient)
Focus on popular, high-frequency combinations that real users search for
Include a mix of simple everyday queries and special occasion queries
Ensure diversity across different dietary preferences, cuisines, and meal types

Output Format:
Provide each combination as a tuple in this format:
(dietary_restriction, meal_type, preparation_time, primary_ingredient, cuisine_type)
Example:

(no meat, dinner, 30 mins, vegetables, Indian)
(none, breakfast, under 15 mins, eggs, Continental)

Generate 15-20 such combinations that cover the most common recipe search patterns.
"""
#now lets generate the dimension tuples
@traceable(name="generate_dimension_tuples")
async def generate_dimension_tuples() -> str:
    # Enable LangSmith callback for async operations
    litellm.callbacks = ["langsmith"]
    response = await litellm.acompletion(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": DIMENSION_TUPLES_PROMPT}],
        caching=True,  # Enable caching for this call
    )
    return response.choices[0].message.content
#now lets save the dimension tuples to a python tuple
async def save_dimension_tuples():
    dimension_tuples = await generate_dimension_tuples()
    dimension_tuples = dimension_tuples.split("\n")
    
    # Parse tuples more carefully
    parsed_tuples = []
    for line in dimension_tuples:
        line = line.strip()
        
        # Handle numbered tuples like "1. (no dairy, breakfast, ...)"
        if "(" in line and ")" in line:
            # Extract the tuple part between parentheses
            start = line.find("(")
            end = line.find(")")
            if start != -1 and end != -1:
                tuple_content = line[start+1:end].strip()
                parts = [part.strip() for part in tuple_content.split(",")]
                if len(parts) == 5:  # Ensure we have exactly 5 dimensions
                    parsed_tuples.append(tuple(parts))
    
    return parsed_tuples
#lets call save_dimension_tuples and print the result
async def print_dimension_tuples():
    try:
        dimension_tuples = await save_dimension_tuples()
        print(f"Generated {len(dimension_tuples)} dimension tuples")
        for i, dimension_tuple in enumerate(dimension_tuples):
            if len(dimension_tuple) == 5:
                print(f"Tuple {i+1}: {dimension_tuple[0]}, {dimension_tuple[1]}, {dimension_tuple[2]}, {dimension_tuple[3]}, {dimension_tuple[4]}")
            else:
                print(f"Tuple {i+1}: Invalid format - {dimension_tuple}")
        print("Saved dimension tuples to a python tuple")
        return dimension_tuples
    except Exception as e:
        print(f"Error generating dimension tuples: {e}")
        return None
"""
**Generate Natural Language User Queries:**
    *   Write a second prompt for an LLM to take 5-7 of the generated tuples and create a natural language user query for your Recipe Bot for each selected tuple.
    *   Review these generated queries to ensure they are realistic and representative of how a user might interact with your bot.
"""
NATURAL_LANGUAGE_USER_QUERIES_PROMPT = """
    Generate 5-7 natural language user queries for a recipe chatbot based on the following dimensions and values:
    {dimension_tuples}
    - queries should be realistic and representative of how a user might interact with your bot.
    - queries should be in natural language and should be easy to understand.
    - queries should be 10-30 words long.
    - queries should be unique and should not be repetitive.
    - queries should realistic user queries.
Think of breaking the recipie chat bot with your queries.
    """
@traceable(name="generate_natural_language_user_queries")
async def generate_natural_language_user_queries(dimension_tuples: list[tuple]) -> str:
    # Enable LangSmith callback for async operations
    litellm.callbacks = ["langsmith"]
    print(f"Generating natural language user queries for dimension tuples: {dimension_tuples}")
    response = await litellm.acompletion(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": NATURAL_LANGUAGE_USER_QUERIES_PROMPT.format(dimension_tuples=dimension_tuples)}],
        caching=True,  # Enable caching for this call
    )
    return response.choices[0].message.content
"""
    Save the natural language user queries to a csv file with the following columns:
    - query_id
    - natural_language_query
    
"""
@traceable(name="save_natural_language_user_queries")
async def save_natural_language_user_queries(natural_language_user_queries: list[str]):
    with open('natural_language_user_queries.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['query_id', 'natural_language_query'])
        for i, query in enumerate(natural_language_user_queries):
            writer.writerow([i+1, query])
    return natural_language_user_queries

def parse_natural_language_queries(queries_text: str) -> list[str]:
    """Parse the natural language queries from the LLM response."""
    lines = queries_text.split('\n')
    queries = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        # Handle numbered list items like "1. "query text""
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            # Remove the number and period
            line = line.split('.', 1)[1].strip()
        
        # Remove quotes if present
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        elif line.startswith("'") and line.endswith("'"):
            line = line[1:-1]
            
        if line and not line.startswith('Here are some'):
            queries.append(line)
    
    return queries



    
if __name__ == "__main__":
    result = run_bulk_test(Path("natural_language_user_queries.csv"))
    print(result)
     
    