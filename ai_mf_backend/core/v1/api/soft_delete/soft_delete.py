from fastapi import APIRouter, HTTPException, Response
from asgiref.sync import sync_to_async
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.db import models, transaction
from ai_mf_backend.models.v1.api.soft_delete import (
    soft_delete_and_clone_request,
    soft_delete_and_clone_response,
    soft_update_and_clone_request,
    soft_update_and_clone_response,
)
from django.db.models import ForeignKey, ManyToOneRel

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/soft-delete-and-clone")
async def soft_delete_and_clone(
    request: soft_delete_and_clone_request, response: Response
):
    """
    API endpoint to soft delete and clone related records for a given model instance.
    :param request: The request body containing the model name and model ID
    :return: Success message if successful, else error message
    """
    try:
        model_class = await sync_to_async(apps.get_model)(
            "ai_mf_backend", request.model
        )

        if model_class is None:
            raise HTTPException(status_code=404, detail="Model not found")

        instance = await sync_to_async(model_class.objects.get)(
            **{request.field_name: request.record_id}
        )

        with transaction.atomic():
            instance.deleted = True
            await sync_to_async(instance.save)()

            for field in model_class._meta.get_fields():
                print("step2")
                print(
                    f"Checking field: {field.name}, type: {type(field)}, is_relation: {field.is_relation}, many_to_one: {field.many_to_one}"
                )

                # Handle ForeignKey relationships
                if isinstance(field, ManyToOneRel):
                    related_model = field.related_model
                    related_records = await sync_to_async(list)(
                        related_model.objects.filter(
                            **{request.field_name: instance}, deleted=False
                        )
                    )

                    for record in related_records:
                        cloned_record = type(
                            record
                        )()  # Create a new instance of the same class

                        # Iterate over fields and copy values
                        for field in record._meta.fields:
                            if (
                                field.name in ["id", "created_at", request.field_name]
                                or field.unique
                            ):
                                continue

                            if isinstance(field, models.ForeignKey):
                                # Wrap access to foreign key fields in sync_to_async
                                value = await sync_to_async(
                                    lambda: getattr(record, field.name)
                                )()
                            else:
                                # For other fields, we can access them directly
                                value = getattr(record, field.name)

                            # Check if the value is None
                            if value is None:
                                print(f"Value for {field.name} is None")
                            else:
                                print(f"Value for {field.name}: {value}")

                            # Check if the field is a ForeignKey
                            if isinstance(field, models.ForeignKey):
                                if value is None:
                                    setattr(
                                        cloned_record, field.name, None
                                    )  # Set ForeignKey to None if allowed
                                else:
                                    # Ensure that you're setting it to a valid instance
                                    try:
                                        setattr(
                                            cloned_record, field.name, value
                                        )  # Assuming value is a valid instance
                                    except Exception as e:
                                        setattr(
                                            cloned_record, field.name, None
                                        )  # Fallback if there's an error

                            else:
                                setattr(cloned_record, field.name, value)

                        if hasattr(cloned_record, request.field_name):
                            setattr(
                                cloned_record, request.field_name, None
                            )  # Set the ForeignKey field to NULL
                        await sync_to_async(
                            cloned_record.save
                        )()  # Save the cloned record

                        # Soft delete the original record
                        record.deleted = True
                        await sync_to_async(record.save)()

                # Handle OneToOneField relationships
                elif isinstance(field, models.OneToOneField):
                    related_model = field.related_model
                    related_name = field.name

                    try:
                        related_record = await sync_to_async(related_model.objects.get)(
                            **{request.field_name: instance}, deleted=False
                        )

                        # Clone the record with the OneToOneField set to None
                        cloned_record = type(
                            related_record
                        )()  # Create a new instance of the same class

                        # Iterate over fields and copy values
                        for field in related_record._meta.fields:
                            if field.name in ["id", "created_at"] or field.unique:
                                continue
                            # Copy value from original record
                            setattr(
                                cloned_record,
                                field.name,
                                getattr(related_record, field.name),
                            )

                        setattr(
                            cloned_record, related_name, None
                        )  # Set the OneToOneField to NULL
                        await sync_to_async(
                            cloned_record.save
                        )()  # Save the cloned record

                        # Soft delete the original record
                        related_record.deleted = True
                        await sync_to_async(related_record.save)()
                    except related_model.DoesNotExist:
                        continue  # No related record exists

        logger.info(
            f"All related records for {model_class.__name__} '{instance}' have been soft deleted and cloned."
        )
        response.status_code = 200
        return soft_delete_and_clone_response(
            status=True,
            message="success",
            data={
                "message": f"Records related to {model_class.__name__} '{instance}' have been soft deleted and cloned."
            },
            status_code=200,
        )

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404, detail="Instance not found.")
    except LookupError:
        raise HTTPException(status_code=404, detail="Model not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/soft-update-and-clone")
async def soft_update_and_clone(
    request: soft_update_and_clone_request, response: Response
):
    try:
        model_class = await sync_to_async(apps.get_model)(
            "ai_mf_backend", request.model
        )

        if model_class is None:
            raise HTTPException(status_code=404, detail="Model not found")

        instance = await sync_to_async(model_class.objects.get)(
            **{request.field_name: request.old_record_id}
        )

        with transaction.atomic():
            setattr(instance, request.field_name, request.new_record_value)
            await sync_to_async(instance.save)()

            # Iterate through all fields in the model
            for field in model_class._meta.get_fields():
                # Handle ForeignKey relationships
                if isinstance(field, ManyToOneRel):
                    related_model = field.related_model
                    related_records = await sync_to_async(list)(
                        related_model.objects.filter(
                            **{request.field_name: instance}, deleted=False
                        )
                    )

                    for record in related_records:
                        cloned_record = type(record)()

                        # Copy values from the original record
                        for field in record._meta.fields:
                            if (
                                field.name in ["id", "created_at", request.field_name]
                                or field.unique
                            ):
                                continue

                            if isinstance(field, models.ForeignKey):
                                value = await sync_to_async(
                                    lambda: getattr(record, field.name)
                                )()
                            else:
                                value = getattr(record, field.name)

                            if isinstance(field, models.ForeignKey):
                                if value is None:
                                    setattr(
                                        cloned_record, field.name, None
                                    )  # Set ForeignKey to None if allowed
                                else:
                                    # Ensure that you're setting it to a valid instance
                                    try:
                                        setattr(
                                            cloned_record, field.name, value
                                        )  # Assuming value is a valid instance
                                    except Exception as e:
                                        setattr(
                                            cloned_record, field.name, None
                                        )  # Fallback if there's an error

                            else:
                                setattr(cloned_record, field.name, value)

                        try:
                            new_instance = await sync_to_async(model_class.objects.get)(
                                **{request.field_name: request.new_record_value}
                            )  # Get the Gender instance

                            if hasattr(cloned_record, request.field_name):
                                # Set the ForeignKey field to the Gender instance
                                setattr(
                                    cloned_record, request.field_name, new_instance
                                )  # Set to the instance instead of string

                                await sync_to_async(
                                    cloned_record.save
                                )()  # Save the cloned record
                            else:
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Field '{request.field_name}' does not exist on cloned_record.",
                                )
                        except model_class.DoesNotExist:
                            raise HTTPException(
                                status_code=404,
                                detail=f"{model_class} instance for {request.new_record_value} not found.",
                            )
                        except Exception as e:
                            raise HTTPException(status_code=500, detail=str(e))

                        # Soft delete the original record
                        record.deleted = True
                        await sync_to_async(record.save)()

                # Handle OneToOneField relationships
                elif isinstance(field, models.OneToOneField):
                    related_model = field.related_model

                    try:
                        related_record = await sync_to_async(related_model.objects.get)(
                            **{request.field_name: instance}, deleted=False
                        )
                        cloned_record = type(related_record)()

                        # Copy values from the original record
                        for field in related_record._meta.fields:
                            if field.name in ["id", "created_at"] or field.unique:
                                continue
                            setattr(
                                cloned_record,
                                field.name,
                                getattr(related_record, field.name),
                            )

                        # Set field to `request.new_values` instead of None
                        if hasattr(cloned_record, request.field_name):
                            setattr(
                                cloned_record,
                                request.field_name,
                                request.new_record_value,
                            )  # Set the ForeignKey field to NULL
                        await sync_to_async(cloned_record.save)()

                        # Soft delete the original record
                        related_record.deleted = True
                        await sync_to_async(related_record.save)()
                    except related_model.DoesNotExist:
                        continue

        logger.info(
            f"All related records for {model_class.__name__} '{instance}' have been soft deleted and cloned."
        )
        response.status_code = 200
        return soft_delete_and_clone_response(
            status=True,
            message="success",
            data={
                "message": f"Records related to {model_class.__name__} '{instance}' have been soft deleted and cloned."
            },
            status_code=200,
        )

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404, detail="Instance not found.")
    except LookupError:
        raise HTTPException(status_code=404, detail="Model not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
