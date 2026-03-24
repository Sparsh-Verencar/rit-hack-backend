import pandas as pd
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# --------------------------------------------------
# TOOL INPUT SCHEMA
# --------------------------------------------------
class FilePathInput(BaseModel):
    # Added a description so the LLM knows exactly what to pass here
    file_path: str = Field(..., description="The local path to the temporary CSV file")

# --------------------------------------------------
# TOOLS
# --------------------------------------------------
@tool(args_schema=FilePathInput)
def get_csv_summary(file_path: str) -> str:
    """Reads a CSV file and returns a summary of its shape, columns, and missing values."""
    df = pd.read_csv(file_path)
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }
    return str(summary)

@tool(args_schema=FilePathInput)
def standardize_columns(file_path: str) -> str:
    """Lowercases and strips column names, replacing spaces with underscores. Overwrites the file."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.to_csv(file_path, index=False)
    return "Columns standardized successfully."

@tool(args_schema=FilePathInput)
def remove_duplicates(file_path: str) -> str:
    """Removes duplicate rows from the CSV file. Overwrites the file."""
    df = pd.read_csv(file_path)
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    df.to_csv(file_path, index=False)
    return f"Removed {before - after} duplicate rows. {after} rows remaining."

@tool(args_schema=FilePathInput)
def handle_missing_values(file_path: str) -> str:
    """Fills missing values with median (for numbers) or 'unknown' (for text). Overwrites the file."""
    df = pd.read_csv(file_path)
    df = df.dropna(how="all")
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("unknown")
    df.to_csv(file_path, index=False)
    return "Missing values handled successfully."

@tool(args_schema=FilePathInput)
def fix_formatting(file_path: str) -> str:
    """Strips whitespace from all string cells in the CSV file. Overwrites the file."""
    df = pd.read_csv(file_path)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(file_path, index=False)
    return "Formatting fixed. Whitespace stripped from all string cells."