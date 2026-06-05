from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File

import uuid
import os

from app.services.image_analyzer import (
    ImageAnalyzer
)

app = FastAPI()

analyzer = (
    ImageAnalyzer()
)


@app.post(
    "/predict"
)
async def predict(
    image: UploadFile = File(...)
):

    filename = (
        f"{uuid.uuid4()}_"
        f"{image.filename}"
    )

    filepath = os.path.join(
        "storage",
        filename
    )

    with open(
        filepath,
        "wb"
    ) as buffer:

        buffer.write(
            await image.read()
        )

    result = analyzer.analyze(
        filepath
    )

    return result