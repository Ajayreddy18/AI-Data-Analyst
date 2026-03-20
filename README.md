 AI Data Analyst (GenAI Project)

Overview
This project is an AI-powered data analyst that allows users to:
- Upload CSV datasets
- Ask questions in natural language
- Generate insights
- Create visualizations automatically

Features
- Local LLM (TinyLlama) for privacy
- Natural language → Python code generation
- Safe code execution
- Automatic chart generation (matplotlib)
- Insight generation
- Streamlit chat UI

Tech Stack
- FastAPI
- Streamlit
- Pandas
- Matplotlib
- Ollama (TinyLlama)

Example Queries
- "What is the total value?"
- "Show bar chart of variable_name vs value"

How to Run

Backend
```bash
uvicorn main:app --reload