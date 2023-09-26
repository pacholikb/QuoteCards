import streamlit as st
import requests
import json
import time

# Set default mode to wide
st.set_page_config(layout="wide")

# Add a new tab to the sidebar
tab = st.sidebar.selectbox("", ["Quote Card Generator", "Quote Ideas"])

if tab == "Quote Card Generator":
    # Hardcoded clients data
    clients = {
        "CEO.works": {
            "API_KEY": 'bb_pr_106b496ae486ce241a32e60cf1782b',
            "TEMPLATE_IDS": ['4KnlWBbK1wPW5OQGgm', 'wXmzGBDa10jxDLN7gj', '8BK3vWZJ2Jr6ZJzk1a'],
            "authors": {
                "Hein Knaapen": {"name": "Hein Knaapen", "title": "Partner, CEO.works Europe", "image": "https://www.ceoworks.com/hs-fs/hubfs/20230703_Hein_Color-1.png?width=290&name=20230703_Hein_Color-1.png"},
                "Sandy Ogg": {"name": "Sandy Ogg", "title": "Founder of CEO.works", "image": "https://www.ceoworks.com/hs-fs/hubfs/sandy%20RTC%2029%20copy.jpg?width=290&name=sandy%20RTC%2029%20copy.jpg"},
            }
        },
        "CLS": {
            "API_KEY": 'cls_api_key',  # Replace with actual API key
            "TEMPLATE_IDS": ['cls_template_id1', 'cls_template_id2', 'cls_template_id3'],  # Replace with actual template IDs
            "authors": {
                "Author1": {"name": "Author1", "title": "Title1", "image": "ImageURL1"},  # Replace with actual author data
                "Author2": {"name": "Author2", "title": "Title2", "image": "ImageURL2"},  # Replace with actual author data
            }
        },
        "Baseball.works": {
            "API_KEY": 'baseball_works_api_key',  # Replace with actual API key
            "TEMPLATE_IDS": ['baseball_works_template_id1', 'baseball_works_template_id2', 'baseball_works_template_id3'],  # Replace with actual template IDs
            "authors": {
                "Author1": {"name": "Author1", "title": "Title1", "image": "ImageURL1"},  # Replace with actual author data
                "Author2": {"name": "Author2", "title": "Title2", "image": "ImageURL2"},  # Replace with actual author data
            }
        },
        # Add more clients as needed
    }

    # Streamlit app
    st.title("⚡️ Quote Card Generator")
    st.divider()

    with st.expander("Enter Your Quote Card Settings", expanded=True):
        # User selects a client
        selected_client = st.selectbox("Select a Client", list(clients.keys()))

        # Get the API key, template IDs, and authors for the selected client
        API_KEY = clients[selected_client]["API_KEY"]
        TEMPLATE_IDS = clients[selected_client]["TEMPLATE_IDS"]
        authors = clients[selected_client]["authors"]

        # User selects an author
        selected_author = st.selectbox("Select an author", list(authors.keys()))

        # User enters a quote
        quote = st.text_input("Enter Quote Text (max 70 characters)", max_chars=70)
        # User enters a tweet
        tweet = st.text_area("Enter Tweet Text (max 130 characters)",  max_chars=130)    

        # User clicks the generate button
        if st.button("Generate"):
            modifications = [
                {"name": "avatar", "image_url": authors[selected_author]["image"]},
                {"name": "name", "text": authors[selected_author]["name"]},
                {"name": "subtitle", "text": authors[selected_author]["title"]},
                {"name": "quote_text", "text": quote},
                {"name": "tweet", "text": tweet},
                {"name": "full_name", "text": authors[selected_author]["name"]},
            ]

            image_ids = []
            for template_id in TEMPLATE_IDS:
                data = {
                    "template": template_id,
                    "modifications": modifications,
                }

                # Send a POST request to Bannerbear API
                response = requests.post(
                    'https://api.bannerbear.com/v2/images',
                    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
                    data=json.dumps(data)
                )

                # Check the response
                if response.status_code == 202:
                    # Get the image ID from the response and store it
                    image_ids.append(response.json()["uid"])
                else:
                    pass
                    
            # Create columns for the images
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]

            for idx, image_id in enumerate(image_ids):
                # Display toast indicating image generation started.
                st.toast(f"Image generation started for template {TEMPLATE_IDS[idx]}. Please wait for the image to be generated.")
                
                # Poll the Bannerbear API for the image status
                while True:
                    # Wait for a while before sending the next request
                    time.sleep(5)

                    # Send a GET request to the Bannerbear API
                    response = requests.get(
                        f'https://api.bannerbear.com/v2/images/{image_id}',
                        headers={'Authorization': f'Bearer {API_KEY}'}
                    )

                    # Check the image status
                    if response.json()["status"] == "completed":
                        # The image is ready, display it in the appropriate column
                        with cols[idx]:
                            st.image(response.json()["image_url"])
                            st.markdown(f'[Download]({response.json()["image_url"]})')
                        break
    pass
elif tab == "Quote Ideas":
    st.title("🧠 Quote Ideas")
    st.divider()
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
                "spellVersionId": "K-QC7zjtN8jRjhjsYmHw3",
                "inputs": {
                    "transcription": transcript,
                }
            }),
        )
        response_data = response.json()

        # Display the generated quotes
        st.markdown("### Generated Quotes")
        quote_ideas = response_data['outputs']['output'].split("\n")
        for i, quote in enumerate(quote_ideas):
            st.markdown(f"{quote}")

    