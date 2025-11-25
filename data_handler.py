import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

class DataHandler:
    def __init__(self):
        # Establish connection
        try:
            self.conn = st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            st.error(f"⚠️ Connection Error: Could not find 'gsheets' in secrets. Check your .toml file. Details: {e}")

    def load_data(self, worksheet_name):
        try:
            # Read data with no caching (ttl=0)
            df = self.conn.read(worksheet=worksheet_name, ttl="0")
            return df if not df.empty else pd.DataFrame()
        except Exception as e:
            # If the error is just "worksheet not found", return empty (that's fine)
            if "worksheet" in str(e).lower() or "not found" in str(e).lower():
                return pd.DataFrame()
            
            # SHOW REAL ERROR
            st.error(f"⚠️ Error loading '{worksheet_name}': {e}")
            return pd.DataFrame()

    def save_data(self, data, worksheet_name):
        try:
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            self.conn.update(worksheet=worksheet_name, data=df)
            return "Saved to Cloud"
        except Exception as e:
            st.error(f"⚠️ Error saving to '{worksheet_name}': {e}")
            return f"Error: {e}"
