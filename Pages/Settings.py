import streamlit as st
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('settings.db')

# Create cursor
c = conn.cursor()

# Create clients table
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        api_key TEXT NOT NULL,
        template_ids TEXT
    )
''')

# Create authors table
c.execute('''
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        image TEXT NOT NULL,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')

# Commit changes
conn.commit()

# Streamlit app
st.title("⚡️ Settings")

with st.form(key='settings_form'):
    st.subheader("Add/Edit Client")
    client_name = st.text_input('Client Name')
    api_key = st.text_input('API Key')
    template_ids = st.text_input('Template IDs (comma-separated)')
    submit_button_client = st.form_submit_button(label='Submit Client')

    st.subheader("Add/Edit Author")
    client_id = st.selectbox('Client ID', [client[0] for client in c.execute("SELECT id FROM clients")])
    author_name = st.text_input('Author Name')
    author_title = st.text_input('Author Title')
    author_image = st.text_input('Author Image URL')
    submit_button_author = st.form_submit_button(label='Submit Author')

if submit_button_client:
     # Insert or update client
    c.execute('''
        INSERT OR REPLACE INTO clients (name, api_key, template_ids)
        VALUES (?, ?, ?)
    ''', (client_name, api_key, template_ids))

    # Commit changes
    conn.commit()

if submit_button_author:
    # Insert or update author
    c.execute('''
        INSERT OR REPLACE INTO authors (client_id, name, title, image)
        VALUES (?, ?, ?, ?)
    ''', (client_id, author_name, author_title, author_image))

    # Commit changes
    conn.commit()

# Close connection
conn.close()

# Connect to SQLite database
conn = sqlite3.connect('settings.db')
c = conn.cursor()

# Fetch clients from the database
c.execute("SELECT * FROM clients")
client_rows = c.fetchall()

# Fetch authors from the database
c.execute("SELECT * FROM authors")
author_rows = c.fetchall()

# Close connection
conn.close()

# Convert client data to DataFrame
import pandas as pd
clients_df = pd.DataFrame(client_rows, columns=['id', 'name', 'api_key', 'template_ids'])

# Convert author data to DataFrame
authors_df = pd.DataFrame(author_rows, columns=['id', 'client_id', 'name', 'title', 'image'])

# Display and edit clients and authors
st.write("Clients:")
clients_df = st.data_editor(clients_df, key="Clients Editor", hide_index=True, num_rows="dynamic")

st.write("Authors:")
authors_df = st.data_editor(authors_df, key="Authors Editor", hide_index=True, num_rows="dynamic")

# Save changes back to the database
if st.button('Save Changes'):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()

    # Update clients
    clients_df.to_sql('clients', conn, if_exists='replace', index=False)

    # Update authors
    authors_df.to_sql('authors', conn, if_exists='replace', index=False)

    # Commit changes and close connection
    conn.commit()
    conn.close()