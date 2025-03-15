import sys
from pathlib import Path


if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from pumpia_to2a.to2a_collection import TO2ACollection

TO2ACollection.run()
