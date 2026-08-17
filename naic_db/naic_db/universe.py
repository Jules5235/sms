"""Load AEX / BEL 20 universe from YAML config."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

UNIVERSE_PATH = Path(__file__).resolve().parent.parent / "config" / "universes.yaml"


@dataclass(frozen=True)
class InstrumentDef:
    ticker: str
    name: str
    exchange: str
    index_code: str
    yahoo_symbol: str
    stooq_symbol: str
    weight_pct: float | None = None


def load_universe(path: Path | None = None) -> list[InstrumentDef]:
    config_path = path or UNIVERSE_PATH
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    instruments: list[InstrumentDef] = []

    for index_code, index_data in raw["indices"].items():
        exchange = index_data["exchange"]
        for member in index_data["members"]:
            instruments.append(
                InstrumentDef(
                    ticker=member["ticker"],
                    name=member["name"],
                    exchange=exchange,
                    index_code=index_code,
                    yahoo_symbol=member["yahoo"],
                    stooq_symbol=member["stooq"],
                    weight_pct=member.get("weight"),
                )
            )
    return instruments
