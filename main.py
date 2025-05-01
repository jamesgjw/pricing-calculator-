import streamlit as st

st.set_page_config(page_title="Pricing Calculator", layout="centered")

st.title("Twelve Labs - Pricing Calculator")

# === Sidebar Inputs ===
st.sidebar.header("Input Parameters")

model = st.sidebar.selectbox("Select Model", ["Marengo", "Pegasus"])
video_hours = st.sidebar.number_input("Video Hours", min_value=0.0, step=0.5)
generate_api_calls = st.sidebar.number_input("Generate API Calls", min_value=0, step=1)
input_tokens_per_call = st.sidebar.number_input("Input Tokens per Generate Call (only for Pegasus)", min_value=0, step=10)
output_tokens_per_call = st.sidebar.number_input("Output Tokens per Generate Call (only for Pegasus)", min_value=0, step=10)

# === Pricing Constants ===
index_cost_per_hour = 2.50
embedding_cost = {
    "video": 0.50,
    "audio": 0.01,
    "image": 0.05,
    "text": 0.01,
}
input_token_cost = 0.00 if model == "Pegasus" else None
output_token_cost = 0.00 if model == "Pegasus" else None
infra_fee_hourly = 0.003
storage_fee_hourly = 0.06

# === Calculations ===
indexing_cost = video_hours * index_cost_per_hour
embedding_cost_total = (
    video_hours * embedding_cost["video"] +
    video_hours * embedding_cost["audio"]
)

if model == "Pegasus":
    total_input_tokens = generate_api_calls * input_tokens_per_call
    total_output_tokens = generate_api_calls * output_tokens_per_call
    input_token_cost_total = (total_input_tokens / 1000) * input_token_cost
    output_token_cost_total = (total_output_tokens / 1000) * output_token_cost
else:
    input_token_cost_total = 0
    output_token_cost_total = 0

infra_cost_annual = video_hours * infra_fee_hourly * 24 * 30 * 12
storage_cost_annual = video_hours * storage_fee_hourly * 12

total_cost = (
    indexing_cost +
    embedding_cost_total +
    input_token_cost_total +
    output_token_cost_total +
    infra_cost_annual +
    storage_cost_annual
)

# === Output ===
st.header("Estimated First Year Cost")
st.markdown(f"**Model:** {model}")
st.markdown(f"- Indexing Cost: **${indexing_cost:,.2f}**")
st.markdown(f"- Embedding Cost: **${embedding_cost_total:,.2f}**")
if model == "Pegasus":
    st.markdown(f"- Generate Input Token Cost: **${input_token_cost_total:,.2f}**")
    st.markdown(f"- Generate Output Token Cost: **${output_token_cost_total:,.2f}**")
st.markdown(f"- Infrastructure Fee (Annual): **${infra_cost_annual:,.2f}**")
st.markdown(f"- Storage Fee (Annual): **${storage_cost_annual:,.2f}**")

st.success(f"**Total Estimated Cost (First Year): ${total_cost:,.2f}**")
