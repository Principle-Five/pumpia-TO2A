"""
Collection for TO2A phantom.
"""

from pumpia.module_handling.module_collections import (OutputFrame,
                                                       BaseCollection)
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.widgets.viewers import BaseViewer
from pumpia.file_handling.dicom_structures import Series

from pumpia_to2a.to2a_context import TO2AContextManagerGenerator
from pumpia_to2a.modules.slice_width import TO2ASliceWidth
from pumpia_to2a.modules.phantom_width import TO2APhantomWidth
from pumpia_to2a.modules.resolution import TO2AResolution


class TO2ACollection(BaseCollection):
    """
    Collection for TO2A phantom.
    """
    context_manager_generator = TO2AContextManagerGenerator()

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    slice_width = TO2ASliceWidth()
    phantom_width = TO2APhantomWidth()
    resolution = TO2AResolution()

    summary = OutputFrame()
    results = OutputFrame()

    def load_outputs(self):
        self.summary.register_output(self.slice_width.slice_width)
        self.summary.register_output(self.phantom_width.average_width)
        self.summary.register_output(self.resolution.phase_dir)
        self.summary.register_output(self.resolution.phase_2)
        self.summary.register_output(self.resolution.phase_1_5)
        self.summary.register_output(self.resolution.phase_1)
        self.summary.register_output(self.resolution.freq_2)
        self.summary.register_output(self.resolution.freq_1_5)
        self.summary.register_output(self.resolution.freq_1)

        self.results.register_output(self.slice_width.expected_width)
        self.results.register_output(self.slice_width.inside_wedge_width)
        self.results.register_output(self.slice_width.outside_wedge_width)
        self.results.register_output(self.slice_width.slice_width)
        self.results.register_output(self.phantom_width.width_12_6)
        self.results.register_output(self.phantom_width.width_1_7)
        self.results.register_output(self.phantom_width.width_2_8)
        self.results.register_output(self.phantom_width.width_3_9)
        self.results.register_output(self.phantom_width.width_4_10)
        self.results.register_output(self.phantom_width.width_5_11)
        self.results.register_output(self.phantom_width.average_width)
        self.results.register_output(self.resolution.phase_dir)
        self.results.register_output(self.resolution.phase_pix)
        self.results.register_output(self.resolution.phase_2)
        self.results.register_output(self.resolution.phase_1_5)
        self.results.register_output(self.resolution.phase_1)
        self.results.register_output(self.resolution.freq_pix)
        self.results.register_output(self.resolution.freq_2)
        self.results.register_output(self.resolution.freq_1_5)
        self.results.register_output(self.resolution.freq_1)

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
