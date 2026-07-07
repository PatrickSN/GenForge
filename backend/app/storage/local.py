from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings


class LocalObjectStorage:
    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir or get_settings().storage_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile, namespace: str) -> tuple[Path, int, str]:
        filename = upload.filename or "upload.vcf"
        safe_suffix = ".vcf.gz" if filename.lower().endswith(".vcf.gz") else Path(filename).suffix
        safe_suffix = safe_suffix or ".vcf"
        target_dir = self.root_dir / namespace
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{uuid.uuid4()}{safe_suffix}"

        checksum = hashlib.sha256()
        size = 0
        with target_path.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                checksum.update(chunk)
                output.write(chunk)
        await upload.seek(0)
        return target_path, size, checksum.hexdigest()
