"""Сверка того, что фронтенд зовёт, с опубликованным контрактом API.

Фронтенд знает URL-пространство в `frontend/src/shared/api/backend/paths.js`.
Контракт бэкенда лежит в `ProductSpecification/api-specs/*.yaml`.

Запуск: python scripts/check_api_contract.py [--openapi файл.json] [--update-baseline]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATHS = ROOT / "frontend/src/shared/api/backend/paths.js"
# Legacy sibling used in some checkouts; prefer paths.js.
ENDPOINTS_TS = ROOT / "frontend/src/shared/api/endpoints.ts"
PATHS_TS = ROOT / "frontend/src/shared/api/backend/paths.ts"
SPECS = ROOT / "ProductSpecification/api-specs"
BASELINE = ROOT / "scripts/api-contract-baseline.json"

PARAM = re.compile(r"\$\{[^}]*\}")
TEMPLATE = re.compile(r"`([^`]*)`")
BRACED = re.compile(r"\{[^}]+\}")
V1_CONST = re.compile(r"const\s+V1\s*=\s*['\"]([^'\"]+)['\"]")


def _paths_file() -> Path:
    if PATHS.exists():
        return PATHS
    if PATHS_TS.exists():
        return PATHS_TS
    raise SystemExit("Не найден frontend/src/shared/api/backend/paths.js")


def frontend_paths() -> set[str]:
    source_path = _paths_file()
    text = source_path.read_text(encoding="utf-8")
    version_match = V1_CONST.search(text)
    prefix = version_match.group(1) if version_match else "/api/v1"

    # Optional endpoints.ts may declare API_VERSION for older layouts.
    if ENDPOINTS_TS.exists():
        version = re.search(
            r"API_VERSION\s*=\s*['\"]([^'\"]+)['\"]",
            ENDPOINTS_TS.read_text(encoding="utf-8"),
        )
        if version:
            prefix = f"/api/{version.group(1)}"

    paths: set[str] = set()
    for raw in TEMPLATE.findall(text):
        if "${V1}" not in raw and not raw.startswith(prefix):
            continue
        path = PARAM.sub("{}", raw.replace("${V1}", prefix))
        paths.add(path.split("?")[0])
    if not paths:
        raise SystemExit(f"В {source_path.relative_to(ROOT)} не найдено ни одного пути")
    return paths


def contract_paths(argv: list[str]) -> set[str]:
    paths: set[str] = set()
    for spec in sorted(SPECS.glob("*.yaml")):
        document = yaml.safe_load(spec.read_text(encoding="utf-8")) or {}
        paths.update(BRACED.sub("{}", path) for path in (document.get("paths") or {}))

    if "--openapi" in argv:
        live = json.loads(Path(argv[argv.index("--openapi") + 1]).read_text(encoding="utf-8"))
        paths.update(BRACED.sub("{}", path) for path in live.get("paths", {}))
    return paths


def main() -> int:
    argv = sys.argv[1:]
    front = frontend_paths()
    contract = contract_paths(argv)
    missing = sorted(front - contract)

    if "--update-baseline" in argv:
        BASELINE.write_text(
            json.dumps({"not_in_contract": missing}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Записано путей вне контракта: {len(missing)}")
        return 0

    known = set()
    if BASELINE.exists():
        known = set(json.loads(BASELINE.read_text(encoding="utf-8"))["not_in_contract"])
    new = [path for path in missing if path not in known]
    landed = sorted(known - set(missing))

    print(f"Фронтенд зовёт путей: {len(front)}. Контракт описывает: {len(contract)}.")
    print(f"Вне контракта: {len(missing)}.")

    if landed:
        print("\nЭти пути появились в контракте — уберите их из scripts/api-contract-baseline.json:")
        for path in landed:
            print(f"  {path}")
    if new:
        print("\nФронтенд зовёт путь, которого нет ни в контракте, ни в списке ожидаемых:")
        for path in new:
            print(f"  {path}")

    return 1 if (new or landed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
