import pandas as pd


def calculate_col_avg(df: pd.DataFrame, col_name: str) -> float:
    """
    Calculate the average of a column
    """
    return df[col_name].mean().item()
