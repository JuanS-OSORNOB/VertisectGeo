import pandas as pd
import os

class Datahandler():
    def load_earthquake_data(path, filename):
        file_path = os.path.join(path, filename)
        try:
            data = pd.read_csv(file_path)
            required_columns = {"X", "Y", "Depth", 'Magnitude'}
            if not required_columns.issubset(data.columns):
                raise ValueError(f"Dataset must contain the columns: {required_columns}")
            return data
        except Exception as e:
            print(f"Error loading earthquake data: {e}")
            return pd.DataFrame()