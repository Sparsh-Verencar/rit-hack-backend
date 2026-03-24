import os
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_anthropic.chat_models import ChatAnthropic

# Import the tools we just separated
from agents.tools import (
    get_csv_summary,
    standardize_columns,
    remove_duplicates,
    handle_missing_values,
    fix_formatting,
)

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

# Initialize the LLM (Using the correct latest Sonnet identifier)
llm = ChatAnthropic(
    model="claude-opus-4-6",
    api_key=API_KEY,
    temperature=0,
)

# --------------------------------------------------
# SUBAGENTS (The Specialists)
# --------------------------------------------------
# Deep Agents will automatically convert these dicts into subagents 
# accessible via the main agent's `task` tool.
subagents_config = [
    {
        "name": "missing-values-agent",
        "description": "Call this agent to fix, fill, or impute missing data (NaN/Nulls).",
        "tools": [handle_missing_values],
        "system_prompt": "You are a missing-data specialist. Run the handle_missing_values tool on the file path provided to you."
    },
    {
        "name": "duplicates-agent",
        "description": "Call this agent to find and remove duplicate rows.",
        "tools": [remove_duplicates],
        "system_prompt": "You are a deduplication specialist. Run the remove_duplicates tool on the file path provided to you."
    },
    {
        "name": "formatting-agent",
        "description": "Call this agent to fix column names, whitespaces, and general text formatting.",
        "tools": [standardize_columns, fix_formatting],
        "system_prompt": "You are a formatting specialist. Use standardize_columns and fix_formatting on the file path provided to you."
    }
]

# --------------------------------------------------
# MAIN ORCHESTRATOR
# --------------------------------------------------
def get_graphify_agent():
    """Returns the main orchestrator agent."""
    return create_deep_agent(
        model=llm,
        tools=[get_csv_summary],  # Main agent can check the file itself
        subagents=subagents_config,
        system_prompt="""
You are Graphify's Lead Data Cleaning Agent.
Your job is to read user prompts and apply the requested changes to a CSV file.

When you receive a file_path and a user request:
1. Run `get_csv_summary` to understand the current state of the dataset.
2. Use your built-in `write_todos` tool to make a plan based ONLY on what the user asked. (Do not do extra work they didn't ask for).
3. Use your `task` tool to delegate the work to the appropriate specialized subagents. You MUST pass the `file_path` to the subagents so they know what file to edit.
4. Once the subagents complete their tasks, run `get_csv_summary` one last time to verify.
5. Provide a short, final RESULT summary of what was accomplished.
"""
    )