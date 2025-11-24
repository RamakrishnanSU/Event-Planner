import pandas as pd

class DataHandler:
    def save_to_csv(self, data, filename):
        """
        Saves a list of dictionaries or a single dictionary to a CSV file.
        Overwrites existing content by default.
        Returns a success message or an error message.
        """
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            df.to_csv(filename, mode='w', index=False)
            return f'Data saved to {filename}.'
        except Exception as e:
            return f'Error saving data: {e}'

    def load_from_csv(self, filename):
        """
        Loads data from a CSV file and returns it as a pandas DataFrame.
        Returns an empty DataFrame if file not found or error occurs.
        """
        try:
            df = pd.read_csv(filename)
            return df if not df.empty else pd.DataFrame()
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Returning empty DataFrame.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return pd.DataFrame()
