"""
Contains context handling for TO2A phantom
"""

import tkinter as tk
from tkinter import ttk
from typing import overload, Literal

import numpy as np

from pumpia.file_handling.dicom_structures import Series, Instance
from pumpia.module_handling.manager import Manager
from pumpia.utilities.typing import DirectionType, SideType
from pumpia.widgets.typing import ScreenUnits, Cursor, Padding, Relief, TakeFocusValue
from pumpia.widgets.context_managers import (PhantomContextManager,
                                             AutoPhantomManager,
                                             PhantomContextManagerGenerator,
                                             side_map,
                                             inv_side_map,
                                             side_opts)
from pumpia.module_handling.context import PhantomContext

# offsets in mm (dicom standard units)
FOUR_BOX_OFFSET = 54
FOUR_BOX_SL = 10


class TO2AContext(PhantomContext):
    """
    Context for TO2A Phantom.
    """

    def __init__(self,
                 xmin: int,
                 xmax: int,
                 ymin: int,
                 ymax: int,
                 wedges_side: SideType = "bottom",
                 mtf_side: SideType = "left"):
        super().__init__(xmin, xmax, ymin, ymax, 'ellipse')

        if ((mtf_side in ["top", "bottom"]
             and wedges_side in ["top", "bottom"])
            or (mtf_side in ["left", "right"]
                and wedges_side in ["left", "right"])):
            raise ValueError("wedges/MTF sides must not be on the same axis")

        self.mtf_side: SideType = mtf_side
        self.wedges_side: SideType = wedges_side


class TO2AContextManager(PhantomContextManager):
    """
    Context Manager for TO2A Phantom.
    """
    @overload
    def __init__(self,
                 parent: tk.Misc,
                 manager: Manager,
                 mode: Literal["auto", "manual"] = "auto",
                 sensitivity: int = 3,
                 top_perc: int = 95,
                 iterations: int = 2,
                 cull_perc: int = 80,
                 bubble_offset: int = 0,
                 bubble_side: SideType = "top",
                 direction: DirectionType = "Vertical",
                 text: float | str = "TO2A Context",
                 *,
                 border: ScreenUnits = ...,
                 borderwidth: ScreenUnits = ...,  # undocumented
                 class_: str = "",
                 cursor: Cursor = "",
                 height: ScreenUnits = 0,
                 labelanchor: Literal["nw", "n", "ne",
                                      "en", "e", "es",
                                      "se", "s", "sw",
                                      "ws", "w", "wn"] = ...,
                 labelwidget: tk.Misc = ...,
                 name: str = ...,
                 padding: Padding = ...,
                 relief: Relief = ...,  # undocumented
                 style: str = "",
                 takefocus: TakeFocusValue = "",
                 underline: int = -1,
                 width: ScreenUnits = 0,
                 ) -> None: ...

    @overload
    def __init__(self,
                 parent: tk.Misc,
                 manager: Manager,
                 mode: Literal["auto", "manual"] = "auto",
                 sensitivity: int = 3,
                 top_perc: int = 95,
                 iterations: int = 2,
                 cull_perc: int = 80,
                 bubble_offset: int = 0,
                 bubble_side: SideType = "top",
                 direction: DirectionType = "Vertical",
                 text: float | str = "TO2A Context",
                 **kw) -> None: ...

    def __init__(self,
                 parent: tk.Misc,
                 manager: Manager,
                 mode: Literal["auto", "manual"] = "auto",
                 sensitivity: int = 3,
                 top_perc: int = 95,
                 iterations: int = 2,
                 cull_perc: int = 80,
                 bubble_offset: int = 0,
                 bubble_side: SideType = "top",
                 direction: DirectionType = "Vertical",
                 text: float | str = "TO2A Context",
                 **kw) -> None:
        kw["shape"] = "ellipse"
        super().__init__(parent,
                         manager=manager,
                         direction=direction,
                         text=text,
                         **kw)
        self.auto_phantom_manager = AutoPhantomManager(self,
                                                       manager=manager,
                                                       mode=mode,
                                                       sensitivity=sensitivity,
                                                       top_perc=top_perc,
                                                       iterations=iterations,
                                                       cull_perc=cull_perc,
                                                       bubble_offset=bubble_offset,
                                                       bubble_side=bubble_side,
                                                       direction=direction,
                                                       text="Bound Box Options",
                                                       **kw)

        self.inserts_frame = ttk.Labelframe(self, text="Inserts")

        self.mtf_var = tk.StringVar(self, inv_side_map["left"])
        self.mtf_combo = ttk.Combobox(self.inserts_frame,
                                      textvariable=self.mtf_var,
                                      values=side_opts,
                                      height=4,
                                      state="readonly")
        self.mtf_label = ttk.Label(self.inserts_frame, text="MTF Box Side")
        self.mtf_label.grid(column=0, row=1, sticky="nsew")
        self.mtf_combo.grid(column=1, row=1, sticky="nsew")

        self.wedge_var = tk.StringVar(self, inv_side_map["bottom"])
        self.wedge_combo = ttk.Combobox(self.inserts_frame,
                                        textvariable=self.wedge_var,
                                        values=side_opts,
                                        height=4,
                                        state="readonly")
        self.wedge_label = ttk.Label(self.inserts_frame, text="Wedges Side")
        self.wedge_label.grid(column=0, row=2, sticky="nsew")
        self.wedge_combo.grid(column=1, row=2, sticky="nsew")

        if self.direction[0].lower() == "h":
            self.auto_phantom_manager.grid(column=0, row=0, sticky="nsew")
            self.inserts_frame.grid(column=1, row=0, sticky="nsew")
        else:
            self.auto_phantom_manager.grid(column=0, row=0, sticky="nsew")
            self.inserts_frame.grid(column=0, row=1, sticky="nsew")

    def get_context(self, image: Series | Instance) -> TO2AContext:

        if isinstance(image, Series):
            slice_index = image.num_slices // 2
            image = image.instances[slice_index]

        boundary_context = self.auto_phantom_manager.get_context(image)

        mtf_side: SideType
        wedge_side: SideType

        if self.auto_phantom_manager.mode_var.get() == "fine tune":
            mtf_side = side_map[self.mtf_var.get()]
            wedge_side = side_map[self.wedge_var.get()]
            return TO2AContext(boundary_context.xmin,
                               boundary_context.xmax,
                               boundary_context.ymin,
                               boundary_context.ymax,
                               wedge_side,
                               mtf_side)

        pixel_size = image.pixel_size
        pixel_height = pixel_size[1]
        pixel_width = pixel_size[2]

        image_array = image.array[0]

        xcent = boundary_context.xcent
        ycent = boundary_context.ycent

        four_box_offset_x = FOUR_BOX_OFFSET / pixel_width
        four_box_offset_y = FOUR_BOX_OFFSET / pixel_height

        four_box_width = FOUR_BOX_SL / pixel_width
        four_box_height = FOUR_BOX_SL / pixel_height

        top_box_xmin = round(xcent - four_box_width / 2)
        top_box_xmax = round(xcent + four_box_width / 2) + 1
        top_box_ymin = round(ycent - four_box_offset_y - four_box_height)
        top_box_ymax = round(ycent - four_box_offset_y) + 1

        bottom_box_xmin = round(xcent - four_box_width / 2)
        bottom_box_xmax = round(xcent + four_box_width / 2) + 1
        bottom_box_ymin = round(ycent + four_box_offset_y)
        bottom_box_ymax = round(ycent + four_box_offset_y + four_box_height) + 1

        left_box_xmin = round(xcent - four_box_offset_x - four_box_width)
        left_box_xmax = round(xcent - four_box_offset_x) + 1
        left_box_ymin = round(ycent - four_box_height / 2)
        left_box_ymax = round(ycent + four_box_height / 2) + 1

        right_box_xmin = round(xcent + four_box_offset_x)
        right_box_xmax = round(xcent + four_box_offset_x + four_box_width) + 1
        right_box_ymin = round(ycent - four_box_height / 2)
        right_box_ymax = round(ycent + four_box_height / 2) + 1

        box_means = [np.mean(image_array[top_box_ymin:top_box_ymax,
                                         top_box_xmin:top_box_xmax]),
                     np.mean(image_array[bottom_box_ymin:bottom_box_ymax,
                                         bottom_box_xmin:bottom_box_xmax]),
                     np.mean(image_array[left_box_ymin:left_box_ymax,
                                         left_box_xmin:left_box_xmax]),
                     np.mean(image_array[right_box_ymin:right_box_ymax,
                                         right_box_xmin:right_box_xmax])]
        sort_box_means = sorted(box_means)

        mtf_mean = sort_box_means[0]
        wedge_mean = sort_box_means[1]

        if mtf_mean == box_means[0]:
            mtf_side = "top"
        elif mtf_mean == box_means[1]:
            mtf_side = "bottom"
        elif mtf_mean == box_means[2]:
            mtf_side = "left"
        elif mtf_mean == box_means[3]:
            mtf_side = "right"

        if wedge_mean == box_means[0]:
            wedge_side = "top"
        elif wedge_mean == box_means[1]:
            wedge_side = "bottom"
        elif wedge_mean == box_means[2]:
            wedge_side = "left"
        elif wedge_mean == box_means[3]:
            wedge_side = "right"

        self.mtf_var.set(inv_side_map[mtf_side])
        self.wedge_var.set(inv_side_map[wedge_side])

        return TO2AContext(boundary_context.xmin,
                           boundary_context.xmax,
                           boundary_context.ymin,
                           boundary_context.ymax,
                           wedge_side,
                           mtf_side)


class TO2AContextManagerGenerator(PhantomContextManagerGenerator[TO2AContextManager]):
    """
    Generator for TO2AContextManager.
    """
    context_manager_type = TO2AContextManager

    @overload
    def __init__(self,
                 *,
                 mode: Literal["auto", "manual"] = "auto",
                 sensitivity: int = 3,
                 top_perc: int = 95,
                 iterations: int = 2,
                 cull_perc: int = 80,
                 bubble_offset: int = 0,
                 bubble_side: SideType = "top",
                 direction: DirectionType = "Vertical",
                 text: float | str = "TO2A Context",
                 border: ScreenUnits = ...,
                 borderwidth: ScreenUnits = ...,  # undocumented
                 class_: str = "",
                 cursor: Cursor = "",
                 height: ScreenUnits = 0,
                 labelanchor: Literal["nw", "n", "ne",
                                      "en", "e", "es",
                                      "se", "s", "sw",
                                      "ws", "w", "wn"] = ...,
                 labelwidget: tk.Misc = ...,
                 name: str = ...,
                 padding: Padding = ...,
                 relief: Relief = ...,  # undocumented
                 style: str = "",
                 takefocus: TakeFocusValue = "",
                 underline: int = -1,
                 width: ScreenUnits = 0,
                 ) -> None: ...

    @overload
    def __init__(self,
                 **kw) -> None: ...

    def __init__(self,
                 **kw) -> None:
        kw["shape"] = "ellipse"
        super().__init__(**kw)
