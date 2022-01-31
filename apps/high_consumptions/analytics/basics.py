import pandas as pd


def calculate_col_avg(df: pd.DataFrame, col_name: str) -> float:
    """
    Calculate the average of a column
    """
    try:
        return df[col_name].mean().item()
    # @NOTE: Fails when a float object is present and not array
    except AttributeError:
        return df[col_name].mean()
