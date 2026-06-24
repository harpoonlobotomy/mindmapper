"""shit I should just make a mind-map script. Goddamn. 10.41am 23/6/26"""
#"D:\Git_Repos\PIL-expanded\Scripts\Utilities\bbox_manip.py"
import FreeSimpleGUI as sg
from tkinter import Canvas
import bbox_manip as bb

#from ..PIL_expanded.Scripts.Utilities import bbox_manip

class window_data:
    def __init__(self):
        self.testing = True

        self.window_size:tuple[int,int] = (1600,1920)
        self.graph_dimensions =  self.window_size[0]*.8, self.window_size[1]*.8
        self.header_height = self.window_size[0]*.2

        self.active_tool = "rectangle"

        self.ratio_part_1 = 1
        self.ratio_part_2 = 1
        self.ratio:tuple[int,int] = (self.ratio_part_1, self.ratio_part_2)
        self.show_ratio:bool=False

    def get_graph_dimensions(self):

        def get_window_size():
            window = sg.Window(title="test_for_dimensions", layout=[[sg.Text("text so it exists")]], alpha_channel=0, finalize=True)
            while True:
                _,_ = window.read(100)
                window.maximize()

                screen_size = window.get_screen_dimensions()
                if screen_size:
                    window.close()
                    break
            return screen_size

        if self.testing:
            self.window_size = (1000,600)#get_window_size() #
        else:
            self.window_size = get_window_size()
        """ Just an approximation for the moment.
        1/5th for the header
        grid = 4/5ths wide
        """
        self.graph_dimensions = self.window_size[0]*.8, self.window_size[1]*.8
        self.header_height = self.window_size[0]*.2

    def get_tl_br(self):
        left = 0
        top = 0
        right = self.graph_dimensions[0]
        bottom = self.graph_dimensions[1]
        self.graph_bottom_left = (left, bottom)
        self.graph_top_right = (right, top)

w = window_data()

class figure_data():

    def __init__(self, id, is_group_leader=False):
        self.id=id
        self.group:int = None
        self.group_leader:bool = is_group_leader

class graph_data():

    def __init__(self):
        self.graph:sg.Graph = None
        self.canvas:Canvas = "black"
        self.figures:list[int] = []

        self.figure_data:list[figure_data] = []

        self.temp_figures:list[int] = []

        self.fill_colour:str = None
        self.line_colour:str = None

        self.line_width = 3
        self.line_type = "single_line"

        self.currently_adding_figure = []

        self.selection_area = []
        self.selected_figure:int = None
        self.selected_coords:list[int] = []

    def clear_all(self):
        self.figures = []

    def get_grouped_figures(self, figure:int=None, coord:tuple[int,int,int,int]=None):
        if figure:
            print(f"figure in g.get_grouped_figures: {figure}")
            matches = list(i for i in self.figure_data if i.id == figure)
            if matches:
                print(f"Matches: {matches}")
                figure = matches[0]

            grouped = list(i.id for i in self.figure_data if i.group == figure.group)
            print(f"grouped before return: {grouped}")
            return grouped

    def move_grouped_figure(self, figure:int):
        pass


g = graph_data()

def add_figure(figure):
    #g.figures.append(figure)
    fig = figure_data(figure)
    print(f"Added {figure} to figure_data.")
    g.figure_data.append(fig)
    return fig

def make_window():
# back at it, 2:56pm

    #def set_ratio(ratio=(1,1)):
        #return [sg.InputText(default_text=str(ratio[0]), size=(2,1)), sg.Text(text=":", size=(1,1)), sg.InputText(default_text=str(ratio[1]), size=(2,1))]
    def bbox_width_and_height(bbox) -> tuple[float, float]:
        left, top, right, bottom = bbox
        width = right - left
        height = bottom - top
        return width, height

    def get_half_dimensions(bbox):
        width, height = bbox_width_and_height(bbox)
        return int(width/2), int(height/2)

    def move(target_loc):
        for fig in g.temp_figures:
            g.graph.delete_figure(fig)
        g.temp_figures = []

        if not g.selected_figure:
            print("No selected figure, cannot move.")
            return []
        print(f"Figure to move: {g.selected_figure}")

        #graph.relocate_figure(g.selected_figure, target_loc[0], target_loc[1])
#   implement group moving here.
        """
move target to centre of figure bbox, not top left.
repeat targeting for all members of group.


7:15am 24/6/26
how did I solve this last time:
  File "..\FreeSimpleGUI\elements\graph.py", line 636, in relocate_figure
    self._TKCanvas2.move(figure, shift_converted[0] - xy[0], shift_converted[1] - xy[1])
??
Uncommenting the graph.relocate_figure above still works, so it's not a general issue. Maybe just the target lock doesn't... apply? Or am I giving it the wrong 'fig'? It needs the int, what am I giving it...

Okay! fixed it. Yes, I was giving it the wrong fig. Fixed now.
They all congregate at the top left, but that's fine; they're all centred anyway, so i just need to recenter all figs before relocating. Will get the util script out and reuse the relevant bit.
"""

        print(f"About to get grouped from g.current_figure `{g.selected_figure}`")
        grouped = g.get_grouped_figures(g.selected_figure)
        # grouping works now. (grouped movement, no, but the grouping, yes.)
        if not grouped:
            print(f"No grouped items for current figure ({g.selected_figure})")
            return []
        for fig in grouped:
            print(f"to move: {fig}")
            centred = bb.centre_on_target(subject=g.canvas.bbox(fig), target=target_loc, target_is_point=True)
            graph.relocate_figure(fig, centred[0], centred[1])

#        doesn't work for text. It aligns the top left of the text to the value given, regardless being centred like everything else. idk if relocate_figure actually treats text different or if it's on my end, will have to look into it.


## Initial attempt with default centering: the text needs to be half-width across and half-width down, but otherwise it works! Also the centering is much better with that fn, need to redo the initial move to use this like I wanted to originally.


        # For two: It moves to the top left, so if yo click something to start moving from the middle, you've moved the the top left of the thing to centre.
        #graph.delete_figure(g.selected_figure)
        #g.selected_figure = temp

        #graph.RelocateFigure(g.selected_figure, target_loc[0], target_loc[1])



    def draw(current_figure, temp=False):
        def add_text_to_figure_centre(figure):
        #g.canvas.find_enclosed()
        #g.canvas.find_closest()

            x, y = get_half_dimensions(g.canvas.bbox(figure))
            a, b = current_figure[0]
            ### currently places the text at text(0,0) to figure centre, instead of text centre to text centre.
            x += a
            y += b
            text = graph.draw_text(text=values["add_text"], location=(x,y))
            fig_1 = add_figure(text)
            text_x, text_y = get_half_dimensions(g.canvas.bbox(text))

            rect = graph.draw_rectangle(top_left=(g.canvas.bbox(text)[0]-text_x/2, g.canvas.bbox(text)[1]-text_y/2), bottom_right=(g.canvas.bbox(text)[2], g.canvas.bbox(text)[3]), fill_color="white")
            fig_2 = add_figure(rect)
## I want to tie the text and background rectangle together. And to be able to edit the text.
### TODO: need grouping, asap.
            graph.relocate_figure(text, x-text_x/8, y-text_y/4)

            graph.bring_figure_to_front(text)

            return fig_1, fig_2

        #if temp:
        for fig in g.temp_figures:
            g.graph.delete_figure(fig)
            g.temp_figures = []

        if w.active_tool == "rectangle":
            figure = g.graph.draw_rectangle(top_left=current_figure[0], bottom_right=current_figure[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            print(f"DREW A RECTANGLE: {figure}")
            if temp:
                g.temp_figures.append(figure)
            else:
                fig = add_figure(figure)
                print("Added figure")
                if window["add_text"]:
                    figs = add_text_to_figure_centre(figure)
                    figs[1].group_leader=True
                    fig.group = figs[0].group = figs[1].group = figs[1].id
                    for f in fig, figs[0], figs[1]:
                        print(f"Group for {f.id}: {f.group}. Is group leader: {f.group_leader}")
                else:
                    fig.group_leader = True
                    fig.group = fig.id
                g.selected_figure = figure
                print(f"non temp rectangle: {figure})")
                #return fig, figs[0],


        elif w.active_tool == "circle":
            import math
            d = math.sqrt((current_figure[1][0] - current_figure[0][0])**2 + (current_figure[1][1] - current_figure[0][1])**2) # for properly round circles.

            figure = g.graph.draw_oval(top_left=current_figure[0], bottom_right=current_figure[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            #figure = g.graph.draw_circle(center_location=current_figure[0], radius=d, fill_color=g.fill_colour, line_color=g.line_colour)
            if temp:
                g.temp_figures.append(figure)
            else:
                #g.figures.append(figure)
                g.selected_figure = figure
                if values.get("add_text"):
                    add_text_to_figure_centre(figure)

        elif w.active_tool == "line":
            figure = g.graph.draw_line(point_from=current_figure[0], point_to=current_figure[1], color=g.line_colour, width=g.line_width)
            if temp:
                g.temp_figures.append(figure)
            else:
                if g.line_type == "polygon": # note: this way of doing polygons doesn't work because you can't move them, selecting selects a specific line, not the full polygon obj.
                    print("Ignore polygons for now.")
                    if not temp:
                        g.selected_figure = figure
                        if values.get("add_text"):
                            add_text_to_figure_centre(figure)
                        return list((current_figure[1],))
                else:
                    g.figures.append(figure)
                    g.selected_figure = figure
                    if values.get("add_text"):
                        add_text_to_figure_centre(figure)

        return []

    def select(selection_area):
        figures = graph.get_figures_at_location(selection_area)
        if not figures:
            print("No figures at location.")
            return
        print(f"Figures at this location: {figures}")
        figure = figures[0] if figures else None

        print(f"g.canvas coords for newly selected figure: {g.canvas.coords(figure)} / figure: {figure}")
        g.selected_figure = figure
        g.selected_coords = g.canvas.coords(figure)






    def update_ratio(event, values):

        if event == "ratio_part_1" and values["ratio_part_1"] != w.ratio_part_1:
            print(f"updated ratio_part_1 to {values['ratio_part_1']}")
            w.ratio_part_1 = values["ratio_part_1"]

        if event == "ratio_part_2" and values["ratio_part_2"] != w.ratio_part_2:
            print(f"updated ratio_part_2 to {values['ratio_part_2']}")
            w.ratio_part_2 = values["ratio_part_2"]


    def show_set_ratio(force_visible=False, force_hidden=False, ignore_checkbox=False):

        print("def show_set_ratio")
        window.refresh()
        if (w.show_ratio or force_visible) and not force_hidden:
            window["set_ratio_column"].unhide_row()
            window["set_ratio_column"].update(visible=True)
            if not ignore_checkbox:
                check = window["set_ratio_rect"] #type: sg.Checkbox
                check.update(value=True)
                window["set_ratio_circ"].update(value=True)

        else:
            window["set_ratio_column"].hide_row()
            window["set_ratio_column"].update(visible=False)

            if not ignore_checkbox:
                window["set_ratio_rect"].update(value=False)
                window["set_ratio_circ"].update(value=False)


    def select_tool(event:str):
        w.active_tool = event
        #"rectangle", "circle", "line", "select", "move"
        all_buttons = ["tool_buttons_select", "tool_buttons_rectangle", "tool_buttons_circle", "tool_buttons_line"]
        for panel in all_buttons:
            if panel.endswith(event):# and values[event]:
                window["tool_options_panel"].update(event)
                window[panel].unhide_row()
                window[panel].update(visible=True)
            else:
                window[panel].hide_row()
        #window.refresh()
        if w.show_ratio and event in ("rectangle", "circle"): # the two that do have set_ratio; need to make this automatic later.
            show_set_ratio(force_visible=True)
        else:
            show_set_ratio(force_hidden=True)



    def simple_radio(group="select_tool", button_name:str="select", is_default_true=False):
        if len(button_name) == 1:
            key = group + button_name
        else:
            key = button_name

        return sg.Radio(text=button_name, group_id=group, default=is_default_true, key=key.lower().replace(" ", "_"), enable_events=True)

    def simple_button(button_name:str):
        #return [sg.Button(button_text=button_name, key=button_name.replace(" ","_").lower())],
# TODO: make placeholder images for header buttons ( + button panel buttons later too)
        return sg.Button(button_text=button_name, key=button_name.replace(" ","_").lower())


#     top bar: New, Undo, Redo, Save, Save As, Settings/Change Defaults


    def tool_options():
        """
        radio buttons:
            select mode: select_one, add_to_selection, remove_from_selection, clear_selection

            rectangle mode: round_edges, hard_edges, set_ratio
                * if set_ratio: option to set ratio to x:y
                * if round_edges: radius of round edges

            circle_mode: set_ratio checkbox
                * if set_ratio: option to set ratio to x:y

            line mode: single_line, polygon
                * if polygon:
                    fill_polygon (checkbox)

        Just going to hide/show panels here.
        """

        select_buttons = sg.Column(layout=[[simple_radio(group="select", button_name="select one"), simple_radio(group="select", button_name="add to selection"), simple_radio(group="select", button_name="remove from selection")], [simple_button(button_name="clear selection")]], key="tool_buttons_select", visible=False)

        rectangle_buttons = sg.Column(layout=[[simple_radio("rectangle", "round edges", True), simple_radio("rectangle", "hard edges")], [sg.Checkbox(text="set ratio", default=False, enable_events=True, key="set_ratio_rect", tooltip="Does nothing yet...")]], key="tool_buttons_rectangle", visible=False)

        circle_buttons = sg.Column(layout=[[sg.Checkbox(text="set ratio", default=False, enable_events=True, key="set_ratio_circ", tooltip="Does nothing yet...")]], key="tool_buttons_circle", visible=False)

        line_buttons = sg.Column(layout=[[simple_radio(group="line", button_name="single line", is_default_true=True), simple_radio(group="line", button_name="polygon"), sg.Button(button_text="close_polygon", enable_events=True, key="close_polygon")]], key="tool_buttons_line", visible=False)

        return [[sg.Column(layout=[
            [select_buttons],
            [rectangle_buttons],
            [circle_buttons],
            [line_buttons],

        ])], [sg.Column(layout=[[sg.Column(layout=[[sg.InputText(default_text=str(w.ratio[0]), size=(2,1), key="ratio_part_1", enable_events=True), sg.Text(text=":", size=(1,1)), sg.InputText(default_text=str(w.ratio[1]), size=(2,1), key="ratio_part_2", enable_events=True)]], visible=False, key="set_ratio_column", pad=0)]])], [sg.Text("Element text:")],[sg.InputText(default_text='', key="add_text")]]


    header_buttons = [
        [simple_button("New"), simple_button("Undo"), simple_button("Redo"), simple_button("Save"), simple_button("Save As"), simple_button("Settings")]
        ]
    header = [sg.Frame(title="mindmapper", layout=header_buttons, size=(None, 120), expand_x=True, pad=15)]

    graph = sg.Graph(canvas_size=w.graph_dimensions, graph_bottom_left=w.graph_bottom_left, graph_top_right=w.graph_top_right, background_color="#D6ECF1", enable_events=True, drag_submits=True, motion_events=False, key="graph", right_click_menu=[["menu_list"], ["later, select tools from here", "and/or change settings"]])

    tool_picker = [
            [simple_radio(group="select_tool", button_name="rectangle", is_default_true=True), simple_radio(group="select_tool", button_name="circle"), simple_radio(group="select_tool", button_name="line"), simple_radio(group="select_tool", button_name="select"), simple_radio(group="select_tool", button_name="move")]
        ]

    line_width = [
        [simple_radio("line_width", "1"), simple_radio("line_width", "3", is_default_true=True), simple_radio("line_width", "5"), simple_radio("line_width", "7"), simple_radio("line_width", "9")]#, simple_radio("line_width", "edit_sizes")] # edit sizes should be per-button, not an addon, but it's here to remind me to do that.
        ]
    copy_paste_etc = [
        [simple_button("copy"), simple_button("paste"), simple_button("duplicate"), simple_button("delete")]
        ]
    colour_panel = [
        [sg.ColorChooserButton(button_text="Stroke Colour"), sg.ColorChooserButton(button_text="Fill Colour")],
        [sg.Button(button_text="Update selected", key="update_selected_to_curr_colours")]
    ]
    button_panel = sg.Column(layout=[
        [sg.Frame(title="tool_picker", layout=tool_picker, key="tool_picker")],
        [sg.Frame(title="tool_options", layout=tool_options(), key="tool_options_panel")],
        [sg.Frame(title="line_width", layout=line_width)],
        [sg.Frame(title="copy_paste_etc", layout=copy_paste_etc)],
        [sg.Frame(title="colour_panel", layout=colour_panel)], # set it to open the colour dialog window nearer to the button, currently it's aiming for 0,0
        ])

    body = [
        graph, button_panel
        ]


    """ Main screen:
    Fullscreen but resizable.

    Rest of window: graph, right side: rectangle-type selector column. Line thickness column.

    """

    main_frame = [
        header,
        body
        ]

    layout=[
        [sg.Frame(title="", layout=main_frame, background_color="#444444", relief="groove", border_width=12, vertical_alignment="center", expand_y=True)] # actually no it's: flat, groove, raised, ridge, solid, or sunken # RELIEF_RAISED RELIEF_SUNKEN RELIEF_FLAT RELIEF_RIDGE RELIEF_GROOVE RELIEF_SOLID
        ]

    window = sg.Window(title="mindmapper", layout=layout, finalize=True, return_keyboard_events=True, element_padding=(5,5,5,5))

    def setup_window():
        if not w.testing:
            window.maximize()
        select_tool(w.active_tool)
        g.graph = window["graph"] ## type: sg.Graph
        g.canvas = window["graph"].Widget

    setup_window()
    g.currently_adding_figure = []

    while True and not window.is_closed():
        event, values = window.read(500)
        if event and event != "__TIMEOUT__":

            if (isinstance(event, str) and event.startswith("Escape")) or window.is_closed():
                break

            if event == "new":
                print("event new")
                window.close()
                return "restart"


            if event.startswith("graph"):

                if w.active_tool in ("rectangle", "circle", "line"):

                    if event == "graph+UP":
                        g.currently_adding_figure.append(values["graph"])
                        g.currently_adding_figure = draw(g.currently_adding_figure)
            # just realised I need to break up 'current figure' from 'selected'. 'current figure' is more of 'the one I'm currently making', which may or may not be the selected one. Going to rename and fix this now.

                    else:
                        if not g.currently_adding_figure:
                            g.currently_adding_figure.append(values["graph"])

                        else:
                            ending = values["graph"]
                            draw((g.currently_adding_figure[0], ending), temp=True)

                else:
                    if w.active_tool == "select":
                        if event == "graph+UP":
                            select(values["graph"])
                    # if click and drag selection:
                    #    g.canvas.find_enclosed()

                    elif w.active_tool == "move" and g.selected_figure:
                        #if event == "graph+UP":
                        move(values["graph"])

                        """else:
                            if not g.current_figure:
                                g.move_figure.append(values["graph"])

                            else:
                                ending = values["graph"]
                                draw((g.move_figure[0], ending), temp=True)
"""

            elif g.currently_adding_figure:
                g.currently_adding_figure = []#= draw(g.current_figure) # so that if you click anything non-graph while drawing a polygon, it just ends drawing that polygon.

            elif event in ("rectangle", "circle", "line", "select", "move"):
                print(f"EVENT: {event}")
                select_tool(event)

            elif event.startswith("line_width"):
                g.line_width = event.replace("line_width", "")

            elif event in ("polygon", "single_line"):
                g.line_type = event

            elif event.startswith("set_ratio"):
                w.show_ratio = not w.show_ratio
                show_set_ratio()

            elif event in ("ratio_part_1", "ratio_part_2"):
                update_ratio(event, values)



            else:
                print(f"EVENT: `{event}`")# / values: `{values}`")



def setup():
    w.get_graph_dimensions()
    w.get_tl_br()


def run():
    setup()
    while True:
        outcome = make_window()
        if outcome:
            if outcome == "restart":
                continue
        else:
            break


run()
