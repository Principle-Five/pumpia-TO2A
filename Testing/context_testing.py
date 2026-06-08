import sys
from pathlib import Path

from pumpia.module_handling.modules import BaseModule
from pumpia.module_handling.fields.viewer_fields import MonochromeDicomViewerField

if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from pumpia_to2a.to2a_context import TO2AContextManager


class ContextTest(BaseModule):
    context_manager = TO2AContextManager()

    main = MonochromeDicomViewerField(0, 0)

    def analyse(self, batch: bool = False):
        pass


if __name__ == "__main__":
    ContextTest.run()
