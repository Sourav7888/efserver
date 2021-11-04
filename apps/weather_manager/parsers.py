from apps.shared.parsers import QuerysetParser
import datetime as dt
from apps.shared.processors import group_and_sum
import pandas as pd


class WeatherDataPr(QuerysetParser):
    @staticmethod
    def transform_df(df):
        """
        Process the dataframe as needed
        """

        if not df.empty:

            if "pk_id" in df.columns:
                df.drop(["pk_id"], inplace=True, axis=1)

            try:
                df["date"] = df["date"].apply(
                    lambda x: dt.datetime.combine(x, dt.time.min)
                )  # Converts date to datetime
            except TypeError:  # Weird error sometimes
                df["date"] = df["date"].apply(
                    lambda x: dt.datetime.strptime(x, "%Y-%m-%d")
                )  # Converts date to datetime
            except ValueError:
                pass

        return df

    def get_monthly_data(self) -> pd.DataFrame:
        """
        Returns a monthly data instead of daily
        """
        df = self.evaluate_queryset_to_df()
        df = group_and_sum(df, year=True, month=True, group_by="date")
        df.reset_index(inplace=True)
        return df
