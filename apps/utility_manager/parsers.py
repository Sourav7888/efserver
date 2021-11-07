from apps.shared.parsers import QuerysetParser
import pandas as pd
from datetime import datetime as dt


class UtilityBillPr(QuerysetParser):
    """
    Queryset parser used for utility bill
    """

    @staticmethod
    def transform_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Object specific transformation to apply to the dataframe
        """
        if not df.empty:
            if "id" in df.columns:
                df.drop("id", axis=1, inplace=True)

            try:
                df["billing_date"] = df["billing_date"].apply(
                    lambda x: dt.strptime(str(x), "%Y-%m-%d")
                )
                df["cost"] = pd.to_numeric(df["cost"])
                df["usage"] = pd.to_numeric(df["usage"])

            except (ValueError, KeyError) as error:
                df = pd.DataFrame([])

        return df
