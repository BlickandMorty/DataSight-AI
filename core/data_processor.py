import pandas as pd
def get_metadata(df):
    return {"columns": list(df.columns), "null_counts": df.isnull().sum().to_dict(), "head": df.head(3).to_dict()}
