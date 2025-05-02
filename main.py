import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dual Model Pricing Calculator", layout="centered")
st.title("Twelve Labs - Pricing Calculator")

# === Pricing Constants ===
PRICING = {
    "index_cost_per_hour": 2.50,
    "embedding_cost": {
        "video": 0.003,      # per embedding
        "audio": 0.01,       # per 1k embeddings
        "image": 0.05,       # per 1k embeddings
        "text": 0.01         # per 1k embeddings
    },
    "input_token_cost_marengo": 0.001,  # per 1k tokens
    "input_token_cost_pegasus": 0.001,
    "output_token_cost_pegasus": 0.002,
    "monthly_infra_fee_per_video_hour": 0.003,
    "monthly_storage_fee_per_video_hour": 0.06
}

# === Sidebar Inputs ===
st.sidebar.header("📦 Marengo Usage")
marengo_video_hours = st.sidebar.number_input("Marengo - Video Hours", min_value=0, step=1, value=10000)
marengo_generate_calls = st.sidebar.number_input("Marengo - Search API Calls", min_value=0, step=1, value=2000)
marengo_input_tokens_per_call = st.sidebar.number_input("Marengo - Input Tokens per Call", min_value=0, step=1, value=50)

st.sidebar.header("🦅 Pegasus Usage")
pegasus_video_hours = st.sidebar.number_input("Pegasus - Video Hours", min_value=0, step=1, value=10000)
pegasus_generate_calls = st.sidebar.number_input("Pegasus - Generate API Calls", min_value=0, step=1, value=2000)
pegasus_input_tokens_per_call = st.sidebar.number_input("Pegasus - Input Tokens per Call", min_value=0, step=1, value=50)
pegasus_output_tokens_per_call = st.sidebar.number_input("Pegasus - Output Tokens per Call", min_value=0, step=1, value=14)

st.sidebar.header("🔍 Embedding Inputs (Shared)")
video_embeddings = st.sidebar.number_input("Video Embeddings", min_value=0, step=1, value=0)
audio_embeddings_1k = st.sidebar.number_input("Audio Embeddings (per 1k)", min_value=0, step=1, value=0)
image_embeddings_1k = st.sidebar.number_input("Image Embeddings (per 1k)", min_value=0, step=1, value=0)
text_embeddings_1k = st.sidebar.number_input("Text Embeddings (per 1k)", min_value=0, step=1, value=0)

# === Cost Calculation Functions ===

def calculate_model_cost(model, video_hours, generate_calls, input_tokens, output_tokens=0):
    index = video_hours * PRICING["index_cost_per_hour"]
    infra = video_hours * PRICING["monthly_infra_fee_per_video_hour"] * 12
    storage = video_hours * PRICING["monthly_storage_fee_per_video_hour"] * 12

    if model == "Marengo":
        input_token_cost = (generate_calls * input_tokens / 1000) * PRICING["input_token_cost_marengo"]
        output_token_cost = 0
    else:  # Pegasus
        input_token_cost = (generate_calls * input_tokens / 1000) * PRICING["input_token_cost_pegasus"]
        output_token_cost = (generate_calls * output_tokens / 1000) * PRICING["output_token_cost_pegasus"]

    total = index + infra + storage + input_token_cost + output_token_cost
    return {
        "Indexing": index,
        "Embedding": 0,  # Added below for Marengo only
        "Infra": infra,
        "Storage": storage,
        "Input Tokens": input_token_cost,
        "Output Tokens": output_token_cost,
        "Total": total  # total will be adjusted for Marengo after embedding
    }

def calculate_embedding_costs():
    return (
        video_embeddings * PRICING["embedding_cost"]["video"] +
        audio_embeddings_1k * PRICING["embedding_cost"]["audio"] +
        image_embeddings_1k * PRICING["embedding_cost"]["image"] +
        text_embeddings_1k * PRICING["embedding_cost"]["text"]
    )

# === Calculations ===
marengo = calculate_model_cost("Marengo", marengo_video_hours, marengo_generate_calls, marengo_input_tokens_per_call)
pegasus = calculate_model_cost("Pegasus", pegasus_video_hours, pegasus_generate_calls, pegasus_input_tokens_per_call, pegasus_output_tokens_per_call)

embedding_cost = calculate_embedding_costs()
marengo["Embedding"] = embedding_cost
marengo["Total"] += embedding_cost

# === Results Table ===
results_df = pd.DataFrame({
    "Marengo": marengo,
    "Pegasus": pegasus
})

# === Display Results ===
st.header("💰 Cost Breakdown Table (USD)")
st.dataframe(results_df.style.format("${:,.0f}"))

grand_total = marengo["Total"] + pegasus["Total"]
st.markdown("---")
st.success(f"🎯 **Total Estimated First-Year Cost: ${grand_total:,.0f}**")
