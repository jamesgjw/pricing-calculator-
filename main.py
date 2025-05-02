import streamlit as st
import pandas as pd

st.set_page_config(page_title="Model Pricing Calculator", layout="centered")

st.title("TwelveLabs - Estimate Pricing Calculator")
st.caption("For more accurate pricing and advanced usage, please contact our sales team.")

# === Default Pricing Constants ===
default_pricing = {
    "index_cost_per_hour": 2.500,
    "infra_storage_unit_price": 0.070,
    "search_cost_per_call": 0.001,
    "embedding_cost": {
        "video": 0.003,
        "audio": 0.010,
        "image": 0.050,
        "text": 0.010
    },
    "input_token_cost_marengo": 0.001,
    "input_token_cost_pegasus": 0.001,
    "output_token_cost_pegasus": 0.002
}

# === Sidebar: Usage Inputs ===
st.sidebar.image("marengo.png", use_container_width=True)
marengo_video_hours = st.sidebar.number_input("Marengo - Video Hours", min_value=0, step=100, value=10000, format="%d")
marengo_search_calls = st.sidebar.number_input("Marengo - Search API Calls", min_value=0, step=100, value=2000, format="%d")

st.sidebar.image("pegasus.png", use_container_width=True)
pegasus_video_hours = st.sidebar.number_input("Pegasus - Video Hours", min_value=0, step=100, value=10000, format="%d")
pegasus_generate_calls = st.sidebar.number_input("Pegasus - Generate API Calls", min_value=0, step=100, value=2000, format="%d")
pegasus_input_tokens_per_call = st.sidebar.number_input("Pegasus - Input Tokens per Call", min_value=0, step=1, value=50, format="%d")
pegasus_output_tokens_per_call = st.sidebar.number_input("Pegasus - Output Tokens per Call", min_value=0, step=1, value=14, format="%d")

st.sidebar.header("🔍 Embedding Inputs")

# Default value for video embeddings: 640 embeddings per hour
video_embeddings_default = marengo_video_hours * 640

video_embeddings = st.sidebar.number_input(
    "Video Embeddings", min_value=0, step=100, value=int(video_embeddings_default), format="%d"
)
audio_embeddings_1k = st.sidebar.number_input("Audio Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
image_embeddings_1k = st.sidebar.number_input("Image Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
text_embeddings_1k = st.sidebar.number_input("Text Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")

# === Main Section: Unit Pricing ===
with st.expander("📐 Adjust Unit Pricing (Advanced)"):
    pricing = {}
    pricing["index_cost_per_hour"] = st.number_input("Indexing ($/hr)", value=default_pricing["index_cost_per_hour"], format="%.3f")
    pricing["infra_storage_unit_price"] = st.number_input("Infra + Storage Fee ($/hr/mo)", value=default_pricing["infra_storage_unit_price"], format="%.3f")
    pricing["search_cost_per_call"] = st.number_input("Search API Call Cost ($/call)", value=default_pricing["search_cost_per_call"], format="%.3f")

    st.markdown("**Embedding Costs**")
    pricing["embedding_cost"] = {
        "video": st.number_input("Video Embedding ($/embedding)", value=default_pricing["embedding_cost"]["video"], format="%.3f"),
        "audio": st.number_input("Audio Embedding ($/1k)", value=default_pricing["embedding_cost"]["audio"], format="%.3f"),
        "image": st.number_input("Image Embedding ($/1k)", value=default_pricing["embedding_cost"]["image"], format="%.3f"),
        "text": st.number_input("Text Embedding ($/1k)", value=default_pricing["embedding_cost"]["text"], format="%.3f"),
    }

    pricing["input_token_cost_marengo"] = st.number_input("Marengo Input Tokens ($/1k)", value=default_pricing["input_token_cost_marengo"], format="%.3f")
    pricing["input_token_cost_pegasus"] = st.number_input("Pegasus Input Tokens ($/1k)", value=default_pricing["input_token_cost_pegasus"], format="%.3f")
    pricing["output_token_cost_pegasus"] = st.number_input("Pegasus Output Tokens ($/1k)", value=default_pricing["output_token_cost_pegasus"], format="%.3f")

# === Cost Calculation Functions ===
def calculate_model_cost(model, video_hours, generate_calls, input_tokens, output_tokens=0):
    indexing = video_hours * pricing["index_cost_per_hour"]
    input_token_cost = (generate_calls * 365 * input_tokens / 1000) * (
        pricing["input_token_cost_marengo"] if model == "Marengo" else pricing["input_token_cost_pegasus"]
    )
    output_token_cost = (generate_calls * 365 * output_tokens / 1000) * pricing["output_token_cost_pegasus"] if model == "Pegasus" else 0
    infra_storage = video_hours * pricing["infra_storage_unit_price"] * 12
    return indexing, input_token_cost, output_token_cost, infra_storage

def calculate_embedding_costs():
    return (
        video_embeddings * pricing["embedding_cost"]["video"] +
        audio_embeddings_1k * pricing["embedding_cost"]["audio"] / 1000 +
        image_embeddings_1k * pricing["embedding_cost"]["image"] / 1000 +
        text_embeddings_1k * pricing["embedding_cost"]["text"] / 1000
    )

# === Perform Calculations ===
mar_index, mar_input, mar_output, mar_infra = calculate_model_cost("Marengo", marengo_video_hours, marengo_search_calls, 0)
peg_index, peg_input, peg_output, peg_infra = calculate_model_cost("Pegasus", pegasus_video_hours, pegasus_generate_calls, pegasus_input_tokens_per_call, pegasus_output_tokens_per_call)
embedding_cost = calculate_embedding_costs()
search_cost = marengo_search_calls * pricing["search_cost_per_call"]

# === Assemble results ===
marengo = {
    "Indexing": mar_index,
    "Input Tokens": mar_input,  # Will be 0
    "Output Tokens": 0,
    "Embedding": embedding_cost,
    "Search": search_cost,
    "Infra + Storage": mar_infra,
}
marengo["Total"] = sum(marengo.values())

pegasus = {
    "Indexing": peg_index,
    "Input Tokens": peg_input,
    "Output Tokens": peg_output,
    "Embedding": 0,
    "Search": 0,
    "Infra + Storage": peg_infra,
}
pegasus["Total"] = sum(pegasus.values())

# === Display Results ===
results_df = pd.DataFrame({
    "Marengo": marengo,
    "Pegasus": pegasus
})
st.header("Cost Estimate Breakdown for First Year (USD)")
st.dataframe(results_df.style.format("${:,.0f}"))

grand_total = marengo["Total"] + pegasus["Total"]
st.markdown("---")
st.success(f"🎯 **Total Estimated First-Year Cost: ${grand_total:,.0f}**")
