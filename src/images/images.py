from minio import Minio
import os

from minio.api import timedelta


class Images:
    """Images class to handle Minio connection and operations"""

    bucket = os.getenv("MINIO_IMAGES_BUCKET") or ""

    def __init__(self):
        self.minio = Minio(
            os.getenv("MINIO_DOMAIN") or "",
            access_key=os.getenv("MINIO_ACCESS_KEY") or "",
            secret_key=os.getenv("MINIO_SECRET_KEY") or "",
            secure=True,
        )

    # Singleton instance attribute
    _instance = None

    @staticmethod
    def instance():
        """Singleton: get the database instance engine or create a new one"""

        if Images._instance is None:
            Images._instance = Images()

        return Images._instance

    def get_upload_url(self, id, extension):
        return self.minio.get_presigned_url(
            "PUT",
            self.bucket,
            f"{id}.{extension}",
            expires=timedelta(hours=1),
        )
