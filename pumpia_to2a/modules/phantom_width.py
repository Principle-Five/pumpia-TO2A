"""
Phantom width of TO2A Phantom
"""
import math
import statistics

from pumpia.module_handling.modules import PhantomModule
from pumpia.module_handling.in_outs.roi_ios import BaseInputROI, InputLineROI
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.module_handling.in_outs.simple import BoolInput, PercInput, FloatOutput
from pumpia.image_handling.roi_structures import LineROI
from pumpia.file_handling.dicom_structures import Series
from pumpia.utilities.array_utils import nth_max_bounds

from pumpia_to2a.to2a_context import TO2AContextManagerGenerator, TO2AContext

# distances in mm
HALF_LINE_LENGTH = 100
COS_PI_6 = math.cos(math.pi / 6)
COS_PI_3 = math.cos(math.pi / 3)


class TO2APhantomWidth(PhantomModule):
    """
    Calculates TO2A phantom width
    """
    context_manager_generator = TO2AContextManagerGenerator()
    show_draw_rois_button = True
    show_analyse_button = True

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    max_perc = PercInput(20, verbose_name="Width position (% of max)")

    bool_12_6 = BoolInput(verbose_name="Include 12-6 in Average")
    bool_1_7 = BoolInput(verbose_name="Include 1-7 in Average")
    bool_2_8 = BoolInput(verbose_name="Include 2-8 in Average")
    bool_3_9 = BoolInput(verbose_name="Include 3-9 in Average")
    bool_4_10 = BoolInput(verbose_name="Include 4-10 in Average")
    bool_5_11 = BoolInput(verbose_name="Include 5-11 in Average")

    width_12_6 = FloatOutput(verbose_name="12-6 Width", reset_on_analysis=True)
    width_1_7 = FloatOutput(verbose_name="1-7 Width", reset_on_analysis=True)
    width_2_8 = FloatOutput(verbose_name="2-8 Width", reset_on_analysis=True)
    width_3_9 = FloatOutput(verbose_name="3-9 Width", reset_on_analysis=True)
    width_4_10 = FloatOutput(verbose_name="4-10 Width", reset_on_analysis=True)
    width_5_11 = FloatOutput(verbose_name="5-11 Width", reset_on_analysis=True)

    average_width = FloatOutput(verbose_name="Average Phantom Width", reset_on_analysis=True)

    line_12_6 = InputLineROI(name="12-6 Line")
    line_1_7 = InputLineROI(name="1-7 Line")
    line_2_8 = InputLineROI(name="2-8 Line")
    line_3_9 = InputLineROI(name="3-9 Line")
    line_4_10 = InputLineROI(name="4-10 Line")
    line_5_11 = InputLineROI(name="5-11 Line")

    def draw_rois(self, context: TO2AContext, batch: bool = False) -> None:

        if self.viewer.image is not None:
            image = self.viewer.image

            if isinstance(image, Series):
                slice_index = image.num_slices // 2
                image = image.instances[slice_index]

            pixel_size = image.pixel_size
            pixel_height = pixel_size[1]
            pixel_width = pixel_size[2]

            xcent = context.xcent
            ycent = context.ycent

            ydiff = HALF_LINE_LENGTH / pixel_height
            xdiff = 0
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_12_6.register_roi(roi)

            ydiff = HALF_LINE_LENGTH / pixel_height * COS_PI_6
            xdiff = HALF_LINE_LENGTH / pixel_width * COS_PI_3
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_5_11.register_roi(roi)

            ydiff = HALF_LINE_LENGTH / pixel_height * COS_PI_3
            xdiff = HALF_LINE_LENGTH / pixel_width * COS_PI_6
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_4_10.register_roi(roi)

            ydiff = 0
            xdiff = HALF_LINE_LENGTH / pixel_width
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_3_9.register_roi(roi)

            ydiff = HALF_LINE_LENGTH / pixel_height * COS_PI_3
            xdiff = -HALF_LINE_LENGTH / pixel_width * COS_PI_6
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_2_8.register_roi(roi)

            ydiff = HALF_LINE_LENGTH / pixel_height * COS_PI_6
            xdiff = -HALF_LINE_LENGTH / pixel_width * COS_PI_3
            x1 = round(xcent - xdiff)
            x2 = round(xcent + xdiff)
            y1 = round(ycent - ydiff)
            y2 = round(ycent + ydiff)
            roi = LineROI(image,
                          x1,
                          y1,
                          x2,
                          y2,
                          replace=True)
            self.line_1_7.register_roi(roi)

    def post_roi_register(self, roi_input: BaseInputROI):
        if (roi_input.roi is not None
            and self.manager is not None
                and roi_input in self.rois):
            self.manager.add_roi(roi_input.roi)

    def link_rois_viewers(self):
        self.line_12_6.viewer = self.viewer
        self.line_1_7.viewer = self.viewer
        self.line_2_8.viewer = self.viewer
        self.line_3_9.viewer = self.viewer
        self.line_4_10.viewer = self.viewer
        self.line_5_11.viewer = self.viewer

    def analyse(self, batch: bool = False):
        if (self.viewer.image is not None
            and self.line_12_6.roi is not None
            and self.line_1_7.roi is not None
            and self.line_2_8.roi is not None
            and self.line_3_9.roi is not None
            and self.line_4_10.roi is not None
                and self.line_5_11.roi is not None):

            image = self.viewer.image

            if isinstance(image, Series):
                slice_index = image.num_slices // 2
                image = image.instances[slice_index]

            pixel_size = image.pixel_size
            pixel_height = pixel_size[1]
            pixel_width = pixel_size[2]

            prof_12_6 = self.line_12_6.roi.profile
            prof_1_7 = self.line_1_7.roi.profile
            prof_2_8 = self.line_2_8.roi.profile
            prof_3_9 = self.line_3_9.roi.profile
            prof_4_10 = self.line_4_10.roi.profile
            prof_5_11 = self.line_5_11.roi.profile

            divisor = 100 / self.max_perc.value

            lengths = []

            unit_length_12_6 = pixel_height
            width_12_6 = nth_max_bounds(prof_12_6, divisor).difference * unit_length_12_6
            self.width_12_6.value = width_12_6
            if self.bool_12_6.value:
                lengths.append(width_12_6)

            unit_length_1_7 = math.dist([pixel_height * COS_PI_6, pixel_width * COS_PI_3], [0, 0])
            width_1_7 = nth_max_bounds(prof_1_7, divisor).difference * unit_length_1_7
            self.width_1_7.value = width_1_7
            if self.bool_1_7.value:
                lengths.append(width_1_7)

            unit_length_2_8 = math.dist([pixel_height * COS_PI_3, pixel_width * COS_PI_6], [0, 0])
            width_2_8 = nth_max_bounds(prof_2_8, divisor).difference * unit_length_2_8
            self.width_2_8.value = width_2_8
            if self.bool_2_8.value:
                lengths.append(width_2_8)

            unit_length_3_9 = pixel_width
            width_3_9 = nth_max_bounds(prof_3_9, divisor).difference * unit_length_3_9
            self.width_3_9.value = width_3_9
            if self.bool_3_9.value:
                lengths.append(width_3_9)

            unit_length_4_10 = math.dist([pixel_height * COS_PI_3, pixel_width * COS_PI_6], [0, 0])
            width_4_10 = nth_max_bounds(prof_4_10, divisor).difference * unit_length_4_10
            self.width_4_10.value = width_4_10
            if self.bool_4_10.value:
                lengths.append(width_4_10)

            unit_length_5_11 = math.dist([pixel_height * COS_PI_6, pixel_width * COS_PI_3], [0, 0])
            width_5_11 = nth_max_bounds(prof_5_11, divisor).difference * unit_length_5_11
            self.width_5_11.value = width_5_11
            if self.bool_5_11.value:
                lengths.append(width_5_11)

            self.average_width.value = statistics.fmean(lengths)
