#!/usr/bin/env python3
"""Executa todos os testes do TESTEPERSONALIDADE."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    print("\n▶ pytest (suite completa)")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
        cwd=str(ROOT),
        env=env,
    )
    if result.returncode == 0:
        print("\n✓ Todos os testes passaram")
        return 0
    print("\n✗ Alguns testes falharam")
    return 1


if __name__ == "__main__":
    sys.exit(main())