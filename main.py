import streamlit as st

st.set_page_config(page_title="Dual Model Pricing Calculator", layout="centered")
st.title("Twelve Labs - Pricing Calculator")

st.markdown("Estimate **first-year cost** using both **Marengo** and **Pegasus** models.")

# === Pricing Constants ===
PRICING = {
    "index_cost_per_hour": 2.50,
    "embedding": {
        "video": 0.50,
        "audio": 0.01,
        "image": 0.05,
        "text": 0.01
    },
    "input_token_cost": 0.00,   # Pegasus only
    "output_token_cost": 0.00,  # Pegasus only
    "infra_fee_hourly": 0.003,
    "storage_fee_hourly": 0.06
}

# === Inputs for Marengo ===
st.sidebar.header("📦 Marengo Usage")
marengo_video_hours = st.sidebar.number_input("Marengo - Video Hours", min_value=0.0, step=0.5)
marengo_generate_calls = st.sidebar.number_input("Marengo - Generate API Calls", min_value=0, step=1)

# === Inputs for Pegasus ===
st.sidebar.header("🦅 Pegasus Usage")
pegasus_video_hours = st.sidebar.number_input("Pegasus - Video Hours", min_value=0.0, step=0.5)
pegasus_generate_calls = st.sidebar.number_input("Pegasus - Generate API Calls", min_value=0, step=1)
input_tokens_per_call = st.sidebar.number_input("Pegasus - Input Tokens per Call", min_value=0, step=10)
output_tokens_per_call = st.sidebar.number_input("Pegasus - Output Tokens per Call", min_value=0, step=10)


def calculate_cost(model, video_hours, generate_calls, input_tokens=0, output_tokens=0):
    indexing = video_hours * PRICING["index_cost_per_hour"]
    embedding = video_hours * (PRICING["embedding"]["video"] + PRICING["embedding"]["audio"])
    infra = video_hours * PRICING["infra_fee_hourly"] * 24 * 30 * 12
    storage = video_hours * PRICING["storage_fee_hourly"] * 12

    if model == "Pegasus":
        total_input_tokens = generate_calls * input_tokens
        total_output_tokens = generate_calls * output_tokens
        input_cost = (total_input_tokens / 1000) * PRICING["input_token_cost"]
        output_cost = (total_output_tokens / 1000) * PRICING["output_token_cost"]
    else:
        input_cost = 0
        output_cost = 0

    total = indexing + embedding + infra + storage + input_cost + output_cost

    return {
        "Indexing": indexing,
        "Embedding": embedding,
        "Infra": infra,
        "Storage": storage,
        "Input Token": input_cost,
        "Output Token": output_cost,
        "Total": total
    }


# === Cost Calculations ===
marengo_cost = calculate_cost("Marengo", marengo_video_hours, marengo_generate_calls)
pegasus_cost = calculate_cost("Pegasus", pegasus_video_hours, pegasus_generate_calls, input_tokens_per_call, output_tokens_per_call)
grand_total = marengo_cost["Total"] + pegasus_cost["Total"]

# === Output ===
st.header("💰 Cost Breakdown")

st.subheader("📦 Marengo")
for k, v in marengo_cost.items():
    if v > 0:
        st.markdown(f"- {k} Cost: **${v:,.2f}**")

st.subheader("🦅 Pegasus")
for k, v in pegasus_cost.items():
    if v > 0:
        st.markdown(f"- {k} Cost: **${v:,.2f}**")

st.markdown("---")
st.success(f"🎯 **Total Estimated First-Year Cost: ${grand_total:,.2f}**")
