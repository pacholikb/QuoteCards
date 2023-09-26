import streamlit as st
import requests
import json


st.title("🧠 Quote Ideas")
st.divider()

with st.expander("AI Instructions"):
    instruction = st.text_area("Enter your instructions below:", value="Your goal is to take the transcript in the prompt which is an interview, find the best most quotable sections that would be insightful and helpful to a reader and would also work well as quote cards for social media. Emphasis on key insights or shocking or thought provoking things. Return a total of 6 quotes; 3 quotes 0-70 characters and 3 quotes under 70-130 characters. They can be overlapping.")

# User pastes in a transcript
transcript = st.text_area("Paste in a transcript")

if st.button("Generate Quote Ideas"):
    # Call the third-party API to get quote suggestions
    response = requests.post(
        "https://api.respell.ai/v1/run",
        headers={
            "Authorization": "Bearer e2a07e9e-fba2-4a41-8ef3-85264bcb58e9",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "spellId": "WxhpU83h3lfUul3XgNbJ1",
            "spellVersionId": "SnB8Qh1ZmOpsS5QFVIf_m",
            "inputs": {
                "transcription": transcript,
                "instructions": instruction,
            }
        }),
    )
    response_data = response.json()

    # Display the generated quotes
    st.markdown("### Generated Quotes")
    quote_ideas = response_data['outputs']['output'].split("\n")
    for i, quote in enumerate(quote_ideas):
        st.markdown(f"{quote}")
