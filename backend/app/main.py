from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .auth import router as auth_router

# Create tables
Base.metadata.create_all(bind=engine)

from .exception_handlers import validation_exception_handler, sqlalchemy_exception_handler, global_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(
    title="AI Foundry Platform",
    description="Unified API for BankCall AI and Anti-Fraud AI",
    version="1.0.0"
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS Configuration
origins = [
    "http://localhost:3000",  # Frontend
    "http://localhost:8000",  # Backend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

from .modules.antifraud import router as antifraud_router
from .modules.bankcall import router as bankcall_router

app.include_router(antifraud_router, prefix="/api/antifraud", tags=["Anti-Fraud AI"])
app.include_router(bankcall_router, prefix="/api/bankcall", tags=["BankCall AI"])

from .api_keys import router as api_key_router
app.include_router(api_key_router, prefix="/api/keys", tags=["API Keys"])

from .webhooks import router as webhook_router
app.include_router(webhook_router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    return {"message": "Welcome to AI Foundry Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
