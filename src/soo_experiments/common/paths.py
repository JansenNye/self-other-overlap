"""Repository-relative experiment paths; scratch storage is configurable."""
import os
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
BENCHMARKS_DIR = REPO_ROOT / "benchmarks"
SCRATCH_DIR = Path(os.environ.get("SELFCONCEPT_SCRATCH", REPO_ROOT / "artifacts"))
def experiment_dir(name: str) -> Path:
    return EXPERIMENTS_DIR / name
def benchmark_dir(name: str) -> Path:
    return BENCHMARKS_DIR / name
def scratch_dir(name: str) -> Path:
    return SCRATCH_DIR / name
