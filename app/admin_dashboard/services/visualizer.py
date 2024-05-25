import pandas as pd
import plotly.express as px
from pandas.core.series import Series
from plotly.offline import plot


class PlotlyVisualizer:
    """Data Visualizer class

    https://plotly.com/python/basic-charts/

    """

    @classmethod
    def draw_bar_chart(
        cls,
        df_in: Series,
        title: str,
        x: str,
        y: str,
        xlabel: str,
        ylabel: str,
        color: str = None,
        include_plotlyjs="cdn",
        limit=None,
        ) -> str | None:
        """Draw Bar Chart using Plotly based on DataFrame df and using title, x and y"""
        # we must reset index to work this thing out
        df_new: pd.DataFrame = df_in.reset_index()
        if df_new.empty:
            return None
        # if we set limit cut off all below this limit
        if limit is not None and color is not None:
            df_new = cls._add_others_column_to_df(
                df_in=df_new,
                x=color,
                y=y,
                limit=limit,
                )
        fig = px.bar(
            df_new,
            x=x,
            y=y,
            title=title,
            labels={x: xlabel, y: ylabel},
            color=color,
            text_auto=True,
            )
        return plot(fig, output_type="div", include_plotlyjs=include_plotlyjs)

    @classmethod
    def draw_pie_chart(
        cls,
        df_in: Series,
        title: str,
        values: str,
        names: str,
        include_plotlyjs="cdn",
        limit=None,
        ):
        """Draw Pie Chart using Plotly based on DataFrame df and using title, x and y"""
        # we must reset index to work this thing out
        df_new: pd.DataFrame = df_in.reset_index()
        if df_new.empty:
            return None
        # if we set limit cut off all below this limit
        if limit:
            df_new = cls._add_others_column_to_df(
                df_in=df_new,
                x=names,
                y=values,
                limit=limit,
                )
        fig = px.pie(
            df_new,
            values=values,
            names=names,
            title=title,
            )
        return plot(fig, output_type="div", include_plotlyjs=include_plotlyjs)

    @staticmethod
    def _add_others_column_to_df(
        df_in: pd.DataFrame,
        x: str,
        y: str,
        limit: float,
        ):
        """Adds column Others to DataFrame which is sum of small values (less than limit)"""
        summa = df_in[df_in[y] < limit][y].sum()
        df_in = df_in[df_in[y] >= limit]
        new_row = pd.Series({x: "Other", y: summa})
        return df_in.append(new_row, ignore_index=True)

    @staticmethod
    def _accumulate_others_category_in_df(df_in, limit, accum_col: str):
        """Accumulate small amounts of categories into one category (Other)"""
        df_result = df_in[df_in[accum_col] > limit]
        df_other = df_in[df_in[accum_col] < limit]
        if df_other.sum() > 0:
            others_accumulated = pd.Series([df_other.sum()], index=["Other"])
            df_result = df_result.append(others_accumulated)
        return df_result
