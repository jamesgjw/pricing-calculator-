import streamlit as st
import pandas as pd

st.set_page_config(page_title="Model Pricing Calculator", layout="centered")

st.title("TwelveLabs - Estimate Pricing Calculator")
st.caption("For more accurate pricing and advanced usage, please contact our sales team.")

# === Default Pricing Constants ===
default_pricing = {
    "index_cost_per_hour": 2.50,
    "embedding_cost": {
        "video": 0.003,
        "audio": 0.01,
        "image": 0.05,
        "text": 0.01
    },
    "input_token_cost_marengo": 0.001,
    "input_token_cost_pegasus": 0.001,
    "output_token_cost_pegasus": 0.002,
    "monthly_infra_fee_per_video_hour": 0.003,
    "monthly_storage_fee_per_video_hour": 0.06,
    "search_cost_per_call": 0.001
}

# === Sidebar: Adjustable Unit Pricing ===
st.sidebar.header("🧮 Unit Pricing Settings")
pricing = {}
pricing["index_cost_per_hour"] = st.sidebar.number_input("Indexing ($/hr)", value=default_pricing["index_cost_per_hour"])
pricing["monthly_infra_fee_per_video_hour"] = st.sidebar.number_input("Infra Fee ($/hr/mo)", value=default_pricing["monthly_infra_fee_per_video_hour"])
pricing["monthly_storage_fee_per_video_hour"] = st.sidebar.number_input("Storage Fee ($/hr/mo)", value=default_pricing["monthly_storage_fee_per_video_hour"])
pricing["search_cost_per_call"] = st.sidebar.number_input("Search API Call Cost ($/call)", value=default_pricing["search_cost_per_call"])

st.sidebar.markdown("**Embedding Costs**")
pricing["embedding_cost"] = {
    "video": st.sidebar.number_input("Video Embedding ($/embedding)", value=default_pricing["embedding_cost"]["video"]),
    "audio": st.sidebar.number_input("Audio Embedding ($/1k)", value=default_pricing["embedding_cost"]["audio"]),
    "image": st.sidebar.number_input("Image Embedding ($/1k)", value=default_pricing["embedding_cost"]["image"]),
    "text": st.sidebar.number_input("Text Embedding ($/1k)", value=default_pricing["embedding_cost"]["text"]),
}

pricing["input_token_cost_marengo"] = st.sidebar.number_input("Marengo Input Tokens ($/1k)", value=default_pricing["input_token_cost_marengo"])
pricing["input_token_cost_pegasus"] = st.sidebar.number_input("Pegasus Input Tokens ($/1k)", value=default_pricing["input_token_cost_pegasus"])
pricing["output_token_cost_pegasus"] = st.sidebar.number_input("Pegasus Output Tokens ($/1k)", value=default_pricing["output_token_cost_pegasus"])

# === Usage Inputs ===
st.sidebar.image("marengo.png", use_container_width=True)
marengo_video_hours = st.sidebar.number_input("Marengo - Video Hours", min_value=0, step=100, value=10000, format="%d")
marengo_search_calls = st.sidebar.number_input("Marengo - Search API Calls", min_value=0, step=100, value=2000, format="%d")

marengo_input_tokens_per_call = st.sidebar.number_input("Marengo - Input Tokens per Call", min_value=0, step=1, value=50, format="%d")

st.sidebar.image("pegasus.png", use_container_width=True)
pegasus_video_hours = st.sidebar.number_input("Pegasus - Video Hours", min_value=0, step=100, value=10000, format="%d")
pegasus_generate_calls = st.sidebar.number_input("Pegasus - Generate API Calls", min_value=0, step=100, value=2000, format="%d")
pegasus_input_tokens_per_call = st.sidebar.number_input("Pegasus - Input Tokens per Call", min_value=0, step=1, value=50, format="%d")
pegasus_output_tokens_per_call = st.sidebar.number_input("Pegasus - Output Tokens per Call", min_value=0, step=1, value=14, format="%d")

st.sidebar.header("🔍 Embedding Inputs")
video_embeddings = st.sidebar.number_input("Video Embeddings", min_value=0, step=100, value=0, format="%d")
audio_embeddings_1k = st.sidebar.number_input("Audio Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
image_embeddings_1k = st.sidebar.number_input("Image Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
text_embeddings_1k = st.sidebar.number_input("Text Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")

# === Calculations ===
def calculate_model_cost(model, video_hours, generate_calls, input_tokens, output_tokens=0):
    indexing = video_hours * pricing["index_cost_per_hour"]
    input_token_cost = (generate_calls * 365 * input_tokens / 1000) * (
        pricing["input_token_cost_marengo"] if model == "Marengo" else pricing["input_token_cost_pegasus"]
    )
    output_token_cost = (generate_calls * 365 * output_tokens / 1000) * pricing["output_token_cost_pegasus"] if model == "Pegasus" else 0

    return {
        "Indexing": indexing,
        "Input Tokens": input_token_cost,
        "Output Tokens": output_token_cost,
    }

def calculate_embedding_costs():
    return (
        video_embeddings * pricing["embedding_cost"]["video"] +
        audio_embeddings_1k * pricing["embedding_cost"]["audio"] / 1000 +
        image_embeddings_1k * pricing["embedding_cost"]["image"] / 1000 +
        text_embeddings_1k * pricing["embedding_cost"]["text"] / 1000
    )

# Calculate model-specific costs
marengo = calculate_model_cost("Marengo", marengo_video_hours, marengo_search_calls, marengo_input_tokens_per_call)
pegasus = calculate_model_cost("Pegasus", pegasus_video_hours, pegasus_generate_calls, pegasus_input_tokens_per_call, pegasus_output_tokens_per_call)

# Calculate shared infra+storage (charged once across models)
total_video_hours = max(marengo_video_hours, pegasus_video_hours)
infra_storage = total_video_hours * (pricing["monthly_infra_fee_per_video_hour"] + pricing["monthly_storage_fee_per_video_hour"]) * 12

# Calculate embedding cost (added under Marengo)
embedding_cost = calculate_embedding_costs()
marengo["Embedding"] = embedding_cost

# Search API cost (based on Marengo search calls only)
search_cost = marengo_search_calls * pricing["search_cost_per_call"]

# Build final display table
marengo["Search"] = search_cost
pegasus["Search"] = 0
marengo["Infra + Storage"] = infra_storage
pegasus["Infra + Storage"] = 0

marengo["Total"] = sum(marengo.values())
pegasus["Total"] = sum(pegasus.values())

# Final table and display
results_df = pd.DataFrame({
    "Marengo": marengo,
    "Pegasus": pegasus
})

st.header("📊 Cost Estimate Breakdown for First Year (USD)")
st.dataframe(results_df.style.format("${:,.0f}"))

grand_total = marengo["Total"] + pegasus["Total"]
st.markdown("---")
st.success(f"🎯 **Total Estimated First-Year Cost: ${grand_total:,.0f}**")
