import streamlit as st
import requests
import json
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize LLM Client 
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

# 2. Define Semantic Layer Menu (System Prompt) - Tell LLM what it can query
SYSTEM_PROMPT = """
You are a data analysis agent connected to the Cube.dev semantic layer.
Please generate a JSON request for querying based on the user's natural language question.
The available data model (dvd_business.yaml) is as follows:
- measures: ["payments.total_revenue", "rentals.total_rentals", "customers.total_customers"]
- dimensions: ["customers.full_name", "customers.is_active"]
- timeDimensions: ["payments.payment_date", "rentals.rental_date"]

[Strict Requirements]
1. Output ONLY a valid JSON string. Do not include any Markdown tags (such as ```json) or explanatory text.
2. Example format: {"measures": ["payments.total_revenue"], "dimensions": ["customers.full_name"], "order": {"payments.total_revenue": "desc"}}
3. [CRITICAL GUARDRAIL] If the user's question asks for metrics or dimensions NOT explicitly listed in the available data model above (e.g., asking for movie titles, store locations), DO NOT guess, approximate, or force a query. You MUST output exactly this JSON format:
{"error": "Sorry, the required data dimension or measure for your query is not available in the current semantic model."}
"""

st.title("🤖 DI-Lab Minimal Analytics Assistant")
st.markdown("Query DVD rental business data using natural language (Powered by Cube.dev)")

# User input field
user_query = st.text_input("What business data would you like to know? (e.g., Show total revenue by customer full name in descending order)")

if st.button("Start Analysis") and user_query:
    with st.spinner("AI is translating your intent into standard JSON..."):
        # ==========================================
        # Action 1: LLM translates natural language into JSON
        # ==========================================
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Clean up potential redundant symbols output by the LLM
        raw_json_str = response.choices[0].message.content.strip().strip("`").removeprefix("json")
        cube_query = json.loads(raw_json_str)
        if "error" in cube_query:
            st.error(f"⚠️ cannot query: {cube_query['error']}")
            st.stop()
        st.success("JSON generated successfully! (This is the API contract between AI and Cube)")
        st.json(cube_query)

    with st.spinner("Cube.dev is compiling SQL and querying the database..."):
        # ==========================================
        # Action 2: Send JSON to local Cube API
        # ==========================================
        cube_api_url = "http://localhost:4000/cubejs-api/v1/load"
        # In Cube's development mode, any non-empty token usually passes validation
        headers = {"Authorization": "Bearer test_token_123"} 
        
        cube_response = requests.get(
            cube_api_url, 
            headers=headers, 
            params={"query": json.dumps(cube_query)}
        )
        
        result_data = cube_response.json().get("data", [])
        
        if not result_data:
            st.warning("No data found, or Cube encountered an error.")
        else:
            # ==========================================
            # Action 3: Retrieve pure data and render frontend charts
            # ==========================================
            df = pd.DataFrame(result_data)
            
            st.markdown("### 📊 Final Data Result")
            # Render data table
            st.dataframe(df)
            
            # Attempt to render a bar/line chart if there are 2 or more columns
            if len(df.columns) >= 2:
                # 1. 尝试获取普通维度
                dimension_cols = [col for col in df.columns if col in cube_query.get("dimensions", [])]
                
                # 2. 尝试获取时间维度 (大模型在时间查询时会使用 timeDimensions)
                time_dimension_cols = []
                if "timeDimensions" in cube_query:
                    for td in cube_query["timeDimensions"]:
                        # Cube.dev 返回的数据列名通常是 "dimension_name.granularity"
                        # 例如: "payments.payment_date.month"
                        expected_col_prefix = td.get("dimension")
                        if expected_col_prefix:
                            time_dimension_cols.extend([col for col in df.columns if expected_col_prefix in col])

                # 3. 确定最终的 X 轴
                x_col = None
                if dimension_cols:
                    x_col = dimension_cols[0]
                elif time_dimension_cols:
                    x_col = time_dimension_cols[0]

                # 4. 确定 Y 轴
                y_col = [col for col in df.columns if col in cube_query.get("measures", [])]
                y_col = y_col[0] if y_col else None
                
                if x_col and y_col:
                    st.markdown("### 📈 Visualization Chart")
                    # 如果 X 轴包含 "date" 或 "time"，建议用折线图展示趋势
                    if "date" in x_col or "time" in x_col:
                        st.line_chart(df, x=x_col, y=y_col)
                    else:
                        st.bar_chart(df, x=x_col, y=y_col)
                else:
                    st.info("The data format is not suitable for automatic charting.")