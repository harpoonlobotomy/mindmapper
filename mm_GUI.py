
import FreeSimpleGUI as sg
import nodes_lines_components as nodes
from debug import debug
db = debug()

_nodes = nodes.desk_drawer

CAN_RATIO = ("rectangle", "circle")

def start_window():

    g = nodes.g

    class window_data:
        def __init__(self):
            self.testing = True

            self.values = {}
            self.first_run = False

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

        def select(self, no_jiggle=False): # Any reason to keep this here and not just direct to _nodes.select directly?
            _nodes.select(selection_area=g.graph.ClickPosition, no_jiggle=no_jiggle)

        def delete(self):
            inst_to_delete:set = set()
            inst_to_delete.add(g.selected_figure)
            if g.selected_figure.components:
                for comp in g.selected_figure.components:
                    inst_to_delete.add(comp)
                    # not _nodes.update_node_line_data() but
                    comp.parent = None
            if isinstance(g.selected_figure, nodes.node) and g.selected_figure.connections:
                for connection in g.selected_figure.connections:
                    inst_to_delete.add(connection)
                    if connection.components:
                        for comp in connection.components:
                            inst_to_delete.add(comp)
                    """relevant = (i for i in connection.to_node.connections if i.to_node == inst_to_delete or i.from_node == inst_to_delete)
                    if relevant:
                        for link_inst in relevant:
                            inst_to_delete.union(link_inst.components)"""

            for item in inst_to_delete:
                g.graph.delete_figure(item.figure_id)
            print(f"Deleted items asociated with {g.selected_figure}")

            g.selected_figure = None
            print("Not sure if def delete() does everything it needs to do yet.")



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
# here to figure out if it needs to change the selected item based on where the click started.
                ending = w.values["graph"]

                if not g.start_coords:
                    g.start_coords = g.graph.ClickPosition
                    local_figures = g.graph.GetFiguresAtLocation(g.start_coords)

                    if local_figures:
                        already_selected = list(i for i in local_figures if g.selected_figure and i == g.selected_figure.figure_id)
                        if already_selected:
                            pass
                        else:
                            w.select(no_jiggle=True)

                if event == "graph+UP":
                    w.move()
                    g.start_coords = None
                    g.end_coords = g.graph.ClickPosition
                if event == "graph":
                    w.move(temp=True)

        def add_xy(event):

            ending = w.values["graph"]

            if event == "graph+UP":
                g.currently_adding_figure.append(ending)
                g.currently_adding_figure = w.draw()
                g.last_coord = None

            else:
                if not g.currently_adding_figure:
                    g.currently_adding_figure.append(ending)

                else:
                    w.draw(temp=True, custom_coordinates=list((g.currently_adding_figure[0], ending)))
                    g.last_coord = (g.currently_adding_figure[0], ending)


        def select_tool(event:str):
            """ Set/Change the selected tool (draw shapes/select/move)"""
            db.announce_fn(f"[select_tool]: event: {event}")
            assert g.active_tool in ("rectangle", "circle", "line", "select", "move") if g.active_tool else event in ("Add Rectangle with Text", "Add Oval with Text", "Connect Nodes")


            right_click_menu = ("Add Rectangle with Text", "Add Oval with Text", "Connect Nodes")

            if event in right_click_menu:
                if "rectangle" in event.lower():
                    event = "rectangle"
                elif "oval" in event.lower():
                    event = "circle"
                elif "connect" in event.lower():
                    event = "line"

            g.active_tool = event
            window[event].update(value=True) # sets the radio button accordingly.

            tool_buttons = ["tool_buttons_select", "tool_buttons_rectangle", "tool_buttons_circle", "tool_buttons_line"]

            for btn in tool_buttons:
                if btn.endswith(event):
                    window["tool_options_panel"].update(event)
                    window[btn].unhide_row()
                    window[btn].update(visible=True)
                else:
                    window[btn].hide_row()

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
                    ]),                ],
                [sg.Column(layout=[[sg.Column(layout=[[sg.InputText(default_text=str(w.ratio[0]), size=(2,1), key="ratio_part_1", enable_events=True), sg.Text(text=":", size=(1,1)), sg.InputText(default_text=str(w.ratio[1]), size=(2,1), key="ratio_part_2", enable_events=True)]], visible=False, key="set_ratio_column", pad=0)]])]]#, [sg.Text("Element text:")],[sg.InputText(default_text="testing", key="add_text", enable_events=True)]] # TODO change "testing" to '' to default to None


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
            #g.add_text = window["popup_text_input"].Widget
            g.current_text = ""#g.add_text.get()


        setup_window()
        g.currently_adding_figure = []

        while True and not window.is_closed():
            event, values = window.read(3000)
            w.values = values
            """if event == "add_text" and not g.changing_text:
                g.current_text=g.add_text.get()
                g.changing_text=True
                continue"""

                #if window._focus_callback(event):# and window._focus_callback(event).event == "add_text":
            if event and event != "__TIMEOUT__":

                """ if g.changing_text and event != "add_text":
                    if len(event) != 1:
                        g.current_text = g.add_text.get()
                        g.changing_text = False
                        print(f"updated g.current_text to: {g.current_text}")"""

    # Now we go back to doing anything else.

                #if w.first_run:
                    #g.current_text = values["add_text"]

                if (isinstance(event, str) and event.startswith("Escape")) or window.is_closed():
                    break

                #if event in ("popup_text_input", "popup_text_done", "popup_text_cancelled"):
                    #print(f"Event: `{event}`")

                """if event == "add_text":
                    g.current_text = values["add_text"]"""

                if event == "new":
                    print("New doesn't work yet.")
                    """g.clear_all()
                    g.graph.erase()"""


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

                elif event == "delete" and g.selected_figure:
                    print(f"Deleting {g.selected_figure} and components.")
                    w.delete()


                elif event in ("Add Rectangle with Text", "Add Oval with Text", "Connect Nodes"):
                    print(f"event going to select_tool: {event}")
                    select_tool(event)
                    pass

                    """
                elif event.startswith("set_ratio"):
                    w.show_ratio = not w.show_ratio
                    show_set_ratio()

                elif event in ("ratio_part_1", "ratio_part_2"):
                    update_ratio(event, values)"""

                else:
                    print(f"EVENT: `{event}` // no match.")

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



