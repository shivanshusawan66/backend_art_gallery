from fastapi import APIRouter, Request, Response, status

from django.core.exceptions import ValidationError
from ai_mf_backend.core.v1.api import limiter
from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.contact_message import (
    ContactMessage,
    ContactMessageFundCategory,
)
from ai_mf_backend.utils.v1.authentication.validators import (
    custom_validate_international_phonenumber,
)
from ai_mf_backend.utils.v1.validators.name import validate_name

from ai_mf_backend.config.v1.api_config import api_config

from ai_mf_backend.models.v1.api.contact_message import (
    ContactMessageFundCategoryOptionResponse,
    ContactMessageRequest,
    ContactMessageResponse,
)

router = APIRouter(tags=["contact_message"])


@router.get(
    "/options_contact_message_fund_category",
    response_model=ContactMessageFundCategoryOptionResponse,
)
async def get_options_contact_message_fund_category():
    try:
        categories = await sync_to_async(list)(ContactMessageFundCategory.objects.all())

        category_options = [
            {
                "key": int(category.id),
                "label": category.fund_type,
                "value": category.fund_type.lower(),
            }
            for category in categories
        ]

        data = {
            "contact_message_fund_categories": {
                "name": "contact_message_fund_category",
                "label": "Contact Message Fund Category",
                "options": category_options,
                "type": "dropdown",
                "default": [category_options[0]["key"]] if category_options else [],
                "required": False,
            }
        }

        return ContactMessageFundCategoryOptionResponse(
            status=True,
            message="Contact message fund category options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        return ContactMessageFundCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch contact message fund category options: {str(e)}",
            data={},
            status_code=500,
        )


@router.post(
    "/submit_contact_message",
    response_model=ContactMessageResponse,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def submit_contact_message(
    request: Request,
    body: ContactMessageRequest,
    response: Response,
):
    try:
        if not body.first_name.strip():
            raise ValidationError("First name cannot be empty.")

        validate_name(body.first_name)
        if body.last_name:
            validate_name(body.last_name)
        custom_validate_international_phonenumber(body.phone_number)

        category = await sync_to_async(
            ContactMessageFundCategory.objects.filter(id=body.category_id).first
        )()
        if not category:
            raise ValidationError("Invalid category ID provided.")

        contact_message = ContactMessage(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone_number=body.phone_number,
            category_id=category,
            message=body.message,
        )

        await sync_to_async(contact_message.full_clean)()
        await sync_to_async(contact_message.save)()

    except Exception as e:
        response.status_code = 400
        return ContactMessageResponse(
            status=False,
            message=f"Error saving contact message: {str(e)}",
            data={},
            status_code=500,
        )

    data = {
        "id": contact_message.id,
        "first_name": contact_message.first_name,
        "last_name": contact_message.last_name,
        "email": contact_message.email,
        "phone_number": contact_message.phone_number,
        "category_id": contact_message.category_id.id,
        "message": contact_message.message,
    }

    response.status_code = 200
    return ContactMessageResponse(
        status=True,
        message="Contact message submitted successfully.",
        data=data,
        status_code=200,
    )
