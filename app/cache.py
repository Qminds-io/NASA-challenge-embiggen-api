from __future__ import annotations

import json
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Mapping, MutableMapping, Optional


@dataclass
class CachedPayload:
    body: bytes
    headers: Mapping[str, str]
    expires_at: float

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class FileCache:
    """Cache minimo basado en archivos para respuestas binarias."""

    def __init__(self, base_dir: Path, ttl_seconds: int) -> None:
        self.base_dir = base_dir
        self.ttl_seconds = ttl_seconds
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, key: str) -> str:
        return sha256(key.encode("utf-8")).hexdigest()

    def _payload_path(self, key: str) -> Path:
        return self.base_dir / f"{self._hash_key(key)}.bin"

    def _metadata_path(self, key: str) -> Path:
        return self.base_dir / f"{self._hash_key(key)}.json"

    def get(self, key: str) -> Optional[CachedPayload]:
        payload_path = self._payload_path(key)
        metadata_path = self._metadata_path(key)
        if not payload_path.exists() or not metadata_path.exists():
            return None

        raw_meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        cached = CachedPayload(
            body=payload_path.read_bytes(),
            headers=raw_meta.get("headers", {}),
            expires_at=raw_meta.get("expiresAt", 0),
        )
        if cached.is_expired:
            try:
                payload_path.unlink()
                metadata_path.unlink()
            except OSError:
                pass
            return None
        return cached

    def set(self, key: str, body: bytes, headers: Mapping[str, str]) -> None:
        metadata: MutableMapping[str, object] = {
            "headers": dict(headers),
            "expiresAt": time.time() + self.ttl_seconds,
        }
        self._payload_path(key).write_bytes(body)
        self._metadata_path(key).write_text(json.dumps(metadata), encoding="utf-8")

    def clear(self) -> None:
        for file in self.base_dir.glob("*"):
            try:
                file.unlink()
            except OSError:
                pass
