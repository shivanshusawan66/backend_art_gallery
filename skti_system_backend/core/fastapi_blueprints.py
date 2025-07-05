from skti_system_backend.core import connect_router

# Authentication Routers
from skti_system_backend.core.v1.api.gallery import (
    router as authentication_router_v1,
)



# Router Inclusions
connect_router.include_router(authentication_router_v1)
