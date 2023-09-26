import streamlit as st
import requests
import json
import time
import sqlite3

# Set default mode to wide
st.set_page_config(page_title="Quote Card Generator",layout="wide",initial_sidebar_state="expanded")

# Connect to SQLite database
conn = sqlite3.connect('settings.db')
c = conn.cursor()

# Create clients table
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY_KEY,
        name TEXT,
        api_key TEXT
        template_ids TEXT
    )
''')

# Create authors table
c.execute('''
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        name TEXT,
        title TEXT,
        image TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')

# Commit changes
conn.commit()

# Fetch clients from the database
c.execute("SELECT * FROM clients")
client_rows = c.fetchall()

# Fetch authors from the database
c.execute("SELECT * FROM authors")
author_rows = c.fetchall()

# Convert author data to dictionary
authors = {row[1]: {"name": row[2], "title": row[3], "image": row[4]} for row in author_rows}

# Convert client data to dictionary
clients = {row[1]: {"API_KEY": row[2], "TEMPLATE_IDS": row[3].split(','), "authors": authors} for row in client_rows}
# Close connection
conn.close()

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
    selected_author = st.selectbox("Select an author", [authors[key]["name"] for key in authors.keys()])

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