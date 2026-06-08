"""
Collection for TO2A phantom.
"""

from pumpia.module_handling.collections import BaseCollection
from pumpia.module_handling.fields.windows import FieldWindow
from pumpia.module_handling.fields.viewer_fields import MonochromeDicomViewerField
from pumpia.widgets.viewers import MonochromeDicomViewer
from pumpia.file_handling.dicom_structures import Series

from pumpia_to2a.to2a_context import TO2AContextManager
from pumpia_to2a.modules.slice_width import TO2ASliceWidth
from pumpia_to2a.modules.phantom_width import TO2APhantomWidth
from pumpia_to2a.modules.resolution import TO2AResolution


class TO2ACollection(BaseCollection):
    """
    Collection for TO2A phantom.
    """
    context_manager = TO2AContextManager()
    title = "TO2A Collection"

    viewer = MonochromeDicomViewerField(row=0, column=0)

    slice_width = TO2ASliceWidth()
    phantom_width = TO2APhantomWidth()
    resolution = TO2AResolution()

    summary = FieldWindow(slice_width.fields.slice_width,
                          phantom_width.fields.average_width,
                          resolution.fields.phase_dir,
                          resolution.fields.phase_2,
                          resolution.fields.phase_1_5,
                          resolution.fields.phase_1,
                          resolution.fields.freq_2,
                          resolution.fields.freq_1_5,
                          resolution.fields.freq_1)
    results = FieldWindow(slice_width.fields.expected_width,
                          slice_width.fields.inside_wedge_width,
                          slice_width.fields.outside_wedge_width,
                          slice_width.fields.slice_width,
                          phantom_width.fields.width_12_6,
                          phantom_width.fields.width_1_7,
                          phantom_width.fields.width_2_8,
                          phantom_width.fields.width_3_9,
                          phantom_width.fields.width_4_10,
                          phantom_width.fields.width_5_11,
                          phantom_width.fields.average_width,
                          resolution.fields.phase_dir,
                          resolution.fields.phase_pix,
                          resolution.fields.phase_2,
                          resolution.fields.phase_1_5,
                          resolution.fields.phase_1,
                          resolution.fields.freq_pix,
                          resolution.fields.freq_2,
                          resolution.fields.freq_1_5,
                          resolution.fields.freq_1)

    def on_image_load(self, viewer: MonochromeDicomViewer) -> None:
        if viewer is self.viewer and self.viewer.image is not None:
            image = self.viewer.image
            if isinstance(image, Series):
                slice_index = image.num_slices // 2
                image = image.instances[slice_index]
            self.slice_width.viewer.load_image(image)
            self.phantom_width.viewer.load_image(image)
            self.resolution.viewer.load_image(image)
