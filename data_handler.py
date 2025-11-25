import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

class DataHandler:
    def __init__(self):
        # Establish connection to Google Sheets
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    def load_data(self, worksheet_name):
        """Loads a specific worksheet into a DataFrame"""
        try:
            # Read data, focusing on the specific worksheet
            # ttl=0 means "don't cache", always get fresh data
            df = self.conn.read(worksheet=worksheet_name, ttl="0") 
            return df if not df.empty else pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    def save_data(self, data, worksheet_name):
        """Overwrites a worksheet with new data"""
        try:
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            self.conn.update(worksheet=worksheet_name, data=df)
            return "Saved to Cloud"
        except Exception as e:
            return f"Error saving: {e}"
