import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from routes.telegram import search, auth

app = FastAPI(
    title="Telethon Userbot", version="0.0.0"
)

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    app.include_router(search.router)
    app.include_router(auth.router)
    logger.info(f"Startup")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutdown")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=False)
