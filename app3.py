import streamlit as st
import pandas as pd
import ollama

st.set_page_config(
    page_title="EcoLedger AI",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 EcoLedger AI")
st.subheader("Carbon Footprint Reporting for Small Businesses")

st.write(
    "Calculate emissions, analyse business activities, "
    "and receive AI-powered sustainability suggestions."
)

st.info(
    "Demo mode: The default emission factors below are "
    "illustrative, not verified reporting factors."
)

st.sidebar.header("Business Information")

business = st.sidebar.text_input(
    "Business Name",
    "My Small Business"
)

period = st.sidebar.selectbox(
    "Reporting Period",
    ["Monthly", "Quarterly", "Yearly"]
)

st.header("1. Enter Activity Data")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Electricity")

    electricity = st.number_input(
        "Electricity consumption (kWh)",
        min_value=0.0,
        value=500.0
    )

    electricity_factor = st.number_input(
        "Electricity factor (kg CO2e/kWh)",
        min_value=0.0,
        value=0.70
    )

with col2:
    st.subheader("⛽ Diesel")

    diesel = st.number_input(
        "Diesel consumption (litres)",
        min_value=0.0,
        value=50.0
    )

    diesel_factor = st.number_input(
        "Diesel factor (kg CO2e/litre)",
        min_value=0.0,
        value=2.68
    )

st.caption(
    "Replace the illustrative factors with documented, "
    "appropriate emission factors before real reporting."
)

if st.button("Calculate Carbon Footprint", type="primary"):

    electricity_emissions = electricity * electricity_factor
    diesel_emissions = diesel * diesel_factor

    total = electricity_emissions + diesel_emissions

    st.header("2. Carbon Footprint Results")

    st.write(f"**Business:** {business}")
    st.write(f"**Reporting period:** {period}")

    a, b, c = st.columns(3)

    a.metric(
        "Electricity Emissions",
        f"{electricity_emissions:.2f} kg CO2e"
    )

    b.metric(
        "Diesel Emissions",
        f"{diesel_emissions:.2f} kg CO2e"
    )

    c.metric(
        "Total Emissions",
        f"{total:.2f} kg CO2e"
    )

    results = pd.DataFrame({
        "Activity": ["Electricity", "Diesel"],
        "Consumption": [electricity, diesel],
        "Emissions (kg CO2e)": [
            electricity_emissions,
            diesel_emissions
        ]
    })

    st.subheader("3. Emissions Breakdown")

    st.bar_chart(
        results.set_index("Activity")["Emissions (kg CO2e)"]
    )

    st.dataframe(results, use_container_width=True)

    st.download_button(
        "Download Carbon Report (CSV)",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="ecoledger_report.csv",
        mime="text/csv"
    )

    st.session_state["carbon_context"] = (
        f"Business: {business}\n"
        f"Period: {period}\n"
        f"Electricity: {electricity} kWh\n"
        f"Electricity emissions: {electricity_emissions:.2f} kg CO2e\n"
        f"Diesel: {diesel} litres\n"
        f"Diesel emissions: {diesel_emissions:.2f} kg CO2e\n"
        f"Total: {total:.2f} kg CO2e\n"
        "Emission factors are illustrative unless verified."
    )

st.divider()

st.header("4. Ask EcoLedger AI")

question = st.text_input(
    "Ask a sustainability question",
    placeholder="How can I reduce my business emissions?"
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        context = st.session_state.get(
            "carbon_context",
            "No calculation has been performed yet."
        )

        try:
            with st.spinner("AI is analysing your question..."):

                response = ollama.chat(
                    model="qwen2.5:3b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are EcoLedger AI, an assistant "
                                "for small-business carbon reporting. "
                                "Explain calculations and suggest "
                                "practical emission-reduction actions. "
                                "Never invent verified emission factors "
                                "or claim that estimates are official."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Business data:\n{context}\n\n"
                                f"Question: {question}"
                            )
                        }
                    ]
                )

            st.subheader("AI Recommendation")
            st.write(response["message"]["content"])

        except Exception as error:
            st.error(
                "Cannot connect to Ollama. Check that Ollama "
                "is running and qwen2.5:3b is installed."
            )
            st.code(str(error))

st.divider()

st.caption(
    "EcoLedger AI | Hackathon Prototype | "
    "Verify activity data and emission factors before reporting."
)

if "eco_chat_history" not in st.session_state:
    st.session_state.eco_chat_history = []

# Display previous messages
for message in st.session_state.eco_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new question
prompt = st.chat_input(
    "Ask about carbon emissions..."
)

if prompt:
    st.session_state.eco_chat_history.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [
        {
            "role": "system",
            "content": (
                "You are EcoLedger AI, a sustainability assistant "
                "for small businesses. Explain carbon footprints, "
                "emissions calculations, energy efficiency, and "
                "sustainable business practices in simple language. "
                "Do not invent official emission factors or claim "
                "that estimates are verified measurements. "
                "Clearly explain uncertainty when necessary."
            )
        }
    ]

    messages.extend(
        st.session_state.eco_chat_history[-10:]
    )

    try:
        with st.chat_message("assistant"):
            with st.spinner("EcoLedger AI is thinking..."):
                response = ollama.chat(
                    model="qwen2.5:3b",
                    messages=messages
                )

                answer = response.message.content
                st.markdown(answer)

        st.session_state.eco_chat_history.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as error:
        st.error(
            "Could not connect to Ollama. "
            "Check that Ollama is running and "
            "qwen2.5:3b is installed."
        )
        st.code(str(error))
        