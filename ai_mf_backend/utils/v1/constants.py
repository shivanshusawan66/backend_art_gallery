from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

from ai_mf_backend.utils.v1.generic_helper import Singleton

from ai_mf_backend.models.v1.database.mutual_fund import FundOverview, FundData
from ai_mf_backend.models.v1.database.reference_table import Reference

from ai_mf_backend.utils.v1.enums import ReferenceTableEnums


class MFFilterOptions(Singleton):
    def __init__(self):
        self.fund_families = None
        self.morningstar_rating = None
        self.min_initial_investments = None

    @staticmethod
    def convert_morningstar_rating(rating: str) -> int:
        """Converts a Morningstar rating string to an integer based on its length."""
        return len(rating) if rating else 0

    async def compute_filter_options(self):
        """Precomputes filter options by querying the database with optimized field selection."""
        fund_families = await sync_to_async(
            lambda: sorted(
                FundOverview.objects.only("fund_family")
                .values_list("fund_family", flat=True)
                .distinct()
            )
        )()

        morningstar_ratings = await sync_to_async(
            lambda: sorted(
                map(
                    self.convert_morningstar_rating,
                    FundOverview.objects.only("morningstar_rating")
                    .values_list("morningstar_rating", flat=True)
                    .distinct(),
                )
            )
        )()

        min_initial_investments = await sync_to_async(
            lambda: sorted(
                float(i)
                for i in FundData.objects.only("min_initial_investment")
                .values_list("min_initial_investment", flat=True)
                .distinct()
            )
        )()

        self.fund_families = fund_families
        self.morningstar_rating = morningstar_ratings
        self.min_initial_investments = min_initial_investments

        return self


class MFProjectionTableMappings(Singleton):
    def __init__(self):
        self.mapping = None
        self.valid_projections = None

    async def get_mapping(self):
        reference_documents = await sync_to_async(
            lambda: Reference.objects.filter(
                reference_type=ReferenceTableEnums.projection_table_mapping.value
            ).only("table_name", "column_name", "display_name")
        )()

        reference_documents = await sync_to_async(
            lambda: [model_to_dict(i) for i in reference_documents]
        )()

        self.mapping = {i["display_name"]: i for i in reference_documents}
        self.valid_projections = [i["display_name"] for i in reference_documents]

        return self


filter_option_object = MFFilterOptions()
projection_table_object = MFProjectionTableMappings()


async def refresh_constants():
    global filter_option_object, projection_table_object
    filter_option_object = await MFFilterOptions().compute_filter_options()
    projection_table_object = await MFProjectionTableMappings().get_mapping()
