import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

class DataHandler:
    def __init__(self):
        # Establish connection to Google Sheets
        # We use st.error to show if the secrets are missing
        try:
            self.conn = st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            st.error(f"⚠️ Connection Error: Could not find 'gsheets' in secrets. Check your .toml file. Details: {e}")

    def load_data(self, worksheet_name):
        """Loads a specific worksheet into a DataFrame"""
        try:
            # ttl=0 ensures we get fresh data every time (no caching)
            df = self.conn.read(worksheet=worksheet_name, ttl="0")
            return df if not df.empty else pd.DataFrame()
        except Exception as e:
            # If the sheet is empty or doesn't exist yet, return empty dataframe
            return pd.DataFrame()

    def save_data(self, data, worksheet_name):
        """Overwrites a worksheet with new data"""
        try:
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            self.conn.update(worksheet=worksheet_name, data=df)
            return "Saved to Cloud"
        except Exception as e:
            return f"Error saving: {e}"
