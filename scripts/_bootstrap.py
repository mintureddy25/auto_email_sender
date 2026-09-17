"""Makes `import src.*` work for scripts living in this folder.

Python puts the *script's* directory on sys.path, not the project root, so
`python3 scripts/foo.py` cannot see `src/` without this. Every script here
imports it first:

    import _bootstrap  # noqa: F401  (must precede any `src.` import)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
