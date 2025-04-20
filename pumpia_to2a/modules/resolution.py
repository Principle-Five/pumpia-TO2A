"""
Resolution inserts of TO2A Phantom
"""
from pumpia.module_handling.modules import PhantomModule
from pumpia.module_handling.in_outs.roi_ios import BaseInputROI, InputRectangleROI
from pumpia.module_handling.in_outs.viewer_ios import MonochromeDicomViewerIO
from pumpia.module_handling.in_outs.simple import PercInput, StringOutput, FloatOutput
from pumpia.image_handling.roi_structures import RectangleROI
from pumpia.file_handling.dicom_structures import Series
from pumpia.file_handling.dicom_tags import MRTags
from pumpia.utilities.array_utils import nth_max_troughs

from pumpia_to2a.to2a_context import TO2AContextManagerGenerator, TO2AContext

# distances in mm
WIDTHS = 11
LENGTH_2MM = 24
LENGTH_1_5_MM = 20
LENGTH_1_MM = 16

WEDGE_SIDE_OFFSET = 10
WEDGE_SIDE_2MM_OFFSET = 31
WEDGE_SIDE_1_5MM_OFFSET = 51
WEDGE_SIDE_1MM_OFFSET = 71

OTHER_SIDE_OFFSET = 43
OTHER_SIDE_2MM_OFFSET = 20
OTHER_SIDE_1_5MM_OFFSET = 41
OTHER_SIDE_1MM_OFFSET = 61

TICK = "\u2713"
CROSS = "\u274c"


class TO2AResolution(PhantomModule):
    """
    Calculates resolution using TO2A phantom inserts
    """
    context_manager_generator = TO2AContextManagerGenerator()
    show_draw_rois_button = True
    show_analyse_button = True

    viewer = MonochromeDicomViewerIO(row=0, column=0)

    max_perc = PercInput(50, verbose_name="Width position (% of max)")

    phase_dir = StringOutput(verbose_name="Phase Encode Direction",
                             reset_on_analysis=True)
    phase_pix = FloatOutput(verbose_name="Phase Pixel Size",
                            reset_on_analysis=True)
    freq_pix = FloatOutput(verbose_name="Frequency Pixel Size",
                           reset_on_analysis=True)

    phase_2 = StringOutput(verbose_name="Phase Encode Direction 2mm",
                           reset_on_analysis=True)
    phase_1_5 = StringOutput(verbose_name="Phase Encode Direction 1.5mm",
                             reset_on_analysis=True)
    phase_1 = StringOutput(verbose_name="Phase Encode Direction 1mm",
                           reset_on_analysis=True)

    freq_2 = StringOutput(verbose_name="Frequency Encode Direction 2mm",
                          reset_on_analysis=True)
    freq_1_5 = StringOutput(verbose_name="Frequency Encode Direction 1.5mm",
                            reset_on_analysis=True)
    freq_1 = StringOutput(verbose_name="Frequency Encode Direction 1mm",
                          reset_on_analysis=True)

    horizontal_2_roi = InputRectangleROI(name="Horizontal 2mm")
    horizontal_1_5_roi = InputRectangleROI(name="Horizontal 1.5mm")
    horizontal_1_roi = InputRectangleROI(name="Horizontal 1mm insert")

    vertical_2_roi = InputRectangleROI(name="Vertical 2mm insert")
    vertical_1_5_roi = InputRectangleROI(name="Vertical 1.5mm insert")
    vertical_1_roi = InputRectangleROI(name="Vertical 1mm insert")

    def draw_rois(self, context: TO2AContext, batch: bool = False) -> None:

        if self.viewer.image is not None:
            image = self.viewer.image

            if isinstance(image, Series):
                slice_index = image.num_slices // 2
                image = image.instances[slice_index]

            pixel_size = image.pixel_size
            pixel_height = pixel_size[1]
            pixel_width = pixel_size[2]

            wedge_loc = context.wedges_side
            mtf_loc = context.mtf_side

            xcent = context.xcent
            ycent = context.ycent

            horizontal_height = WIDTHS / pixel_height
            horizontal_2mm_width = LENGTH_2MM / pixel_width
            horizontal_1_5mm_width = LENGTH_1_5_MM / pixel_width
            horizontal_1mm_width = LENGTH_1_MM / pixel_width

            vertical_width = WIDTHS / pixel_width
            vertical_2mm_height = LENGTH_2MM / pixel_height
            vertical_1_5mm_height = LENGTH_1_5_MM / pixel_height
            vertical_1mm_height = LENGTH_1_MM / pixel_height

            if wedge_loc == "bottom" or wedge_loc == "top":
                horizontal_xoffset = OTHER_SIDE_OFFSET / pixel_width
                horizontal_2mm_yoffset = OTHER_SIDE_2MM_OFFSET / pixel_height
                horizontal_1_5mm_yoffset = OTHER_SIDE_1_5MM_OFFSET / pixel_height
                horizontal_1mm_yoffset = OTHER_SIDE_1MM_OFFSET / pixel_height

                vertical_yoffset = WEDGE_SIDE_OFFSET / pixel_height
                vertical_2mm_xoffset = WEDGE_SIDE_2MM_OFFSET / pixel_width
                vertical_1_5mm_xoffset = WEDGE_SIDE_1_5MM_OFFSET / pixel_width
                vertical_1mm_xoffset = WEDGE_SIDE_1MM_OFFSET / pixel_width

                if wedge_loc == "bottom":
                    horizontal_2mm_ymin = ycent - horizontal_2mm_yoffset
                    horizontal_1_5mm_ymin = ycent - horizontal_1_5mm_yoffset
                    horizontal_1mm_ymin = ycent - horizontal_1mm_yoffset
                    vertical_2mm_ymin = ycent + vertical_yoffset
                    vertical_1_5mm_ymin = ycent + vertical_yoffset
                    vertical_1mm_ymin = ycent + vertical_yoffset

                else:
                    horizontal_2mm_ymin = ycent + horizontal_2mm_yoffset - horizontal_height
                    horizontal_1_5mm_ymin = ycent + horizontal_1_5mm_yoffset - horizontal_height
                    horizontal_1mm_ymin = ycent + horizontal_1mm_yoffset - horizontal_height
                    vertical_2mm_ymin = ycent - vertical_yoffset - vertical_2mm_height
                    vertical_1_5mm_ymin = ycent - vertical_yoffset - vertical_1_5mm_height
                    vertical_1mm_ymin = ycent - vertical_yoffset - vertical_1mm_height

                if mtf_loc == "left":
                    horizontal_2mm_xmin = xcent + horizontal_xoffset
                    horizontal_1_5mm_xmin = xcent + horizontal_xoffset
                    horizontal_1mm_xmin = xcent + horizontal_xoffset
                    vertical_2mm_xmin = xcent + vertical_2mm_xoffset
                    vertical_1_5mm_xmin = xcent + vertical_1_5mm_xoffset
                    vertical_1mm_xmin = xcent + vertical_1mm_xoffset

                else:
                    horizontal_2mm_xmin = xcent - horizontal_xoffset - horizontal_2mm_width
                    horizontal_1_5mm_xmin = xcent - horizontal_xoffset - horizontal_1_5mm_width
                    horizontal_1mm_xmin = xcent - horizontal_xoffset - horizontal_1mm_width
                    vertical_2mm_xmin = xcent - vertical_2mm_xoffset - vertical_width
                    vertical_1_5mm_xmin = xcent - vertical_1_5mm_xoffset - vertical_width
                    vertical_1mm_xmin = xcent - vertical_1mm_xoffset - vertical_width

            else:
                horizontal_xoffset = WEDGE_SIDE_OFFSET / pixel_width
                horizontal_2mm_yoffset = WEDGE_SIDE_2MM_OFFSET / pixel_height
                horizontal_1_5mm_yoffset = WEDGE_SIDE_1_5MM_OFFSET / pixel_height
                horizontal_1mm_yoffset = WEDGE_SIDE_1MM_OFFSET / pixel_height

                vertical_yoffset = OTHER_SIDE_OFFSET / pixel_height
                vertical_2mm_xoffset = OTHER_SIDE_2MM_OFFSET / pixel_width
                vertical_1_5mm_xoffset = OTHER_SIDE_1_5MM_OFFSET / pixel_width
                vertical_1mm_xoffset = OTHER_SIDE_1MM_OFFSET / pixel_width

                if wedge_loc == "right":
                    horizontal_2mm_xmin = xcent + horizontal_xoffset
                    horizontal_1_5mm_xmin = xcent + horizontal_xoffset
                    horizontal_1mm_xmin = xcent + horizontal_xoffset
                    vertical_2mm_xmin = xcent - vertical_2mm_xoffset
                    vertical_1_5mm_xmin = xcent - vertical_1_5mm_xoffset
                    vertical_1mm_xmin = xcent - vertical_1mm_xoffset

                else:
                    horizontal_2mm_xmin = xcent - horizontal_xoffset - horizontal_2mm_width
                    horizontal_1_5mm_xmin = xcent - horizontal_xoffset - horizontal_1_5mm_width
                    horizontal_1mm_xmin = xcent - horizontal_xoffset - horizontal_1mm_width
                    vertical_2mm_xmin = xcent + vertical_2mm_xoffset - vertical_width
                    vertical_1_5mm_xmin = xcent + vertical_1_5mm_xoffset - vertical_width
                    vertical_1mm_xmin = xcent + vertical_1mm_xoffset - vertical_width

                if mtf_loc == "bottom":
                    horizontal_2mm_ymin = ycent - horizontal_2mm_yoffset - horizontal_height
                    horizontal_1_5mm_ymin = ycent - horizontal_1_5mm_yoffset - horizontal_height
                    horizontal_1mm_ymin = ycent - horizontal_1mm_yoffset - horizontal_height
                    vertical_2mm_ymin = ycent - vertical_yoffset - vertical_2mm_height
                    vertical_1_5mm_ymin = ycent - vertical_yoffset - vertical_1_5mm_height
                    vertical_1mm_ymin = ycent - vertical_yoffset - vertical_1mm_height

                else:
                    horizontal_2mm_ymin = ycent + horizontal_2mm_yoffset
                    horizontal_1_5mm_ymin = ycent + horizontal_1_5mm_yoffset
                    horizontal_1mm_ymin = ycent + horizontal_1mm_yoffset
                    vertical_2mm_ymin = ycent + vertical_yoffset
                    vertical_1_5mm_ymin = ycent + vertical_yoffset
                    vertical_1mm_ymin = ycent + vertical_yoffset

            horizontal_2mm_ymax = round(horizontal_2mm_ymin + horizontal_height)
            horizontal_1_5mm_ymax = round(horizontal_1_5mm_ymin + horizontal_height)
            horizontal_1mm_ymax = round(horizontal_1mm_ymin + horizontal_height)
            vertical_2mm_ymax = round(vertical_2mm_ymin + vertical_2mm_height)
            vertical_1_5mm_ymax = round(vertical_1_5mm_ymin + vertical_1_5mm_height)
            vertical_1mm_ymax = round(vertical_1mm_ymin + vertical_1mm_height)

            horizontal_2mm_xmax = round(horizontal_2mm_xmin + horizontal_2mm_width)
            horizontal_1_5mm_xmax = round(horizontal_1_5mm_xmin + horizontal_1_5mm_width)
            horizontal_1mm_xmax = round(horizontal_1mm_xmin + horizontal_1mm_width)
            vertical_2mm_xmax = round(vertical_2mm_xmin + vertical_width)
            vertical_1_5mm_xmax = round(vertical_1_5mm_xmin + vertical_width)
            vertical_1mm_xmax = round(vertical_1mm_xmin + vertical_width)

            horizontal_2mm_ymin = round(horizontal_2mm_ymin)
            horizontal_1_5mm_ymin = round(horizontal_1_5mm_ymin)
            horizontal_1mm_ymin = round(horizontal_1mm_ymin)
            vertical_2mm_ymin = round(vertical_2mm_ymin)
            vertical_1_5mm_ymin = round(vertical_1_5mm_ymin)
            vertical_1mm_ymin = round(vertical_1mm_ymin)

            horizontal_2mm_xmin = round(horizontal_2mm_xmin)
            horizontal_1_5mm_xmin = round(horizontal_1_5mm_xmin)
            horizontal_1mm_xmin = round(horizontal_1mm_xmin)
            vertical_2mm_xmin = round(vertical_2mm_xmin)
            vertical_1_5mm_xmin = round(vertical_1_5mm_xmin)
            vertical_1mm_xmin = round(vertical_1mm_xmin)

            horizontal_2mm_roi = RectangleROI(image,
                                              horizontal_2mm_xmin,
                                              horizontal_2mm_ymin,
                                              horizontal_2mm_xmax,
                                              horizontal_2mm_ymax,
                                              replace=True)
            self.horizontal_2_roi.register_roi(horizontal_2mm_roi)

            horizontal_1_5mm_roi = RectangleROI(image,
                                                horizontal_1_5mm_xmin,
                                                horizontal_1_5mm_ymin,
                                                horizontal_1_5mm_xmax,
                                                horizontal_1_5mm_ymax,
                                                replace=True)
            self.horizontal_1_5_roi.register_roi(horizontal_1_5mm_roi)

            horizontal_1mm_roi = RectangleROI(image,
                                              horizontal_1mm_xmin,
                                              horizontal_1mm_ymin,
                                              horizontal_1mm_xmax,
                                              horizontal_1mm_ymax,
                                              replace=True)
            self.horizontal_1_roi.register_roi(horizontal_1mm_roi)

            vertical_2mm_roi = RectangleROI(image,
                                            vertical_2mm_xmin,
                                            vertical_2mm_ymin,
                                            vertical_2mm_xmax,
                                            vertical_2mm_ymax,
                                            replace=True)
            self.vertical_2_roi.register_roi(vertical_2mm_roi)

            vertical_1_5mm_roi = RectangleROI(image,
                                              vertical_1_5mm_xmin,
                                              vertical_1_5mm_ymin,
                                              vertical_1_5mm_xmax,
                                              vertical_1_5mm_ymax,
                                              replace=True)
            self.vertical_1_5_roi.register_roi(vertical_1_5mm_roi)

            vertical_1mm_roi = RectangleROI(image,
                                            vertical_1mm_xmin,
                                            vertical_1mm_ymin,
                                            vertical_1mm_xmax,
                                            vertical_1mm_ymax,
                                            replace=True)
            self.vertical_1_roi.register_roi(vertical_1mm_roi)

    def post_roi_register(self, roi_input: BaseInputROI):
        if (roi_input.roi is not None
            and self.manager is not None
                and roi_input in self.rois):
            self.manager.add_roi(roi_input.roi)

    def link_rois_viewers(self):
        self.vertical_1_roi.viewer = self.viewer
        self.vertical_1_5_roi.viewer = self.viewer
        self.vertical_2_roi.viewer = self.viewer
        self.horizontal_1_roi.viewer = self.viewer
        self.horizontal_1_5_roi.viewer = self.viewer
        self.horizontal_2_roi.viewer = self.viewer

    def analyse(self, batch: bool = False):
        if (self.viewer.image is not None
           and self.vertical_1_roi.roi is not None
            and self.vertical_1_5_roi.roi is not None
            and self.vertical_2_roi.roi is not None
            and self.horizontal_1_roi.roi is not None
            and self.horizontal_1_5_roi.roi is not None
                and self.horizontal_2_roi.roi is not None):

            vertical_1_prof = self.vertical_1_roi.roi.v_profile
            vertical_1_5_prof = self.vertical_1_5_roi.roi.v_profile
            vertical_2_prof = self.vertical_2_roi.roi.v_profile
            horizontal_1_prof = self.horizontal_1_roi.roi.h_profile
            horizontal_1_5_prof = self.horizontal_1_5_roi.roi.h_profile
            horizontal_2_prof = self.horizontal_2_roi.roi.h_profile

            divisor = 100 / self.max_perc.value

            vertical_1_n_seen = len(nth_max_troughs(vertical_1_prof, divisor))
            vertical_1_5_n_seen = len(nth_max_troughs(vertical_1_5_prof, divisor))
            vertical_2_n_seen = len(nth_max_troughs(vertical_2_prof, divisor))
            horizontal_1_n_seen = len(nth_max_troughs(horizontal_1_prof, divisor))
            horizontal_1_5_n_seen = len(nth_max_troughs(horizontal_1_5_prof, divisor))
            horizontal_2_n_seen = len(nth_max_troughs(horizontal_2_prof, divisor))

            if isinstance(self.viewer.image, Series):
                phase_dir = self.viewer.image.get_tag(MRTags.InPlanePhaseEncodingDirection, 0)
            else:
                phase_dir = self.viewer.image.get_tag(MRTags.InPlanePhaseEncodingDirection)

            self.phase_dir.value = phase_dir  # type: ignore

            pixel_size = self.viewer.image.pixel_size
            pixel_height = pixel_size[1]
            pixel_width = pixel_size[2]

            if phase_dir == "ROW":
                self.phase_pix.value = pixel_height
                self.freq_pix.value = pixel_width
                if vertical_1_n_seen == 5:
                    self.phase_1.value = TICK
                else:
                    self.phase_1.value = CROSS

                if vertical_1_5_n_seen == 5:
                    self.phase_1_5.value = TICK
                else:
                    self.phase_1_5.value = CROSS

                if vertical_2_n_seen == 5:
                    self.phase_2.value = TICK
                else:
                    self.phase_2.value = CROSS

                if horizontal_1_n_seen == 5:
                    self.freq_1.value = TICK
                else:
                    self.freq_1.value = CROSS

                if horizontal_1_5_n_seen == 5:
                    self.freq_1_5.value = TICK
                else:
                    self.freq_1_5.value = CROSS

                if horizontal_2_n_seen == 5:
                    self.freq_2.value = TICK
                else:
                    self.freq_2.value = CROSS

            else:
                self.phase_pix.value = pixel_width
                self.freq_pix.value = pixel_height
                if horizontal_1_n_seen == 5:
                    self.phase_1.value = TICK
                else:
                    self.phase_1.value = CROSS

                if horizontal_1_5_n_seen == 5:
                    self.phase_1_5.value = TICK
                else:
                    self.phase_1_5.value = CROSS

                if horizontal_2_n_seen == 5:
                    self.phase_2.value = TICK
                else:
                    self.phase_2.value = CROSS

                if vertical_1_n_seen == 5:
                    self.freq_1.value = TICK
                else:
                    self.freq_1.value = CROSS

                if vertical_1_5_n_seen == 5:
                    self.freq_1_5.value = TICK
                else:
                    self.freq_1_5.value = CROSS

                if vertical_2_n_seen == 5:
                    self.freq_2.value = TICK
                else:
                    self.freq_2.value = CROSS
