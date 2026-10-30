# 🤖 Agentic Analytics: Natural Language to Insights

This is a minimal, end-to-end prototype demonstrating an AI Agent architecture querying business metrics via a Semantic Layer.

## 🏗️ Architecture
- **Database**: PostgreSQL (Pagila dataset representing a DVD rental business)
- **Semantic Layer**: Cube.dev (Translates API calls to SQL, prevents AI hallucinations)
- **AI Agent UI**: Streamlit + LLM (Translates Natural Language to JSON Query)

## 🚀 How to Run Locally

**1. Clone the repository & Start the Data Layer**
```bash
git clone <你的GitHub仓库地址>
cd <你的项目名>
# This will spin up Postgres and Cube.dev, and initialize the mock dataset
docker-compose up -d
```

**2. Setup Python Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure API Key**
Create a `.env` file in the root directory and add your LLM API Key (Groq/OpenRouter/OpenAI):
```text
LLM_API_KEY=your_api_key_here
```

**4. Run the Streamlit App**
```bash
streamlit run app.py
```

**Open `http://localhost:8501` to start chatting with your data!**
