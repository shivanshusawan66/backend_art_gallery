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

# Fixed columns that are always included in the query
FIXED_COLUMNS = [
    "fund_id",
    "scheme_name",
    "morningstar_rating",
    "fund_family",
    "net_asset_value",
    "min_investment",
]

# Predefined valid columns to check the request against
VALID_COLUMNS = set(COLUMN_MAPPING.keys())

# Default page size and validation constants
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Error message constants
ERROR_MESSAGES = {
    "invalid_columns": "Invalid columns: {columns}",
    "no_mutual_funds_found": "No mutual funds found matching the specified filter.",
    "unexpected_error": "An unexpected error occurred: {error}",
}

# Validation constants
VALID_MORNINGSTAR_RATINGS = ["1", "2", "3", "4", "5"]  # Example ratings
