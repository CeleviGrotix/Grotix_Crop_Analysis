from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.analysis_controller import (
    router as analysis_router
)

app = FastAPI(
    title="Crop Analysis Service",
    version="1.0.0"
)

app.mount(
    "/images",
    StaticFiles(directory="storage/images"),
    name="images"
)

app.include_router(
    analysis_router,
    prefix="/analysis",
    tags=[
        "Crop Analysis"
    ]
)

@app.get("/")
def root():
    return {
        "service": "Crop Analysis Service",
        "status": "running"
    }
