from ai_mf_backend.config.v1 import BaseSettingsWrapper


class ColumnNames(BaseSettingsWrapper):
    """
    ColoumnNmaes Configuration class that sets up a BaseSettingsWrapper with all coloumn name list present in our database for our mutual funds

    

    :returns: An instance of the ColumnNames class with a specified 
    :return type: ColumnNames instance
    """

    MUTUAL_FUND_OVERVIEW_COLOUMNS: list[str] = ["id", "scheme_name", "q_param", "net_asset_value", "symbol"]
    MUTUAL_FUND_PERFORMANCE_COLOUMNS:list[str] = ["fund_id", "ytd_return", "average_return_5y", "number_of_years_up", 
                                                  "number_of_years_down", "best_1y_total_return", "worst_1y_total_return", 
                                                  "best_3y_total_return", "worst_3y_total_return"]


mutual_funds_table_config = ColumnNames()
