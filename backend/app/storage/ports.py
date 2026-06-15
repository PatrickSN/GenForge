from __future__ import annotations

from pathlib import Path
from typing import Protocol

from fastapi import UploadFile


class ObjectStorage(Protocol):
    async def save_upload(self, upload: UploadFile, namespace: str) -> tuple[Path, int, str]:
        """Persist an upload and return path, size in bytes and SHA-256 checksum."""
