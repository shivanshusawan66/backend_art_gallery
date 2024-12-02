from ai_mf_backend.models.v1.database.mutual_fund import FundOverview, FundData


def convert_morningstar_rating(rating: str) -> int:
    """Converts a Morningstar rating string to an integer based on its length."""
    return len(rating) if rating else 0


def precompute_filter_options():
    """Precomputes filter options by querying the database with optimized field selection."""
    fund_families = sorted(
        FundOverview.objects.only("fund_family")
        .values_list("fund_family", flat=True)
        .distinct()
    )
    morningstar_ratings = sorted(
        map(
            convert_morningstar_rating,
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

    return {
        "fund_families": fund_families,
        "morningstar_ratings": morningstar_ratings,
        "min_initial_investments": min_initial_investments,
    }


FILTER_OPTIONS = precompute_filter_options()
