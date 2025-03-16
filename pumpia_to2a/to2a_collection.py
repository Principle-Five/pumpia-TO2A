"""
Collection for TO2A phantom.
"""

from pumpia.module_handling.module_collections import (OutputFrame,
                                                       BaseCollection)
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.widgets.viewers import BaseViewer
from pumpia.file_handling.dicom_structures import Series

from .to2a_context import TO2AContextManagerGenerator
from .modules.slice_width import TO2ASliceWidth
from .modules.phantom_width import TO2APhantomWidth
from .modules.resolution import TO2AResolution


class TO2ACollection(BaseCollection):
    """
    Collection for TO2A phantom.
    """
    context_manager_generator = TO2AContextManagerGenerator()

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    slice_width = TO2ASliceWidth()
    phantom_width = TO2APhantomWidth()
    resolution = TO2AResolution()

    results = OutputFrame()

    def load_outputs(self):
        self.results.register_output(self.slice_width.slice_width)
        self.results.register_output(self.phantom_width.average_width)
        self.results.register_output(self.resolution.horizontal_2)
        self.results.register_output(self.resolution.horizontal_1_5)
        self.results.register_output(self.resolution.horizontal_1)
        self.results.register_output(self.resolution.vertical_2)
        self.results.register_output(self.resolution.vertical_1_5)
        self.results.register_output(self.resolution.vertical_1)

    def on_image_load(self, viewer: BaseViewer) -> None:
        if viewer is self.viewer:
            if self.viewer.image is not None:
                image = self.viewer.image
                if isinstance(image, Series):
                    slice_index = image.num_slices // 2
                    image = image.instances[slice_index]
                self.slice_width.viewer.load_image(image)
                self.phantom_width.viewer.load_image(image)
                self.resolution.viewer.load_image(image)
