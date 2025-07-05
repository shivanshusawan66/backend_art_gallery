from typing import Any, Dict, Optional
import jwt
from datetime import datetime, timedelta
from skti_system_backend.config.v1.authentication_config import authentication_config


def create_jwt_token(user_id: int, role: str) -> str:
    """
    Create a JWT token for authenticated user.
    
    Args:
        user_id (int): The user's ID
        role (str): The user's role
        
    Returns:
        str: JWT token
    """
    try: 
        payload = {
            "sub": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        token =  jwt.encode(
            payload,
            authentication_config.JWT_SECRET_KEY,
            algorithm=authentication_config.JWT_ALGORITHM
        )
        return token

    except Exception as e:
        print(f"JWT token creation error: {str(e)}")
        raise e

