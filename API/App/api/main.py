from fastapi import FastAPI
import uvicorn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from API.App.api.routes.user import user_router
from API.App.api.routes.auth import auth_router
from API.App.api.routes.category import category_router
from API.App.api.routes.allocation import allocation_router
from API.App.api.routes.prediction import prediction_router
from API.App.api.routes.bills_and_refs import billsandrefs_router
from fastapi.openapi.utils import get_openapi

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

app = FastAPI(title="washingtonsilver")

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(category_router, prefix="/category", tags=["category"])
app.include_router(allocation_router, prefix="/allocation", tags=["allocation"])
app.include_router(prediction_router, prefix="/predict", tags=["prediction"])
app.include_router(billsandrefs_router, prefix="/bills", tags=["bills_and_refs"])

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=8000, workers=1)
