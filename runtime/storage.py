from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalJsonStore:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.cycles_dir = self.base_dir / "cycle_records"
        self.memory_dir = self.base_dir / "memory_records"
        self.profiles_dir = self.base_dir / "profiles"
        self.cycles_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def load_or_create_user_profile(self, user_id: str = "local-user") -> dict[str, Any]:
        path = self.profiles_dir / f"{user_id}.json"
        if path.exists():
            return self._read_json(path)
        profile = {
            "user_id": user_id,
            "scenario_scope": "money_income",
            "created_at": None,
            "latest_cycle_id": None,
            "memory_record_id": f"memory-{user_id}",
        }
        self._write_json(path, profile)
        return profile

    def save_user_profile(self, profile: dict[str, Any]) -> None:
        path = self.profiles_dir / f"{profile['user_id']}.json"
        self._write_json(path, profile)

    def load_or_create_memory_record(self, user_id: str) -> dict[str, Any]:
        path = self.memory_dir / f"{user_id}.json"
        if path.exists():
            return self._read_json(path)
        record = {
            "memory_record_id": f"memory-{user_id}",
            "user_id": user_id,
            "cycle_count": 0,
            "last_mechanism_label": None,
            "repeated_mechanism_markers": [],
            "repeated_barrier_markers": [],
            "shift_history": [],
            "last_resolution_status": None,
            "updated_at": None,
        }
        self._write_json(path, record)
        return record

    def save_memory_record(self, record: dict[str, Any]) -> None:
        path = self.memory_dir / f"{record['user_id']}.json"
        self._write_json(path, record)

    def save_cycle_record(self, record: dict[str, Any]) -> None:
        path = self.cycles_dir / f"{record['cycle_id']}.json"
        self._write_json(path, record)

    def load_cycle_record(self, cycle_id: str) -> dict[str, Any]:
        path = self.cycles_dir / f"{cycle_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Unknown cycle_id: {cycle_id}")
        return self._read_json(path)

    def list_cycle_records(self) -> list[dict[str, Any]]:
        records = [self._read_json(path) for path in self.cycles_dir.glob("*.json")]
        return sorted(records, key=lambda item: item["updated_at"], reverse=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")
