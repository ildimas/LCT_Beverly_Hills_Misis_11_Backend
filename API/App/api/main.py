from fastapi import FastAPI
import uvicorn
from routes import auth
from fastapi.openapi.utils import get_openapi
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.mount("/auth", auth.auth_app)

@app.get("/")
async def root():
    return {"message": "alive"}


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=8000, workers=1)