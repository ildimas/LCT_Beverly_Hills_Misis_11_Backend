from fastapi import FastAPI
import uvicorn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from API.App.api.routes.user import user_router
from fastapi.openapi.utils import get_openapi

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="washingtonsilver")
app.include_router(user_router, prefix="/user", tags=["user"])


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=8000, workers=1)