import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def run_cmd(command: list[str], cwd: Optional[str] = None, check: bool = False) -> Dict[str, Any]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    output = {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if check and result.returncode != 0:
        raise RuntimeError(json.dumps(output, indent=2))
    return output


def read_text(path: str, default: str = "") -> str:
    p = Path(path)
    if not p.exists():
        return default
    return p.read_text(encoding="utf-8", errors="replace")


def write_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def write_json(path: str, data: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
