import os
import uuid

from fastapi import UploadFile


class ImageStorageService:

    STORAGE_PATH = "storage/images"

    def save(
        self,
        image: UploadFile
    ):

        extension = image.filename.split(".")[-1]

        filename = (
            f"{uuid.uuid4()}.{extension}"
        )

        filepath = os.path.join(
            self.STORAGE_PATH,
            filename
        )

        with open(
            filepath,
            "wb"
        ) as buffer:

            buffer.write(
                image.file.read()
            )

        return filepath