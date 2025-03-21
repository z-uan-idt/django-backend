from io import BytesIO
from django.conf import settings
from tempfile import TemporaryFile
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from .backblaze_b2 import BackBlazeB2


@deconstructible
class B2Storage(Storage):
    def __init__(self, account_id=None, app_key=None, bucket_name=None, bucket_id=None):
        overrides = locals()
        defaults = {
            "account_id": settings.BACKBLAZEB2_ACCOUNT_ID,
            "app_key": settings.BACKBLAZEB2_APP_KEY,
            "bucket_name": settings.BACKBLAZEB2_BUCKET_NAME,
            "bucket_id": settings.BACKBLAZEB2_BUCKET_ID,
        }
        kwargs = {k: overrides[k] or v for k, v in defaults.items()}
        self.b2 = BackBlazeB2(**kwargs)

    def save(self, name, content, max_length=None):
        resp = self.b2.upload_file(name, content)
        if "fileName" in resp:
            return resp["fileName"]
        else:
            pass

    def exists(self, name):
        return False

    def _temporary_storage(self, contents):
        conent_file = TemporaryFile(contents, "r+")
        return conent_file

    def open(self, name, mode="rb"):
        resp = self.b2.download_file(name)

        output = BytesIO()
        output.write(resp)
        output.seek(0)
        return File(output, name)

    def url(self, name):
        return self.b2.get_file_url(name)
