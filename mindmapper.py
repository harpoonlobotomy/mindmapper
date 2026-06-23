"""shit I should just make a mind-map script. Goddamn. 10.41am 23/6/26"""

import FreeSimpleGUI as sg

class window_data:
    def __init__(self):
        self.window_size:tuple[int,int] = (1600,1920)
        self.graph_dimensions =  self.window_size[0]*.8, self.window_size[1]*.8


    def get_graph_dimensions(self):

        def get_window_size():
            window = sg.Window(title="test_for_dimensions", layout=[[sg.Text("text so it exists")]], alpha_channel=0, finalize=True)
            while True:
                _,_ = window.read(100)
                window.maximize()

                screen_size = window.get_screen_dimensions()
                if screen_size:
                    break
            return screen_size
        self.window_size = get_window_size()
        """ Just an approximation for the moment.
        1/5th for the header
        grid = 4/5ths wide
        """
        self.graph_dimensions = self.window_size[0]*.8, self.window_size[1]*.8

    def get_tl_br(self):
        left = 0
        top = 0
        right = self.graph_dimensions[0]
        bottom = self.graph_dimensions[1]
        self.graph_bottom_left = (left, bottom)
        self.graph_top_right = (right, top)

w = window_data()


def make_window():

    def default_content(call_name):
        return sg.Column(layout=[[sg.Text(call_name)]])

    def simple_button(button_name:str):
        #return [sg.Button(button_text=button_name, key=button_name.replace(" ","_").lower())],
# TODO: make placeholder images for header buttons ( + button panel buttons later too)
        return sg.Button(button_text=button_name, key=button_name.replace(" ","_").lower())

    #    return sg.Column(layout=[
    #        [sg.Button(button_text="placeholder", key=button_name.replace(" ","_").lower())],
    #        [sg.Text(button_name)]
    #        ], element_justification="center", background_color="#5F7766")

#     top bar: New, Undo, Redo, Save, Save As, Settings/Change Defaults
    header_buttons = [
        [simple_button("New"), simple_button("Undo"), simple_button("Redo"), simple_button("Save"), simple_button("Save As"), simple_button("Settings")]
        ]
    header = [
        sg.Column(layout=header_buttons)
        ]


    graph = sg.Graph(canvas_size=w.graph_dimensions, graph_bottom_left=w.graph_bottom_left, graph_top_right=w.graph_top_right, background_color="#D6ECF1")

    tool_picker = [
            [simple_button("rectangle"), simple_button("oval"), simple_button("line"), simple_button("select")]#default_content("tool_picker")]
        ]
    shape_options = [
        # this is for rounded rectangles, radius of rounding, etc. But might have to change depending on which tool? 'round edges' make no sense for a circle.
            [simple_button("round_edges"), simple_button("radius_increase"), simple_button("radius_decrease")]#default_content("tool_picker")]
    ]
    line_width = [
        [simple_button("size_1"), simple_button("size_2"), simple_button("size_3"), simple_button("size_4"), simple_button("size_5"), simple_button("edit_sizes")] # edit sizes should be per-button, not an addon, but it's here to remind me to do that.
        ]
    copy_paste_etc = [
        [simple_button("copy"), simple_button("paste"), simple_button("duplicate"), simple_button("delete")]
        ]
    colour_panel = [
        [sg.ColorChooserButton(button_text="Stroke Colour"), sg.ColorChooserButton(button_text="Fill Colour")]
    ]
    button_panel = sg.Column(layout=[
        [sg.Frame(title="tool_picker", layout=tool_picker)],
        [sg.Frame(title="shape_options", layout=shape_options)],
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
        [sg.Frame(title="", layout=main_frame, background_color="#444444", relief="sunken", border_width=12)] # actually no it's: flat, groove, raised, ridge, solid, or sunken # RELIEF_RAISED RELIEF_SUNKEN RELIEF_FLAT RELIEF_RIDGE RELIEF_GROOVE RELIEF_SOLID
        ]

    window = sg.Window(title="mindmapper", layout=layout, finalize=True, return_keyboard_events=True)

    while True and not window.is_closed():
        event, values = window.read(1000)
        if event and event != "__TIMEOUT__":
            print(f"Event: {event}")

            if event.startswith("Escape") or window.is_closed():
                break


def setup():
    w.get_graph_dimensions()
    w.get_tl_br()


def run():
    setup()
    make_window()

run()
