from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings
from app.database import init_database
from app.exceptions import AppError


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    status = 400
    if exc.code == "NOT_FOUND":
        status = 404
    elif exc.code == "CONFLICT":
        status = 409
    return JSONResponse(status_code=status, content={"code": exc.code, "message": exc.message})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
