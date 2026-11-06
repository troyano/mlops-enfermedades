"""Persistencia de consultas en un archivo JSON (lista), con bloqueo y escritura atómica."""

import fcntl
import json
import os
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from diagnostico_api.schemas import Consulta


class ConsultaStorage:
    """Guarda y lee consultas en `<directorio>/consultas.json`."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._path = directory / "consultas.json"
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    @contextmanager
    def _exclusive(self) -> Iterator[None]:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._lock, open(self._dir / ".consultas.lock", "w") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file, fcntl.LOCK_UN)

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        return data if isinstance(data, list) else []

    def _write(self, items: list[dict[str, Any]]) -> None:
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self._path)

    def add(self, build: Callable[[str], Consulta]) -> Consulta:
        """Asigna el siguiente id (C-0001...), construye la consulta y la guarda."""
        with self._exclusive():
            items = self._read()
            last = max((int(i["id"].split("-")[1]) for i in items), default=0)
            consulta = build(f"C-{last + 1:04d}")
            items.append(consulta.model_dump(mode="json"))
            self._write(items)
            return consulta

    def list(self, limit: int = 100) -> list[Consulta]:
        """Consultas más recientes primero."""
        with self._exclusive():
            items = self._read()
        return [Consulta.model_validate(i) for i in reversed(items)][:limit]
