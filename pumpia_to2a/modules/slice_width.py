"""
Slice width using TO2A wedges
"""
import math
import numpy as np

from pumpia.module_handling.modules import PhantomModule
from pumpia.module_handling.in_outs.roi_ios import BaseInputROI, InputRectangleROI
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.module_handling.in_outs.simple import FloatInput, PercInput, FloatOutput, StringOutput
from pumpia.image_handling.roi_structures import RectangleROI
from pumpia.file_handling.dicom_structures import Series
from pumpia.utilities.array_utils import nth_max_widest_peak

from ..to2a_context import TO2AContextManagerGenerator, TO2AContext

# distances in mm
INSIDE_OFFSET = 41
OUTSIDE_OFFSET = 62
ROI_WIDTH = 14
ROI_LENGTH = 70


class TO2ASliceWidth(PhantomModule):
    """
    Calculates slice width using TO2A wedges
    """
    context_manager_generator = TO2AContextManagerGenerator()

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    tan_theta = FloatInput(0.25, verbose_name="Tan of wedge angle")
    max_perc = PercInput(50, verbose_name="Width position (% of max)")

    wedge_dir = StringOutput(verbose_name="Wedge Direction")
    expected_width = FloatOutput()
    inside_wedge_width = FloatOutput()
    outside_wedge_width = FloatOutput()
    slice_width = FloatOutput()

    inside_wedge = InputRectangleROI()
    outside_wedge = InputRectangleROI()

    def draw_rois(self, context: TO2AContext, batch: bool = False) -> None:

        if self.viewer.image is not None:
            image = self.viewer.image

            if isinstance(image, Series):
                slice_index = image.num_slices // 2
                image = image.instances[slice_index]

            pixel_size = image.pixel_size
            pixel_height = pixel_size[1]
            pixel_width = pixel_size[2]

            self.expected_width.value = pixel_size[0]

            if context.wedges_side == "bottom" or context.wedges_side == "top":
                self.wedge_dir.value = "Horizontal"
                box_width = ROI_WIDTH / pixel_height
                box_length = ROI_LENGTH / pixel_width
                inside_pix_offset = INSIDE_OFFSET / pixel_height
                outside_pix_offset = OUTSIDE_OFFSET / pixel_height

                inside_xmin = outside_xmin = round(context.xcent - box_length / 2)
                inside_xmax = outside_xmax = round(context.xcent + box_length / 2)

                if context.wedges_side == "bottom":
                    inside_ymin = round(context.ycent + inside_pix_offset)
                    inside_ymax = round(context.ycent + inside_pix_offset + box_width)
                    outside_ymin = round(context.ycent + outside_pix_offset)
                    outside_ymax = round(context.ycent + outside_pix_offset + box_width)
                else:
                    inside_ymin = round(context.ycent - inside_pix_offset - box_width)
                    inside_ymax = round(context.ycent - inside_pix_offset)
                    outside_ymin = round(context.ycent - outside_pix_offset - box_width)
                    outside_ymax = round(context.ycent - outside_pix_offset)
            else:
                self.wedge_dir.value = "Vertical"
                box_width = ROI_WIDTH / pixel_width
                box_length = ROI_LENGTH / pixel_height
                inside_pix_offset = INSIDE_OFFSET / pixel_width
                outside_pix_offset = OUTSIDE_OFFSET / pixel_width

                inside_ymin = outside_ymin = round(context.ycent - box_length / 2)
                inside_ymax = outside_ymax = round(context.ycent + box_length / 2)

                if context.wedges_side == "right":
                    inside_xmin = round(context.xcent + inside_pix_offset)
                    inside_xmax = round(context.xcent + inside_pix_offset + box_width)
                    outside_xmin = round(context.xcent + outside_pix_offset)
                    outside_xmax = round(context.xcent + outside_pix_offset + box_width)
                else:
                    inside_xmin = round(context.xcent - inside_pix_offset - box_width)
                    inside_xmax = round(context.xcent - inside_pix_offset)
                    outside_xmin = round(context.xcent - outside_pix_offset - box_width)
                    outside_xmax = round(context.xcent - outside_pix_offset)

            inside_roi = RectangleROI(image,
                                      inside_xmin,
                                      inside_ymin,
                                      inside_xmax,
                                      inside_ymax,
                                      slice_num=image.current_slice,
                                      replace=True)
            self.inside_wedge.register_roi(inside_roi)

            outside_roi = RectangleROI(image,
                                       outside_xmin,
                                       outside_ymin,
                                       outside_xmax,
                                       outside_ymax,
                                       slice_num=image.current_slice,
                                       replace=True)
            self.outside_wedge.register_roi(outside_roi)

    def post_roi_register(self, roi_input: BaseInputROI):
        if (roi_input.roi is not None
            and self.manager is not None
                and (roi_input is self.inside_wedge or roi_input is self.outside_wedge)):
            self.manager.add_roi(roi_input.roi)

    def link_rois_viewers(self):
        self.inside_wedge.viewer = self.viewer
        self.outside_wedge.viewer = self.viewer

    def analyse(self, batch: bool = False):
        if (self.inside_wedge.roi is not None
            and self.outside_wedge.roi is not None
                and self.viewer.image is not None):
            if self.wedge_dir.value == "Vertical":
                inside_prof = np.abs(np.diff(self.inside_wedge.roi.v_profile))
                outide_prof = np.abs(np.diff(self.outside_wedge.roi.v_profile))
                pix_size = self.viewer.image.pixel_size[1]
            else:
                inside_prof = np.abs(np.diff(self.inside_wedge.roi.h_profile))
                outide_prof = np.abs(np.diff(self.outside_wedge.roi.h_profile))
                pix_size = self.viewer.image.pixel_size[2]

            divisor = 100 / self.max_perc.value

            inside_fwhm = nth_max_widest_peak(inside_prof, divisor)
            outside_fwhm = nth_max_widest_peak(outide_prof, divisor)

            tan_theta = self.tan_theta.value

            inside_width = inside_fwhm.difference * tan_theta * pix_size
            outside_width = outside_fwhm.difference * tan_theta * pix_size

            self.inside_wedge_width.value = inside_width
            self.outside_wedge_width.value = outside_width

            self.slice_width.value = math.sqrt(inside_width * outside_width)
