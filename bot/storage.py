from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Storage:
    path: Path
    _data: dict[str, Any] = field(default_factory=dict)

    def load(self) -> None:
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._data = {"guilds": {}}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")

    def guild(self, guild_id: int) -> dict[str, Any]:
        guilds = self._data.setdefault("guilds", {})
        return guilds.setdefault(str(guild_id), {})
