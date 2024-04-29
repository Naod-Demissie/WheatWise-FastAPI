import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, diagnosis, user, analytics
from app.services.diagnosis import DiagnosisServices
from app.services.user import UserServices
from app.version import __version__


load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
model = DiagnosisServices.load_model(model_path=MODEL_PATH)

UserServices.create_default_user()

app = FastAPI(
    title="WheatNet API",
    description="An API for classifying wheat diseases from images.",
    version=__version__,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(diagnosis.router)
app.include_router(analytics.router)

