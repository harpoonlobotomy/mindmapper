"""Minimim viable product GUI"""

import FreeSimpleGUI as sg
import nodes_lines_components as nodes

_nodes = nodes.desk_drawer

CAN_RATIO = ("rectangle", "circle")

def start_window():

    g = nodes.g

    class window_data:
        def __init__(self):
            self.testing = True

            self.values = {}

            self.window_size:tuple[int,int] = (1600,1920)
            self.graph_dimensions =  self.window_size[0]*.8, self.window_size[1]*.8
            self.header_height = self.window_size[0]*.2

            self.ratio_part_1 = 1
            self.ratio_part_2 = 1
            self.ratio:tuple[int,int] = (self.ratio_part_1, self.ratio_part_2)
            self.show_ratio:bool=False


        def move(self, temp=False):
            if not g.selected_figure:
                #TODO: get figure at xy if any and set selected.
                return
            _nodes.move(target_loc=w.values["graph"], exclude_text=temp)


        def draw(self, temp=False, custom_coordinates=None):
            #print(f"custom coordinates: {custom_coordinates} / values: {w.values} / temp: {temp}")
            _nodes.draw(custom_coordinates if custom_coordinates else g.currently_adding_figure, values=w.values, temp=temp)

            return [] # to clear g.currently_drawing.

        def select(self):
            _nodes.select(selection_area=w.values.get("graph"))

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
                self.window_size = (500,500)
            else:
                self.window_size = get_window_size()

            """
            Note: Just an approximation for the moment. Set properly later.
            header = 1/5th height
            grid = 4/5ths width
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

    def make_window():

        def end_current_drawing():
            """ Just exists to clear the current drawing in the case of polygons etc. Later can decide if a polygon should keep drawing even if you've clicked off."""
            g.currently_adding_figure = []

        def do_move_and_select(event):
           # if event == "graph+UP":
                #print(f"Figure count: {len(g.canvas.find_all())}")
                #print(f"len(dd.lines): {len(_nodes.lines)}\n\n")

            if g.active_tool == "select":
                if event == "graph+UP":
                    w.select()
            # if click and drag selection:#    g.canvas.find_enclosed()

            elif g.active_tool == "move" and g.selected_figure:
                if event == "graph+UP":
                    print("graph UP")
                    w.move()
                if event == "graph":
                    w.move(temp=True)

        def add_xy(event):

            ending = w.values["graph"]

            if event == "graph+UP":
                g.currently_adding_figure.append(ending)
                g.currently_adding_figure = w.draw()
                g.last_coord = None

            else:
                #if g.currently_adding_figure and g.last_coord and g.last_coord == (g.currently_adding_figure[0], ending):
                #    print(f"SAME AS PREVIOUS, IGNORE. currently_adding_figure: {g.currently_adding_figure} / ending: {ending}") # is tuple in a list
                #    g.currently_adding_figure = []
                #    return
                #else:
                #    print(f"Not returning as not same coords")
                if not g.currently_adding_figure:
                    g.currently_adding_figure.append(ending)

                else:
                    print(f"g.currently_adding_figure[0], ending: {g.currently_adding_figure[0], ending} 000")
                    w.draw(temp=True, custom_coordinates=list((g.currently_adding_figure[0], ending)))

                    g.last_coord = (g.currently_adding_figure[0], ending)


        def select_tool(event:str):
            assert g.active_tool in ("rectangle", "circle", "line", "select", "move") if g.active_tool else False
            g.active_tool = event
            all_buttons = ["tool_buttons_select", "tool_buttons_rectangle", "tool_buttons_circle", "tool_buttons_line"]
            for panel in all_buttons:
                if panel.endswith(event):
                    window["tool_options_panel"].update(event)
                    window[panel].unhide_row()
                    window[panel].update(visible=True)
                else:
                    window[panel].hide_row()

            if w.show_ratio and event in CAN_RATIO:
                print ("Ratio not implemented yet.")
                pass # do the ratio latershow_set_ratio(force_visible=True)


        def simple_radio(group="select_tool", button_name:str="select", is_default_true=False) -> sg.Radio[str, str]:

            if len(button_name) == 1:
                key = group + button_name
            else:
                key = button_name

            return sg.Radio(text=button_name, group_id=group, default=is_default_true, key=key.lower().replace(" ", "_"), enable_events=True)


        def simple_button(button_name:str) -> sg.Button:     # TODO: make placeholder images for header buttons ( + button panel buttons later too)

            return sg.Button(button_text=button_name, key=button_name.replace(" ","_").lower())


        def tool_options() -> list:

            select_buttons = sg.Column(layout=[[simple_radio(group="select", button_name="select one"), simple_radio(group="select", button_name="add to selection"), simple_radio(group="select", button_name="remove from selection")], [simple_button(button_name="clear selection")]], key="tool_buttons_select", visible=False)

            rectangle_buttons = sg.Column(layout=[[simple_radio("rectangle", "round edges", True), simple_radio("rectangle", "hard edges")], [sg.Checkbox(text="set ratio", default=False, enable_events=True, key="set_ratio_rect", tooltip="Does nothing yet...")]], key="tool_buttons_rectangle", visible=False)

            circle_buttons = sg.Column(layout=[[sg.Checkbox(text="set ratio", default=False, enable_events=True, key="set_ratio_circ", tooltip="Does nothing yet...")]], key="tool_buttons_circle", visible=False)

            line_buttons = sg.Column(layout=[[simple_radio(group="line", button_name="single line", is_default_true=True), sg.Checkbox(text="attach to node", default=True, key="attach_line_to_node", enable_events=True)], [simple_radio(group="line", button_name="polygon"), sg.Button(button_text="close_polygon", enable_events=True, key="close_polygon")]], key="tool_buttons_line", visible=False)

            return [[sg.Column(layout=[
                [select_buttons],
                [rectangle_buttons],
                [circle_buttons],
                [line_buttons],

            ])], [sg.Column(layout=[[sg.Column(layout=[[sg.InputText(default_text=str(w.ratio[0]), size=(2,1), key="ratio_part_1", enable_events=True), sg.Text(text=":", size=(1,1)), sg.InputText(default_text=str(w.ratio[1]), size=(2,1), key="ratio_part_2", enable_events=True)]], visible=False, key="set_ratio_column", pad=0)]])], [sg.Text("Element text:")],[sg.InputText(default_text="testing", key="add_text")]] # TODO change "testing" to '' to default to None


        header_buttons = [
            [simple_button("New"), simple_button("Undo"), simple_button("Redo"), simple_button("Save"), simple_button("Save As"), simple_button("Settings")]
            ]
        header = [sg.Frame(title="mindmapper", layout=header_buttons, size=(None, 120), expand_x=True, pad=15)]

        graph = sg.Graph(canvas_size=w.graph_dimensions, graph_bottom_left=w.graph_bottom_left, graph_top_right=w.graph_top_right, background_color=g.background_colour, enable_events=True, drag_submits=True, motion_events=False, key="graph", right_click_menu=[["menu_list"], ["later, select tools from here", "and/or change settings"]])

        tool_picker = [
                [simple_radio(group="select_tool", button_name="rectangle", is_default_true=True), simple_radio(group="select_tool", button_name="circle"), simple_radio(group="select_tool", button_name="line"), simple_radio(group="select_tool", button_name="select"), simple_radio(group="select_tool", button_name="move")]
            ]

        line_width = [
            [simple_radio("line_width", "1"), simple_radio("line_width", "3", is_default_true=True), simple_radio("line_width", "5"), simple_radio("line_width", "7"), simple_radio("line_width", "9")]
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
            select_tool(g.active_tool)
            g.graph = window["graph"] ## type: sg.Graph
            g.canvas = window["graph"].Widget
            print(f"Selected tool: {g.active_tool}")
            print(f"g.graph: {g.graph}")


        setup_window()
        g.currently_adding_figure = []

        while True and not window.is_closed():
            event, values = window.read(3000)
            w.values = values
            if event and event != "__TIMEOUT__":

                if (isinstance(event, str) and event.startswith("Escape")) or window.is_closed():
                    break

                if event == "new":
                    print("event new")
                    g.graph.erase()
                    print("also a fn here to clear all the data regarding said figures.")

                #print(f"EVENT: {event}")
                if event.startswith("graph"):

                    if g.active_tool in ("rectangle", "circle", "line"):
                        add_xy(event)

                    else:
                        do_move_and_select(event)


                elif g.currently_adding_figure:
                    end_current_drawing()

                elif event in ("rectangle", "circle", "line", "select", "move"):
                    select_tool(event)

                elif event.startswith("line_width"):
                    g.line_width = event.replace("line_width", "")

                elif event in ("polygon", "single_line"):
                    g.line_type = event

                    """
                elif event.startswith("set_ratio"):
                    w.show_ratio = not w.show_ratio
                    show_set_ratio()

                elif event in ("ratio_part_1", "ratio_part_2"):
                    update_ratio(event, values)"""

                else:
                    print(f"EVENT: `{event}`")# / values: `{values}`")

    w = window_data()

    def setup():
        w.get_graph_dimensions()
        w.get_tl_br()

    setup()
    while True:
        outcome = make_window()
        if outcome:
            return (f"Exiting because make_window ended with outcome `{outcome}`.")
        return ("Exiting because make_window ended without an outcome.")



