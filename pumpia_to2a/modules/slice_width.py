"""
Slice width using TO2A wedges
"""
import math
import numpy as np
from scipy.optimize import curve_fit

from pumpia.module_handling.modules import PhantomModule
from pumpia.module_handling.in_outs.roi_ios import BaseInputROI, InputRectangleROI
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.module_handling.in_outs.simple import FloatInput, PercInput, FloatOutput, StringOutput
from pumpia.image_handling.roi_structures import RectangleROI
from pumpia.file_handling.dicom_structures import Series
from pumpia.utilities.feature_utils import split_gauss_integral

from pumpia_to2a.to2a_context import TO2AContextManagerGenerator, TO2AContext

# distances in mm
INSIDE_OFFSET = 40
OUTSIDE_OFFSET = 61
ROI_WIDTH = 14
ROI_LENGTH = 70


class TO2ASliceWidth(PhantomModule):
    """
    Calculates slice width using TO2A wedges by fitting to a flat top gaussian
    """
    context_manager_generator = TO2AContextManagerGenerator()
    show_draw_rois_button = True
    show_analyse_button = True
    name = "Slice Width"

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    tan_theta = FloatInput(0.25, verbose_name="Tan of wedge angle")
    max_perc = PercInput(50, verbose_name="Width position (% of max)")

    wedge_dir = StringOutput(verbose_name="Wedge Direction")

    expected_width = FloatOutput()
    inside_wedge_width = FloatOutput(reset_on_analysis=True)
    outside_wedge_width = FloatOutput(reset_on_analysis=True)
    slice_width = FloatOutput(reset_on_analysis=True)

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
                                      inside_xmax - inside_xmin,
                                      inside_ymax - inside_ymin,
                                      slice_num=image.current_slice,
                                      replace=True)
            self.inside_wedge.register_roi(inside_roi)

            outside_roi = RectangleROI(image,
                                       outside_xmin,
                                       outside_ymin,
                                       outside_xmax - outside_xmin,
                                       outside_ymax - outside_ymin,
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
                inside_prof = self.inside_wedge.roi.v_profile
                outside_prof = self.outside_wedge.roi.v_profile
                pix_size = self.viewer.image.pixel_size[1]
            else:
                inside_prof = self.inside_wedge.roi.h_profile
                outside_prof = self.outside_wedge.roi.h_profile
                pix_size = self.viewer.image.pixel_size[2]

            inside_prof_diff = np.diff(inside_prof)
            outside_prof_diff = np.diff(outside_prof)

            init_in_max = np.max(inside_prof_diff)
            init_in_min = np.min(inside_prof_diff)
            if abs(init_in_max) > abs(init_in_min):
                init_in_amp = init_in_max
            else:
                init_in_amp = init_in_min
            init_in_bl = np.min(inside_prof)
            init_in_c = self.expected_width.value / 2
            init_in_a = inside_prof_diff.shape[0] / 2 - init_in_c
            init_in_b = inside_prof_diff.shape[0] / 2 + init_in_c
            init_in = (init_in_a, init_in_b, init_in_c, init_in_amp, init_in_bl)
            in_shp = list(inside_prof_diff.shape)
            in_shp[0] = in_shp[0] + 1
            in_indeces = np.indices(in_shp)[0]

            in_fit, _ = curve_fit(split_gauss_integral,
                                  in_indeces,
                                  inside_prof,
                                  init_in)

            init_out_max = np.max(outside_prof_diff)
            init_out_min = np.min(outside_prof_diff)
            if abs(init_out_max) > abs(init_out_min):
                init_out_amp = init_out_max
            else:
                init_out_amp = init_out_min
            init_out_bl = np.min(outside_prof)
            init_out_c = self.expected_width.value / 2
            init_out_a = outside_prof_diff.shape[0] / 2 - init_out_c
            init_out_b = outside_prof_diff.shape[0] / 2 + init_out_c
            init_out = (init_out_a, init_out_b, init_out_c, init_out_amp, init_out_bl)
            out_shp = list(outside_prof_diff.shape)
            out_shp[0] = out_shp[0] + 1
            out_indeces = np.indices(out_shp)[0]

            out_fit, _ = curve_fit(split_gauss_integral,
                                   out_indeces,
                                   outside_prof,
                                   init_out)

            divisor = 100 / self.max_perc.value
            c_coeff = 2 * math.sqrt(2 * math.log(divisor))

            inside_fwhm = abs(in_fit[1] - in_fit[0]) + c_coeff * in_fit[2]
            outside_fwhm = abs(out_fit[1] - out_fit[0]) + c_coeff * out_fit[2]

            tan_theta = self.tan_theta.value

            inside_width = inside_fwhm * tan_theta * pix_size
            outside_width = outside_fwhm * tan_theta * pix_size

            self.inside_wedge_width.value = inside_width
            self.outside_wedge_width.value = outside_width

            self.slice_width.value = math.sqrt(inside_width * outside_width)
