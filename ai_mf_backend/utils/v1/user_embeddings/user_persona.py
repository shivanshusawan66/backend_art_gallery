def get_user_persona(value: float) -> str:
    """
    Classifies a value between 0 and 1 into one of five market personas.

    Parameters:
    - value (float): A number between 0 and 1 (inclusive).

    Returns:
    - str: Market persona as one of:
        'Very Bearish', 'Bearish', 'Neutral', 'Bullish', 'Very Bullish'
        or an error message if input is invalid.
    """
    try:
        if not 0 <= value <= 1:
            raise ValueError("Value must be between 0 and 1 (inclusive).")

        if value <= 0.2:
            return "Very Bearish"
        elif value <= 0.4:
            return "Bearish"
        elif value <= 0.6:
            return "Neutral"
        elif value <= 0.8:
            return "Bullish"
        else:
            return "Very Bullish"
    except Exception as e:
        return f"Error: {str(e)}"
