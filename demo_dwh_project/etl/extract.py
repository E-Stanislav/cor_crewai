import pandas as pd

def extract_data(source_path: str) -> pd.DataFrame:
    """Extract data from source."""
    data = pd.read_csv(source_path)
    return data
