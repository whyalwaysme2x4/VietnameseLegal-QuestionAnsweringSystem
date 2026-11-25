"""Published-repo entry point; W08 canonical evidence is Evidence/W08."""
import runpy
from pathlib import Path

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1]/'Evidence/tools/validate_w08.py'),run_name='__main__')
