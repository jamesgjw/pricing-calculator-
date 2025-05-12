import streamlit as st
import pandas as pd

st.set_page_config(page_title="Model Pricing Calculator", layout="centered")

st.title("TwelveLabs - Estimate Pricing Calculator")
st.caption("For more accurate pricing and advanced usage, please contact the finance team.")

# Default Pricing
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
    "output_token_cost_pegasus": 0.002,
    "reindex_price_marengo": 2.5,
    "reindex_price_pegasus": 2.5
}

# Sidebar Inputs
st.sidebar.image("marengo.png", use_container_width=True)
marengo_video_hours = st.sidebar.number_input("Marengo - Video Hours", min_value=0, step=100, value=10000, format="%d")
marengo_search_calls = st.sidebar.number_input("Marengo - Daily Search API Calls", min_value=0, step=100, value=2000, format="%d")

st.sidebar.image("pegasus.png", use_container_width=True)
pegasus_video_hours = st.sidebar.number_input("Pegasus - Video Hours", min_value=0, step=100, value=10000, format="%d")
pegasus_generate_calls = st.sidebar.number_input("Pegasus - Daily Generate API Calls", min_value=0, step=100, value=2000, format="%d")
pegasus_input_tokens_per_call = st.sidebar.number_input("Pegasus - Input Tokens per Call", min_value=0, step=1, value=500, format="%d")
pegasus_output_tokens_per_call = st.sidebar.number_input("Pegasus - Output Tokens per Call", min_value=0, step=1, value=200, format="%d")

# Contract Inputs
st.sidebar.header("Contract Setting")
contract_years = st.sidebar.number_input("Number of Contract Years", min_value=1, step=1, value=1, format="%d")
reindex_frequency = st.sidebar.number_input(
    "Reindex Frequency (per year)", 
    min_value=0, step=1, value=0, format="%d",
    help="Number of times the video is expected to be reindexed each year. "
         "Note: In the first year, initial indexing is already included. "
         "So if the contract is 1 year and frequency is set to 1, no reindex cost or additional embedding is charged."
)
enterprise_discount = st.sidebar.number_input("Enterprise Discount (0-1)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)

# Embedding Inputs
st.sidebar.header("🔍 Embedding Inputs")
video_embeddings_default = marengo_video_hours * 640
video_embeddings = st.sidebar.number_input("Video Embeddings", min_value=0, step=100, value=int(video_embeddings_default), format="%d")
audio_embeddings_1k = st.sidebar.number_input("Audio Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
image_embeddings_1k = st.sidebar.number_input("Image Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")
text_embeddings_1k = st.sidebar.number_input("Text Embeddings (per 1k)", min_value=0, step=100, value=0, format="%d")

# Pricing Panel
with st.expander("📐 Adjust Unit Pricing (Advanced)"):
    pricing = {}
    pricing["index_cost_per_hour"] = st.number_input("Indexing ($/hr)", value=default_pricing["index_cost_per_hour"], format="%.3f")
    pricing["infra_storage_unit_price"] = st.number_input("Infra + Storage Fee ($/hr/mo)", value=default_pricing["infra_storage_unit_price"], format="%.3f")
    pricing["search_cost_per_call"] = st.number_input("Search API Call Cost ($/call)", value=default_pricing["search_cost_per_call"], format="%.3f")
    pricing["reindex_price_marengo"] = st.number_input("Reindex Price Marengo ($/hr)", value=default_pricing["reindex_price_marengo"], format="%.3f")
    pricing["reindex_price_pegasus"] = st.number_input("Reindex Price Pegasus ($/hr)", value=default_pricing["reindex_price_pegasus"], format="%.3f")

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

# Helper for Embedding Costs
def calculate_embedding_costs(times=1):
    return times * (
        video_embeddings * pricing["embedding_cost"]["video"] +
        audio_embeddings_1k * pricing["embedding_cost"]["audio"] / 1000 +
        image_embeddings_1k * pricing["embedding_cost"]["image"] / 1000 +
        text_embeddings_1k * pricing["embedding_cost"]["text"] / 1000
    )

# Yearly Breakdown
total_cost = 0
for year in range(1, contract_years + 1):
    is_first_year = year == 1
    mar_reindex_times = max(0, reindex_frequency - 1) if is_first_year else reindex_frequency
    peg_reindex_times = max(0, reindex_frequency - 1) if is_first_year else reindex_frequency
    embedding_times = 1 + mar_reindex_times if is_first_year else reindex_frequency

    mar_index = marengo_video_hours * pricing["index_cost_per_hour"] if is_first_year else 0
    peg_index = pegasus_video_hours * pricing["index_cost_per_hour"] if is_first_year else 0

    mar_reindex = marengo_video_hours * pricing["reindex_price_marengo"] * mar_reindex_times
    peg_reindex = pegasus_video_hours * pricing["reindex_price_pegasus"] * peg_reindex_times

    peg_input = (pegasus_generate_calls * 365 * pegasus_input_tokens_per_call / 1000) * pricing["input_token_cost_pegasus"]
    peg_output = (pegasus_generate_calls * 365 * pegasus_output_tokens_per_call / 1000) * pricing["output_token_cost_pegasus"]
    mar_input = 0
    mar_output = 0

    mar_infra = marengo_video_hours * pricing["infra_storage_unit_price"] * 12
    peg_infra = pegasus_video_hours * pricing["infra_storage_unit_price"] * 12
    search_cost = marengo_search_calls * pricing["search_cost_per_call"] * 365
    embedding_cost = calculate_embedding_costs(times=embedding_times)

    marengo = {
        "Indexing": mar_index,
        "Reindexing": mar_reindex,
        "Input Tokens": mar_input,
        "Output Tokens": mar_output,
        "Embedding": embedding_cost,
        "Search": search_cost,
        "Infra + Storage": mar_infra,
    }
    marengo["Total"] = sum(marengo.values())

    pegasus = {
        "Indexing": peg_index,
        "Reindexing": peg_reindex,
        "Input Tokens": peg_input,
        "Output Tokens": peg_output,
        "Embedding": 0,
        "Search": 0,
        "Infra + Storage": peg_infra,
    }
    pegasus["Total"] = sum(pegasus.values())

    df = pd.DataFrame({"Marengo": marengo, "Pegasus": pegasus})
    st.header(f"📊 Cost Breakdown for Year {year}")
    st.dataframe(df.style.format("${:,.0f}"))

    total_cost += marengo["Total"] + pegasus["Total"]

# Final Total
final_price = total_cost * (1 - enterprise_discount)
st.markdown("---")
if enterprise_discount > 0:
    discount_pct = int(enterprise_discount * 100)
    discount_amount = total_cost * enterprise_discount

    st.markdown(f"""
    <div style='line-height: 1.8; font-size: 16px'>
        🎯 <b>Total Estimated {contract_years}-Year Cost (before discount):</b> ${total_cost:,.0f}<br>
        💸 <b>Enterprise Discount ({discount_pct}%):</b> -${discount_amount:,.0f}
    </div>
    """, unsafe_allow_html=True)

    st.success(f"✅ Final Cost After Discount: ${final_price:,.0f}")
else:
    st.success(f"🎯 Total Estimated {contract_years}-Year Cost: ${final_price:,.0f}")



