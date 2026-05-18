"""Loader y validación de params.toml + prices.toml.

Único punto de entrada para acceder a la fuente de verdad. Cualquier script
del pipeline (BOM generator, budget generator, build123d, etc.) llama a
`load_params()` y `load_prices()` desde aquí — nunca lee los TOML directamente.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CAD_DIR = Path(__file__).resolve().parent
REPO_ROOT = CAD_DIR.parent
PARAMS_PATH = CAD_DIR / "params.toml"
PRICES_PATH = CAD_DIR / "prices.toml"


@dataclass(frozen=True)
class Profile:
    name: str
    kg_per_m: float
    width_mm: float
    height_mm: float
    thickness_mm: float
    shape: str  # hss | c_channel | i_beam | angle


@dataclass(frozen=True)
class Params:
    raw: dict[str, Any]
    profiles: dict[str, Profile] = field(default_factory=dict)

    @property
    def width_m(self) -> float:
        return float(self.raw["platform"]["width_m"])

    @property
    def depth_m(self) -> float:
        return float(self.raw["platform"]["depth_m"])

    @property
    def enclosed_depth_m(self) -> float:
        return float(self.raw["envelope"]["enclosed_depth_m"])

    @property
    def terrace_depth_m(self) -> float:
        return float(self.raw["envelope"]["terrace_depth_m"])

    @property
    def apex_height_m(self) -> float:
        return float(self.raw["aframe"]["apex_height_m"])

    @property
    def half_span_m(self) -> float:
        return self.width_m / 2.0

    @property
    def rafter_length_m(self) -> float:
        from math import hypot
        return hypot(self.half_span_m, self.apex_height_m)

    @property
    def column_heights_m(self) -> list[list[float]]:
        return [list(map(float, row)) for row in self.raw["columns"]["heights_m"]]

    @property
    def column_count(self) -> int:
        cols = int(self.raw["platform"]["column_grid_cols"])
        rows = int(self.raw["platform"]["column_grid_rows"])
        return cols * rows

    @property
    def total_column_length_m(self) -> float:
        return sum(h for row in self.column_heights_m for h in row)

    @property
    def anchor_count(self) -> int:
        return self.column_count * int(self.raw["columns"]["anchors_per_column"])

    def profile(self, name: str) -> Profile:
        if name not in self.profiles:
            raise KeyError(f"perfil desconocido: {name} (definir en params.toml [profiles.*])")
        return self.profiles[name]


@dataclass(frozen=True)
class Prices:
    raw: dict[str, Any]

    @property
    def currency(self) -> str:
        return str(self.raw["currency"])

    @property
    def indirect_pct(self) -> float:
        return float(self.raw["overhead"]["indirect_pct"])

    @property
    def contingency_pct(self) -> float:
        return float(self.raw["overhead"]["contingency_pct"])

    @property
    def iva_pct(self) -> float:
        return float(self.raw["overhead"]["iva_pct"])

    @property
    def usd_cop(self) -> float:
        return float(self.raw["exchange_rate_usd_cop"])

    def get(self, section: str, key: str, level: str = "mid") -> float:
        node = self.raw[section][key]
        return float(node[level])

    def unit(self, section: str, key: str) -> str:
        return str(self.raw[section][key].get("unit", "u"))


def load_params(path: Path = PARAMS_PATH) -> Params:
    with path.open("rb") as fh:
        data = tomllib.load(fh)

    profiles: dict[str, Profile] = {}
    for name, body in data.get("profiles", {}).items():
        profiles[name] = Profile(
            name=name,
            kg_per_m=float(body["kg_per_m"]),
            width_mm=float(body["width_mm"]),
            height_mm=float(body["height_mm"]),
            thickness_mm=float(body["thickness_mm"]),
            shape=str(body["shape"]),
        )

    _validate_params(data, profiles)
    return Params(raw=data, profiles=profiles)


def load_prices(path: Path = PRICES_PATH) -> Prices:
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    _validate_prices(data)
    return Prices(raw=data)


def _validate_params(data: dict[str, Any], profiles: dict[str, Profile]) -> None:
    required_sections = ["platform", "columns", "aframe", "envelope", "platform_structure"]
    for sec in required_sections:
        if sec not in data:
            raise ValueError(f"params.toml: falta sección [{sec}]")

    cols = int(data["platform"]["column_grid_cols"])
    rows = int(data["platform"]["column_grid_rows"])
    heights = data["columns"]["heights_m"]
    if len(heights) != rows:
        raise ValueError(f"columns.heights_m: esperan {rows} filas, hay {len(heights)}")
    for i, row in enumerate(heights):
        if len(row) != cols:
            raise ValueError(f"columns.heights_m[{i}]: esperan {cols} columnas, hay {len(row)}")

    referenced = {
        data["columns"]["profile"],
        data["aframe"]["rafter_profile"],
        data["aframe"]["tie_beam_profile"],
        data["aframe"]["ridge_profile"],
        data["aframe"]["purlin_profile"],
        data["platform_structure"]["main_beam_profile"],
        data["platform_structure"]["secondary_joist_profile"],
        data["platform_structure"]["bracing_profile"],
    }
    missing = referenced - set(profiles.keys())
    if missing:
        raise ValueError(f"params.toml: perfiles referenciados sin definir: {sorted(missing)}")


def _validate_prices(data: dict[str, Any]) -> None:
    if "overhead" not in data:
        raise ValueError("prices.toml: falta sección [overhead]")
    for key in ("indirect_pct", "contingency_pct", "iva_pct"):
        if key not in data["overhead"]:
            raise ValueError(f"prices.toml: falta overhead.{key}")


if __name__ == "__main__":
    p = load_params()
    pr = load_prices()
    print(f"Plataforma: {p.width_m} × {p.depth_m} m")
    print(f"Apex A-frame: {p.apex_height_m} m")
    print(f"Rafter (calculado): {p.rafter_length_m:.3f} m")
    print(f"Columnas: {p.column_count} × variable height")
    print(f"Largo total columnas: {p.total_column_length_m:.1f} m")
    print(f"Anclajes: {p.anchor_count}")
    print(f"Perfiles definidos: {sorted(p.profiles.keys())}")
    print(f"Precios cargados: {len([k for k in pr.raw if not k.startswith('_')])} secciones")
