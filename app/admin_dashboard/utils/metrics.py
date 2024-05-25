import pandas as pd

from admin_dashboard.models import Stat
from admin_dashboard.services.metrics import ServiceMetrics
from admin_dashboard.services.visualizer import PlotlyVisualizer
from admin_dashboard.utils.data_builder import DataBuilder


class MetricsUtils:

    @classmethod
    def calculate_metrics(cls) -> dict:
        metrics = {"total_users": ServiceMetrics.total_users(),
                   "users_with_messages": ServiceMetrics.users_with_messages(),
                   "users_with_no_messages": ServiceMetrics.users_with_no_messages(),
                   "reached_maximum_messages": ServiceMetrics.reached_maximum_messages(),
                   "number_of_problems_not_public": ServiceMetrics.number_of_problems_not_public(),
                   "number_of_problems_public": ServiceMetrics.number_of_problems_public(),
                   "number_of_users_messages": ServiceMetrics.number_of_users_messages(),
                   "users_with_problems": ServiceMetrics.users_with_problems(),
                   "number_of_problem_messages_total": ServiceMetrics.number_of_problem_messages_total(),
                   "number_of_problem_messages_text": ServiceMetrics.number_of_problem_messages_text(),
                   "number_of_problem_messages_photo": ServiceMetrics.number_of_problem_messages_photo(),
                   "ratio_reached_per_signups": ServiceMetrics.ratio_reached_per_signups(),
                   "ratio_at_least_one_message_users_to_signups": ServiceMetrics.ratio_at_least_one_message_users_to_signups(),
                   "chat_satisfaction": ServiceMetrics.chat_satisfaction(),
                   "photos_to_text_messages_ratio": ServiceMetrics.photos_to_text_messages_ratio(),
                   "custom_problems_to_total_users_with_messages_ratio": ServiceMetrics.custom_problems_to_total_users_with_messages_ratio(),
                   }
        return metrics

    @classmethod
    def get_chart_metrics(cls) -> dict:
        return {"chart_total_users": cls.chart_total_users(),
                "chart_users_with_problems": cls.chart_users_with_problems(),
                "chart_chat_satisfaction": cls.chart_chat_satisfaction(),
                "chart_users_with_messages": cls.chart_users_with_messages(),
                "chart_users_with_no_messages": cls.chart_users_with_no_messages(),
                "chart_number_of_problems_public": cls.chart_number_of_problems_public(),
                "chart_number_of_users_messages": cls.chart_number_of_users_messages(),
                "chart_ratio_reached_per_signups": cls.chart_ratio_reached_per_signups(),
                "chart_reached_maximum_messages": cls.chart_reached_maximum_messages(),
                "chart_number_of_problems_not_public": cls.chart_number_of_problems_not_public(),
                "chart_number_of_problem_messages_text": cls.chart_number_of_problem_messages_text(),
                "chart_photos_to_text_messages_ratio": cls.chart_photos_to_text_messages_ratio(),
                "chart_number_of_problem_messages_photo": cls.chart_number_of_problem_messages_photo(),
                "chart_number_of_problem_messages_total": cls.chart_number_of_problem_messages_total(),
                "chart_ratio_at_least_one_message_users_to_signups": cls.chart_ratio_at_least_one_message_users_to_signups(),
                "chart_custom_problems_to_total_users_with_messages_ratio": cls.chart_custom_problems_to_total_users_with_messages_ratio(),
                }

    @classmethod
    def save_metrics_to_db(cls):
        stat = Stat()
        stat.metrics = cls.calculate_metrics()
        stat.save()
        return stat.metrics

    @classmethod
    def chart_total_users(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__total_users"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="SignUps",
            x="created_at",
            y="metrics__total_users",
            xlabel="Date",
            ylabel="Users (Sign Ups)",
            )

    @classmethod
    def chart_users_with_problems(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__users_with_problems"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="users_with_problems",
            x="created_at",
            y="metrics__users_with_problems",
            xlabel="Date",
            ylabel="Users",
            )

    @classmethod
    def chart_chat_satisfaction(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__chat_satisfaction"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="chat_satisfaction",
            x="created_at",
            y="metrics__chat_satisfaction",
            xlabel="Date",
            ylabel="chat_satisfaction",
            )

    @classmethod
    def chart_users_with_messages(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__users_with_messages"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__users_with_messages",
            x="created_at",
            y="metrics__users_with_messages",
            xlabel="Date",
            ylabel="metrics__users_with_messages",
            )

    @classmethod
    def chart_users_with_no_messages(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__users_with_no_messages"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__users_with_no_messages",
            x="created_at",
            y="metrics__users_with_no_messages",
            xlabel="Date",
            ylabel="metrics__users_with_no_messages",
            )

    @classmethod
    def chart_number_of_problems_public(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_problems_public"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_problems_public",
            x="created_at",
            y="metrics__number_of_problems_public",
            xlabel="Date",
            ylabel="metrics__number_of_problems_public",
            )

    @classmethod
    def chart_number_of_users_messages(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_users_messages"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_users_messages",
            x="created_at",
            y="metrics__number_of_users_messages",
            xlabel="Date",
            ylabel="metrics__number_of_users_messages",
            )

    @classmethod
    def chart_ratio_reached_per_signups(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__ratio_reached_per_signups"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__ratio_reached_per_signups",
            x="created_at",
            y="metrics__ratio_reached_per_signups",
            xlabel="Date",
            ylabel="metrics__ratio_reached_per_signups",
            )

    @classmethod
    def chart_reached_maximum_messages(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__reached_maximum_messages"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__reached_maximum_messages",
            x="created_at",
            y="metrics__reached_maximum_messages",
            xlabel="Date",
            ylabel="metrics__reached_maximum_messages",
            )

    @classmethod
    def chart_number_of_problems_not_public(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_problems_not_public"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_problems_not_public",
            x="created_at",
            y="metrics__number_of_problems_not_public",
            xlabel="Date",
            ylabel="metrics__number_of_problems_not_public",
            )

    @classmethod
    def chart_number_of_problem_messages_text(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_problem_messages_text"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_problem_messages_text",
            x="created_at",
            y="metrics__number_of_problem_messages_text",
            xlabel="Date",
            ylabel="metrics__number_of_problem_messages_text",
            )

    @classmethod
    def chart_photos_to_text_messages_ratio(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__photos_to_text_messages_ratio"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__photos_to_text_messages_ratio",
            x="created_at",
            y="metrics__photos_to_text_messages_ratio",
            xlabel="Date",
            ylabel="metrics__photos_to_text_messages_ratio",
            )

    @classmethod
    def chart_number_of_problem_messages_photo(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_problem_messages_photo"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_problem_messages_photo",
            x="created_at",
            y="metrics__number_of_problem_messages_photo",
            xlabel="Date",
            ylabel="metrics__number_of_problem_messages_photo",
            )

    @classmethod
    def chart_number_of_problem_messages_total(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__number_of_problem_messages_total"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__number_of_problem_messages_total",
            x="created_at",
            y="metrics__number_of_problem_messages_total",
            xlabel="Date",
            ylabel="metrics__number_of_problem_messages_total",
            )

    @classmethod
    def chart_ratio_at_least_one_message_users_to_signups(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__ratio_at_least_one_message_users_to_signups"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__ratio_at_least_one_message_users_to_signups",
            x="created_at",
            y="metrics__ratio_at_least_one_message_users_to_signups",
            xlabel="Date",
            ylabel="metrics__ratio_at_least_one_message_users_to_signups",
            )

    @classmethod
    def chart_custom_problems_to_total_users_with_messages_ratio(cls) -> str:
        df = cls._get_stats_data()
        df = df["metrics__custom_problems_to_total_users_with_messages_ratio"]

        return PlotlyVisualizer.draw_bar_chart(
            df_in=df,
            title="metrics__custom_problems_to_total_users_with_messages_ratio",
            x="created_at",
            y="metrics__custom_problems_to_total_users_with_messages_ratio",
            xlabel="Date",
            ylabel="metrics__custom_problems_to_total_users_with_messages_ratio",
            )

    @classmethod
    def _get_stats_data(cls) -> pd.DataFrame:
        qs = DataBuilder.get_metrics_from_db()
        fields = ("metrics__total_users",
                  "metrics__users_with_problems",
                  "metrics__chat_satisfaction",
                  "metrics__users_with_messages",
                  "metrics__users_with_no_messages",
                  "metrics__number_of_problems_public",
                  "metrics__number_of_users_messages",
                  "metrics__ratio_reached_per_signups",
                  "metrics__reached_maximum_messages",
                  "metrics__number_of_problems_not_public",
                  "metrics__number_of_problem_messages_text",
                  "metrics__photos_to_text_messages_ratio",
                  "metrics__number_of_problem_messages_photo",
                  "metrics__number_of_problem_messages_total",
                  "metrics__ratio_at_least_one_message_users_to_signups",
                  "metrics__custom_problems_to_total_users_with_messages_ratio",
                  "created_at",
                  )
        df = pd.DataFrame(list(qs.values(*fields)))
        df.index = pd.to_datetime(df["created_at"], format="%Y-%m-%d")
        return df
