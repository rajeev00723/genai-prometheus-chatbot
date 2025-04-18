import os
import subprocess
import requests
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from prompt_helper import build_prompt

# Load environment variables
load_dotenv()
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Function to generate PromQL query from user input
def ask_llm(user_input, model=OLLAMA_MODEL):
    prompt = build_prompt(user_input)

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )

    output = result.stdout.decode().strip()

    for line in output.splitlines():
        if any(line.startswith(prefix) for prefix in ["sum", "avg", "rate", "count", "histogram", "irate", "node_", "container_"]):
            return line.strip()
    return output

# Query Prometheus
def query_prometheus(promql):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {'query': promql}
    response = requests.get(url, params=params)
    return response.json()

# Streamlit UI
st.set_page_config(page_title="GenAI Prometheus Chatbot", page_icon="🧠")
st.title("🧠 GenAI + Prometheus Chatbot")

user_input = st.text_input("Ask a question (e.g., 'CPU usage last hour')")

if user_input:
    with st.spinner("Generating PromQL with Ollama..."):
        promql = ask_llm(user_input)
        st.code(promql, language="text")

        st.info("📡 Querying Prometheus...")
        result = query_prometheus(promql)

        if result.get("status") == "success":
            st.subheader("📊 Instant Query Result")
            result_type = result.get("data", {}).get("resultType", "")
            data = result.get("data", {}).get("result", [])

            if result_type == "scalar":
                ts, val = result["data"]["result"]
                readable_ts = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")
                st.write(f"📆 Time: `{readable_ts}`")
                st.write(f"📈 Value: `{val}`")

            elif result_type == "vector":
                if not data:
                    st.info("✅ Query ran successfully but returned no data.")
                else:
                    for r in data:
                        metric = r.get("metric", {})
                        value = r.get("value", [])
                        if len(value) == 2:
                            ts, val = value
                            readable_ts = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")
                            metric_str = ", ".join(f"{k}={v}" for k, v in metric.items()) if metric else "(no labels)"
                            st.write(f"📌 Metric: `{metric_str}`")
                            st.write(f"📆 Time: `{readable_ts}`")
                            st.write(f"📈 Value: `{val}`")
                        else:
                            st.warning(f"Unexpected data format: {r}")
            else:
                st.warning(f"Unexpected result type: {result_type}")
        else:
            st.error("❌ Error fetching data from Prometheus.")
