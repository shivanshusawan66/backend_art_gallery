import logging

from celery import chain
from sklearn.preprocessing import normalize
from django.db import transaction

from ai_mf_backend.core import celery_app

from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.mf_embedding_tables import (
    Section,
    MFMarker,
    MFMarkerOptions,
    MFResponse,
    MarkerWeightsPerMutualFund,
    SectionWeightsPerMutualFund,
)
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeMasterInDetails
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)


@celery_app.task(acks_late=False, bind=True)
def assign_final_marker_weights(self, scheme_code: int):
    try:
        with transaction.atomic():
            # Fetch all sections
            mf_responses = MFResponse.objects.filter(scheme_code=scheme_code)
            for response in mf_responses:
                option_id = int(response.option_id.id)

                derived_option = MFMarkerOptions.objects.filter(
                    pk=option_id
                ).first()

                option_score = (
                    derived_option.option_weight * derived_option.position
                )
                Marker = MFMarker.objects.filter(
                    marker=response.marker_id
                ).first()

                marker_weight_for_mutual_fund = MarkerWeightsPerMutualFund.objects.filter(
                    scheme_code=scheme_code,
                    marker=response.marker_id,
                    section=response.section_id,
                ).first()

                if marker_weight_for_mutual_fund:
                    marker_weight_for_mutual_fund.weight = (
                        option_score * Marker.initial_marker_weight
                    )
                    marker_weight_for_mutual_fund.save()
                else:
                    marker_weight_for_mutual_fund = MarkerWeightsPerMutualFund(
                        scheme_code=scheme_code,
                        marker=response.marker_id,
                        section=response.section_id,
                        weight=option_score * Marker.initial_marker_weight,
                    )
                logger.info(f"marker weight saved {scheme_code}")
                marker_weight_for_mutual_fund.save()
    except Exception as e:
        logger.error(f"Error assigning final marker weights for scheme {scheme_code}: {e}")
        raise AssignWeightException(
            f"Error assigning final marker weights for scheme {scheme_code}: {e}"
        )


@celery_app.task(acks_late=False, bind=True)
def assign_final_section_weights_for_mutual_funds(self, scheme_code: int):
    try:
        with transaction.atomic():
            Markers = MarkerWeightsPerMutualFund.objects.filter(scheme_code=scheme_code)
            sections = Section.objects.all()

            embedding_array = []
            for section in sections:
                final_section_weight = 0
                for marker in Markers:
                    if marker.section == section:
                        final_section_weight += marker.weight
                    else:
                        continue
                embedding_array.append(final_section_weight)

            normalized = normalize([embedding_array], norm='l2')[0]

            section_weight_for_mutual_fund = SectionWeightsPerMutualFund.objects.filter(
                scheme_code=scheme_code,
            ).first()

            if section_weight_for_mutual_fund:
                section_weight_for_mutual_fund.embedding = normalized.tolist()
                section_weight_for_mutual_fund.save()
            else:
                section_weight_for_mutual_fund = SectionWeightsPerMutualFund(
                    scheme_code=scheme_code, 
                    embedding = normalized.tolist()
                )
                logger.info(f"section weight saved for scheme : {scheme_code}")
                section_weight_for_mutual_fund.save()
    except Exception as e:
        logger.error(f"Error assigning final section weights for scheme {scheme_code}: {e}")
        raise AssignWeightException(
            f"Error assigning final section weights for scheme {scheme_code}: {e}"
        )


async def assign_user_weights_chain(scheme_codes: list): 
    failed_schemes = []
    for scheme_code in scheme_codes:
        try: 
            logger.info(f"Assigning weights for scheme code: {scheme_code}")
            task_chain = chain( 
                assign_final_marker_weights.si(scheme_code), 
                assign_final_section_weights_for_mutual_funds.si(scheme_code), 
            ) 
            task_chain.apply_async() 
        except Exception as e: 
            error_msg = f"Error assigning weights for scheme code {scheme_code}: {e}"
            logger.error(error_msg) 
            failed_schemes.append(scheme_code)
    
    if failed_schemes:
        error_message = f"Failed to assign weights for scheme codes: {failed_schemes}"
        logger.error(error_message)
        raise AssignWeightException(error_message)
            
    return f"Successfully initiated weight assignment for {len(scheme_codes) - len(failed_schemes)} out of {len(scheme_codes)} scheme codes"


async def process_all_schemes():
    active_scheme_codes = await sync_to_async(list)(MFSchemeMasterInDetails.objects.filter(status="Active").values_list("schemecode", flat=True))
    try:
        result = await assign_user_weights_chain(active_scheme_codes)
        logger.info(result)
    except AssignWeightException as e:
        logger.error(f"Weight assignment process failed: {e}")