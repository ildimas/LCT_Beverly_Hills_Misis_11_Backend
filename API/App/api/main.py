from fastapi import FastAPI
import uvicorn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowPassword
from API.App.api.routes.user import user_router
from API.App.api.routes.auth import auth_router
from API.App.api.routes.category import category_router
from API.App.api.routes.allocation import allocation_router
from API.App.api.routes.prediction import prediction_router
from API.App.api.routes.bills_and_refs import billsandrefs_router
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from logging.config import dictConfig
import logging
from API.App.core.loging_config import LogConfig
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("washingtonsilver")

# logger.info("Dummy Info")
# logger.error("Dummy Error")
# logger.debug("Dummy Debug")
# logger.warning("Dummy Warning")

from dotenv import load_dotenv
load_dotenv()

# tags_metadata = [
#     {
#         "name": "user",
#         "description": "User is a base class which id contains in all other clasess this object can be: registred, deleted or authenificate",
#     },
#     {
#         "name": "category",
#         "description": "Categories is the second grade object in odject hierarchy. the main purpose of it is to filter allocations"
#     },
#     {
#         "name": "allocation",
#         "description": "The main onject in this api is allocations it contains your processed allocations and this object lead to reference books objects, bills to pay, and predicted values"
#     },
#     {
#         "name": "rediction",
#         "description": "The object holding procesed analytics results for allocation for a next 12 month. Contains various endpoints to easily filter out values"
#     },
#     {
#         "name": "bills_and_refs",
#         "description": "Group of object that stores all needed data to start allocation calculation"
# #     }
# ]
#openapi_tags=tags_metadata, 

app = FastAPI(title="washingtonsilver", docs_url="/api/docs", openapi_url="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="WashingtonSilver project",
        version="1.0.1",
        description="Api documentation for LDT 2024",
        routes=app.routes,
    )
    oauth2_scheme = {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "auth/token",
                "scopes": {}
            }
        }
    }
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = oauth2_scheme
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(category_router, prefix="/api/category", tags=["category"])
app.include_router(allocation_router, prefix="/api/allocation", tags=["allocation"])
app.include_router(prediction_router, prefix="/api/predict", tags=["prediction"])
app.include_router(billsandrefs_router, prefix="/api/bills", tags=["bills_and_refs"])

if __name__ == "__main__":
    from main import app
    uvicorn.run("main:app", host=os.getenv("LOCALHOST", "127.0.0.1"), port=8888, reload=True)
