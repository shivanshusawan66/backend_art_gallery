from ai_mf_backend.utils.v1.generic_helper import Singleton

from ai_mf_backend.models.v1.database.mutual_fund import FundOverview, FundData


class MFFilterOptions(Singleton):
    def __init__(self):
        self.fund_families = None
        self.morningstar_rating = None
        self.min_initial_investments = None

    @staticmethod
    def convert_morningstar_rating(rating: str) -> int:
        """Converts a Morningstar rating string to an integer based on its length."""
        return len(rating) if rating else 0

    def compute_filter_options(self):
        """Precomputes filter options by querying the database with optimized field selection."""
        fund_families = sorted(
            FundOverview.objects.only("fund_family")
            .values_list("fund_family", flat=True)
            .distinct()
        )
        morningstar_ratings = sorted(
            map(
                self.convert_morningstar_rating,
                FundOverview.objects.only("morningstar_rating")
                .values_list("morningstar_rating", flat=True)
                .distinct(),
            )
        )
        min_initial_investments = sorted(
            float(i)
            for i in FundData.objects.only("min_initial_investment")
            .values_list("min_initial_investment", flat=True)
            .distinct()
        )

        self.fund_families = fund_families
        self.morningstar_rating = morningstar_ratings
        self.min_initial_investments = min_initial_investments

        return self


filter_option_object = MFFilterOptions().compute_filter_options()

# Mapping of API request columns to database fields
COLUMN_MAPPING = {
    # Basic Information
    "scheme_name": ("scheme_name", None),
    "fund_id": ("id", None),
    "net_asset_value": ("net_asset_value", None),
    # Overview Related
    "ytd_return": ("overview__ytd_return", "overview"),
    "morningstar_rating": ("overview__morningstar_rating", "overview"),
    "fund_family": ("overview__fund_family", "overview"),
    "net_assets": ("overview__net_assets", "overview"),
    "yield_value": ("overview__yield_value", "overview"),
    "inception_date": ("overview__inception_date", "overview"),
    # Fund Data
    "min_investment": ("fund_data__min_initial_investment", "fund_data"),
    # Performance Data
    "performance_ytd_return": ("performance_data__ytd_return", "performance_data"),
    "performance_average_return_5y": (
        "performance_data__average_return_5y",
        "performance_data",
    ),
    "number_of_years_up": ("performance_data__number_of_years_up", "performance_data"),
    "number_of_years_down": (
        "performance_data__number_of_years_down",
        "performance_data",
    ),
    "best_3y_total_return": (
        "performance_data__best_3y_total_return",
        "performance_data",
    ),
    "worst_3y_total_return": (
        "performance_data__worst_3y_total_return",
        "performance_data",
    ),
    # Risk Statistics
    "alpha": ("risk_statistics__alpha", "risk_statistics"),
    "beta": ("risk_statistics__beta", "risk_statistics"),
    "mean_annual_return": ("risk_statistics__mean_annual_return", "risk_statistics"),
    "r_squared": ("risk_statistics__r_squared", "risk_statistics"),
    "standard_deviation": ("risk_statistics__standard_deviation", "risk_statistics"),
    "sharpe_ratio": ("risk_statistics__sharpe_ratio", "risk_statistics"),
    "treynor_ratio": ("risk_statistics__treynor_ratio", "risk_statistics"),
}

# Predefined valid columns to check the request against
VALID_COLUMNS = set(COLUMN_MAPPING.keys())

# Error message constants
ERROR_MESSAGES = {
    "invalid_columns": "Invalid columns: {columns}",
    "no_mutual_funds_found": "No mutual funds found matching the specified filter.",
    "unexpected_error": "An unexpected error occurred: {error}",
}
