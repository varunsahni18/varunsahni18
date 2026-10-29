"""Build all three portfolio directions and their comparison page."""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parent
runpy.run_path(str(ROOT/'build-versions.py'),run_name='__main__')
runpy.run_path(str(ROOT/'build-comparison.py'),run_name='__main__')
