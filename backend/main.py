from fastapi import FastAPI, UploadFile, File
import pandas as pd
import shutil
import os
import ollama
import matplotlib.pyplot as plt
from fastapi.staticfiles import StaticFiles

# Initialize app
app = FastAPI()

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

df = None


# Home route
@app.get("/")
def home():
    return {"message": "AI Data Analyst Running (AI + Charts + Insights)"}


# Upload CSV
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global df

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_csv(file_path)

    # Convert Value column to numeric
    if "Value" in df.columns:
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    return {
        "message": "File uploaded successfully",
        "columns": list(df.columns),
        "rows": len(df)
    }


# Preview data
@app.get("/data-preview/")
def preview_data():
    global df

    if df is None:
        return {"error": "No data uploaded"}

    return df.head().to_dict()



def execute_code(code: str, df):
    local_vars = {"df": df, "plt": plt}

    try:
        exec(code, {}, local_vars)

        # Check if plot created
        if plt.get_fignums():
            plot_path = "data/plot.png"
            plt.savefig(plot_path)
            plt.close()
            return {"type": "plot", "path": plot_path}

        return {"type": "text", "value": local_vars.get("result", "No result")}

    except Exception as e:
        return {"type": "error", "value": str(e)}


# Insight generator
def generate_insight(df):
    summary = df.groupby("Variable_name")["Value"].sum().sort_values(ascending=False)

    top = summary.index[0]
    bottom = summary.index[-1]

    return f"""
Top category: {top}
Lowest category: {bottom}

Insight:
{top} contributes the highest value, while {bottom} is the lowest.
This shows an imbalance in financial distribution.
"""


# Ask your data 
@app.post("/ask/")
async def ask_question(question: str):
    global df

    if df is None:
        return {"error": "No data uploaded"}

    # STEP 1: Detect visualization queries
    if "chart" in question.lower() or "plot" in question.lower() or "graph" in question.lower():

        code = """
result = df.groupby("Variable_name")["Value"].sum()
result = result.sort_values(ascending=False)

result.plot(kind="bar", figsize=(12,6))
plt.title("Total Value by Variable Name")
plt.xlabel("Variable Name")
plt.ylabel("Value")
plt.xticks(rotation=60)
plt.tight_layout()
"""

        output = execute_code(code, df)
        insight = generate_insight(df)

        return {
            "question": question,
            "generated_code": code,
            "output": output,
            "insight": insight
        }

    # STEP 2: AI for calculations
    columns = list(df.columns)

    prompt = f"""
You are a Python data analyst.

Dataset columns:
{columns}

STRICT RULES:
- ONLY return Python code
- NO explanation
- NO print statements
- Use ONLY these columns: {columns}
- Use dataframe 'df'
- Store final answer in variable 'result'

IMPORTANT:
- If question is about total value → use df["Value"].sum()

Example:
result = df["Value"].sum()

Question:
{question}
"""

    response = ollama.chat(
        model="tinyllama",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = response["message"]["content"]

    # Extract ONLY first valid result line
    lines = raw_output.split("\n")

    code = None
    for line in lines:
        line = line.strip()

        if line.startswith("result"):
            code = line
            break

    #  Fallback
    if not code:
        code = 'result = df["Value"].sum()'

    # Ensure single line only
    code = code.split("\n")[0].strip()

    # Execute
    output = execute_code(code, df)

    return {
        "question": question,
        "generated_code": code,
        "output": output
    }


app.mount("/data", StaticFiles(directory="data"), name="data")
