from typing import Annotated

from fastapi import HTTPException, Header

from ai_mf_backend.config.v1.authentication_config import authentication_config


async def login_checker(Authorization: Annotated[str | None, Header()]):
    if Authorization:
        Authorization = Authorization.replace("Bearer", "").strip()

        if Authorization == authentication_config.SECRET:
            return Authorization
        else:
            raise HTTPException(
                status_code=401,
                detail="Token is invalid",
            )

    raise HTTPException(
        status_code=401,
        detail="No JWT token found.",
    )
