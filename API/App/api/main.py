from fastapi import FastAPI
from App.api.routes import auth

app = FastAPI()
app.mount(app=auth.auth_app, path="/auth")

@app.get("/")
async def root():
    return {"message": "alive"}