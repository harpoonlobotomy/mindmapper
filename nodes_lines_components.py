""" Just need to figure out the node classes for the mindmapper.
Instead of tracking and changing the figure_id on differing instances of lines etc, it's one instance per completed drawing, and you just point that at a different figure ID. There is literally no reason that can't work and it's the clearest way."""

""" Am gong to have the graph here too, but separate. At least for now.

Man I really want a socket class but that's dumb."""

import traceback
from uuid import uuid4
import FreeSimpleGUI as sg
import bbox_manip as bb

def repr_colours(repr_str:str="node", text=""):

    codes = {
        "node": ["21", "32"],
        "component": ["35", "26"],
        "line": ["37", "36"]
        }

    start = f"\033[{';'.join(codes[repr_str])}m"
    end = "\033[0m"
    return f"{start}{text}{end}"


SHAPES = {
    "rectangle": {"radius":0},
    "circle": {},
    "polygon": {"closed":True}
}

COMPONENTS = {
    "text_label": None,
    "text_bg": None
}


class graph_data():

    def __init__(self):

        self.graph:sg.Graph = None
        self.canvas:sg.Canvas = None
        self.add_text:sg.Input = None

        self.temp_figures:list[int] = []

        self.background_colour:str = "#D6ECF1"
        self.fill_colour:str = self.background_colour#None
        self.line_colour:str = "black"#None
        self.lighter_line_colour:str = "#494949"

        self.line_width = 3
        self.line_type = "single_line"

        self.currently_adding_figure = []

        self.selected_figure:node = None

        self.active_tool:str = "rectangle"

        self.last_coords:tuple[tuple[int,int], tuple[int,int]] = ((0,0), (0,0))

        self.current_text = ""
        self.changing_text:bool = False
        self.start_coords:tuple[int,int] = None
        self.end_coords:tuple[int,int] = None # not for any particular figure/instance, just the last click-and-drag/click event start/end.

        self.add_labels_to_lines:bool = False

    def clear_all(self):
        self.pointer_index = {}
        self.figure_id_index = {}
        self.selected_figure = None
        self.additional_connection = None
        self.currently_adding_figure:list = []
        self.temp_figures = []
        g.graph.erase()



    def remove_figure(self, figure_id, replace = None):

        if g.canvas.find_withtag(figure_id):
            g.graph.delete_figure(figure_id)



    def clear_temp_figures(self):
        for fig in self.temp_figures:
            self.remove_figure(fig)

        self.temp_figures = []

    def find_nodes_for_line(self) -> tuple[tuple[int,int], tuple[int,int]] | tuple[node, node]:

        if not g.last_coords:
            print("no last coords to find overlapping")
            return None, None

        from_node = self.canvas.find_overlapping(g.last_coords[0][0]-10, g.last_coords[0][1]-10, g.last_coords[0][0]+10, g.last_coords[0][1]+10)

        to_node = self.canvas.find_overlapping(g.last_coords[1][0]-10, g.last_coords[1][1]-10, g.last_coords[1][0]+10, g.last_coords[1][1]+10)


        if not from_node or not to_node:
            print("Either no from or no to node at click, returning null.")
            return None, None

        from_node = desk_drawer.get_node_by_figure_id(from_node[0])
        to_node = desk_drawer.get_node_by_figure_id(to_node[0])
        return from_node, to_node


g = graph_data()



class line:


    def __init__(self, figure_id:int, from_node:node=None, to_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        """ Note: Lines can also have components."""
        self.line_id = uuid4()
        self.figure_id = figure_id
        self.from_node = from_node
        self.to_node = to_node
        self.components:set = set()
        self.set_coords(coords)

        print(f"line init: {self} / coords: {coords}")

    def set_coords(self, coords):
        print(f"COORDS: {coords} len: {len(coords)}")
        if len(coords) == 1:
            coords = coords[0]
        if len(coords) == 3:
            if coords[1] == coords[2]:
                coords = coords[0], coords[1]
        if len(coords) == 4:
            coords = list(int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3]))

        print(f"Coords after fix (should be [(0,0), (0,0)]: {coords}")
        self.line_start = coords[0]
        self.to_xy = coords[0] # these are literal duplicates, but I keep thinking I need them. So will make them as needed, them combine function later.
        self.line_end = coords[1]
        self.from_xy = coords[1] # these are literal duplicates
        self.coords = coords

    def __repr__(self): # removed `line_id: {str(self.line_id)[:-6]}, `
        #test = input("Type anything to print a traceback to this point, else hit return")
        #if test:
        #    traceback.print_stack()
        return repr_colours("line", text=f"[[figure_id: {self.figure_id}{f'||from_node.figure_id: {self.from_node.figure_id}' if self.from_node else ""}{f'||to_node.figure_id: {self.to_node.figure_id}' if self.to_node else ""}||line_start: {self.line_start}, line_end: {self.line_end}]]")



class component:

    def __init__(self, figure_id:int, component_type:str, primary_figure:node|line, text:str=None):#, text:str=None):
        assert component_type in COMPONENTS
        assert isinstance(primary_figure, node|line)

        self.figure_id:int = figure_id
        self.parent:node|line = primary_figure
        self.component_type=component_type
        if self.component_type == "text_label":
            self.text = text if text else None # used to store after init, not for init fetching.text is given at each instance's init, not globally.
        print(f"comp init: {self}")

    def __repr__(self):
        return repr_colours("component", f"[[component_type: {self.component_type}{f'||text: {self.text}' if hasattr(self, 'text') else ''}|| figure_id: {self.figure_id}{f'||parent:  {self.parent.figure_id}' if self.parent else ''}]]")

    def set_text_to_top(self):
        print(f"SElf.component_type in set_text_to_top: {self.component_type}")
        if self.component_type == "text_label" or self.component_type == "text":
            print(f"The text type component type varname is: {self.component_type}. Always use this when referencing, make it transparent.")
            g.graph.bring_figure_to_front(self.figure_id)

class node:
    def __init__(self, figure_id:int, shape:str, bbox=None):
        print(f"Shape in node init: {shape}")
        assert shape in SHAPES

        self.figure_id:int = figure_id
        self.shape:str = shape
        if bbox:
            self.centrepoint = bb.get_half_dimensions(bbox)
        self.components:set[component] = set()
        self.connections:set[line] = set()
        print(f"Node init: {self}")

    def __repr__(self): # removed `node_id: {str(self.node_id)[:-6]}`
        return repr_colours("node", f"[[figure_id: {self.figure_id}||shape: {self.shape}{f'||components: {self.components}' if self.components else ""}{f'||connections: {self.connections}' if self.connections else ""}]]")


class desk:
    def __init__(self):
        self.nodes:set[node] = set() # just all the nodes. Can get the data from those nodes, don't think it needs a dict or anything.

        self.lines:set[line] = set() # do I need the lines separate here? Idk.

        self.components:set[component] = set() # I really shouldn't need this, but I do need to be able to click any component and have it find the match. So I do need a route back from figure_id...
        # temporarily adding this here, but it should be in the class that manages the graph, not here. This is for the elements themselves. It's a desk drawer. graph is the drawing surface.

        #self.add_text:str = "test_text" # this is the presence of text in that box, not actually a var written here. Purely for testing.

        self.temp_figures:list[str] = [] # figure_ids for temp items.

    #def delete_components
    def get_all_components(self):
        components = list()
        for node in self.nodes:
            if node.components:
                components.extend(node.components)

        self.components = components # it exists, might as well try to use it once.
        return components


    def get_node_by_figure_id(self, figure_id):

        nodes = list(i for i in self.nodes if i.figure_id == figure_id)
        if nodes:
            return nodes[0]
        """else:
            print("Have just realised self.components isn't added to? Is that true? If so how can this possibly return anything?")
            components = list(i for i in self.components if i.figure_id == figure_id)
            if components:
                return components[0].parent if components[0].parent else components[0]
            else:
                print("It didn't return anything.")
                lines = list(i.from_node for i in self.lines if i.figure_id == figure_id)
                if lines:
                    return list(i.from_node for i in self.lines if i.figure_id == figure_id)[0]"""

    def get_instances_by_figure_id(self, figures):

        """just the plural version of get_node_by_figure_id"""
        instances = set()
        if not figures:
            return set()
        print(f"figures: {figures}")
        if isinstance(figures, int):
            instances.add(self.get_node_by_figure_id(figures))
            return instances
        for figure in figures:
            instances.add(self.get_node_by_figure_id(figure))

        return instances

    def edit_text_label(self, target_of_doubleclick:node):
        """
    Here, use the popup window at mouselocationto get the new input.
        """
        newtext = "test_text_oop"
        text_label = list(i for i in target_of_doubleclick.components if i.component_type == "text_label")
        if text_label:
            text_label[0].text = newtext
            g.add_text.update(newtext)


    def connect_nodes_with_line(self, line_figure_id:int, from_node=None, to_node=None, to_coords=None): # use a version of this again with the update. Make them work together better. Same goal.

        def remove_improper_connection(line_figure_id):
            if line_figure_id in g.temp_figures:
                g.temp_figures.remove(line_figure_id)
            g.graph.delete_figure(line_figure_id)

        to_coord = g.currently_adding_figure[-1] if g.currently_adding_figure else None
        if not to_coord:
            print("No currently_adding_")
            return

        if not from_node or not to_node:
            from_node, to_node = g.find_nodes_for_line()


        if not from_node or not to_node:
            print(f"No from_node, deleting line {line_figure_id}")
            remove_improper_connection(line_figure_id)
            #g.last_coords = None#(g.currently_adding_figure[0], g.graph.ClickPosition)
            return None

        if from_node.connections:
            for conn in from_node.connections:
                if conn.to_node == to_node and conn.from_node == from_node or conn.from_node == to_node and conn.to_node == from_node:
                    print("Nodes already have a connection, cancelling.")
                    remove_improper_connection(line_figure_id)
                    #g.last_coords = None
                    return None

        if line_figure_id in g.temp_figures:
            g.temp_figures.remove(line_figure_id)

        line_link = self.create_line_inst(line_figure_id, from_node, to_node, coords=g.currently_adding_figure)
        self.update_node_line_data(_line=line_link, new_figure_id=line_figure_id, from_node=from_node, to_node=to_node)

        g.selected_figure = to_node if to_node else None
        assert isinstance(g.selected_figure, node) if g.selected_figure else True#g.selected_figure
        g.graph.send_figure_to_back(line_figure_id)

        return line_link


    def move_components(self, luggage:list[component], centred:tuple[tuple[int,int], tuple[int,int]], target_loc=None):
        """ Not in use yet, got distracted."""
        for fig in luggage:
            if target_loc:
                centred = bb.centre_on_target(subject=g.canvas.bbox(fig.figure_id), target=target_loc, target_is_point=True)
            if fig.component_type == "text_label":

                width, height = bb.bbox_width_and_height(centred)
                centred = centred[0]+(width/2)-2, centred[1]+height/2-2, centred[2]+(width/2)-2, centred[3]+(height/2)-2

            g.graph.relocate_figure(fig.figure_id, centred[0], centred[1])

    def update_node_line_data(self, _line:line=None, new_figure_id:int=None, from_node:node=None, to_node:node=None):
        assert isinstance(_line, line)
        """ This is where the figure_id is changed, and where connections are updated, etc. Nothing about the node instances should change outside of this fn."""
        ## to update:
        print(f"[update_node_line_date] {_line} / new_figure_id: {new_figure_id}")

        old_id = _line.figure_id
        _line.figure_id = new_figure_id
        _line.line_start

        assert _line.from_node == from_node and isinstance(from_node, node)
        assert _line.to_node == to_node  and isinstance(to_node, node)
        def remove_previous_connection(from_node:node, to_node:node, new_figure_id):

            for node in (from_node, to_node):
                print(f"NODE in replace_line: {node.figure_id}\n")
                if node.connections:
                    match = list(i for i in node.connections if (i.from_node == from_node and i.to_node == to_node))# or (i.to_node == from_node and i.from_node == to_node))#for connection in from_node.connections: if connection.to_node == to_node:
                    if match:
                        print(f"match founbd in node.connections: {match[0]}")
                        match.figure_id = new_figure_id
                        print(f"replacing old figure_id with the new one to see if that works: {match}")
                        return
            """ Remove/replace anything still using old_id"""
            """ delete the figure"""
            """ make sure the coords assigned to line are actually its coordinates. I can just get it from canvas."""

            """
            If any existing connections with this to_ and from_ node:
                that's the line you need to redraw.

            """
        if not _line.from_node and _line.to_node:
            print("Line does not have to_node and from_node; fatal error, no idea how this happened.")
            #traceback.print_stack()
            traceback.print_last()

        _line.to_node.connections.add(_line)#] = ({"from_node":from_node}) # should already be in it.
        _line.from_node.connections.add(_line)#] = ({"to_node":to_node})


    def create_node_inst(self, figure_id, shape="rectangle", bbox=None):
        """ This is for after the shape is drawn, once we have the figure_id. Only for /nodes/, not lines or components.
        Maybe we get shape from current_tool?"""
        node_inst = node(figure_id, shape, bbox)
        self.nodes.add(node_inst)

        return node_inst

    def create_line_inst(self, figure_id:int, from_node:node=None, to_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        """ Just the line version of create_node_inst. Not sure if I should merge them or not. Keeping like this for now."""

        if not isinstance(from_node,node):

            print(f"No from_node: `{from_node}`")
            traceback.print_stack()
        if not isinstance(to_node,node):
            print(f"No to_node: `{to_node}`")
        assert isinstance(from_node, node) if from_node else True
        assert isinstance(to_node, node) if to_node else True
        line_inst = line(figure_id, from_node, to_node, coords)
        print(f"ADDING {self} TO LINES NOW.")
        self.lines.add(line_inst)

        print(f"Returning line_inst: {line_inst}")
        return line_inst


    def create_component_insts(self, primary_figure:node|line, text_figure_id:int=None, text_bg_id:int=None, text:str=None):
        """ Can be used on its own to add components"""
        if not text:
            return primary_figure.components

        print(f"PRIMARY FIGURE: {primary_figure}")
        assert isinstance(primary_figure, node|line)# else isinstance(primary_figure, line)

        #primary_figure = node_inst if node_inst else line_inst # so I don't have to do it separately depending. Might merge them later, idk.

        primary_figure.components.add(component(figure_id=text_bg_id, component_type="text_bg", primary_figure=primary_figure, text=text))
        #text_figure_id, text_bg_id = 6,7#"fn here where we make the text figure + bg rectangle, can't be bothered rn"
        primary_figure.components.add(component(figure_id = text_figure_id, component_type="text_label", primary_figure=primary_figure))
        print(f"\nprimary_figure.components (text): {primary_figure.components}")
    # then once those are created:
        return primary_figure.components


################ ------------------- ################
    #   Now all the figure-manipulating stuff. We figure it out here, then just export the result to graph_data to expose. #

    def get_colour_data(self, figure_id):
        """Returns fill colour, outline colour, line width"""

        figure_data = g.canvas.itemconfigure(figure_id)
        fill = figure_data["fill"][-1] if figure_data.get("fill") else g.background_colour
        outline = figure_data["outline"][-1] if figure_data.get("outline") else "black"
        width = figure_data["width"][-1] if figure_data.get("width") else  g.line_width
        return fill, outline, width

    def jiggle_figure(self, figure_instance:node):

        from time import sleep
        #window["figures_list"].set_focus(True)
        move_distance = 2
        sleeptime = .02
        #print(f"FIGURE INSTANCE IN JIGGLE FIGURE: {figure_instance}")
        g.graph.move_figure(figure_instance.figure_id, move_distance, move_distance)
        g.canvas.update_idletasks()
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph.move_figure(figure_instance.figure_id, -move_distance, move_distance)
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph.move_figure(figure_instance.figure_id, -move_distance, -move_distance)
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph.move_figure(figure_instance.figure_id, move_distance, -move_distance)
        sleep(sleeptime)


    def move(self, target_loc, is_temp=False):


        def draw_newline(existing_line_instance:line, line_start, line_end) -> int:
            line_start = (int(line_start[0]), int(line_start[1]))
            line_end = (int(line_end[0]), int(line_end[1]))

            _, outline_colour, line_width = self.get_colour_data(existing_line_instance.figure_id)
            new_line = g.graph.draw_line(line_start, line_end, color=outline_colour, width=line_width)

            g.temp_figures.append(new_line)

            return new_line

        if not g.selected_figure:
            print("No selected figure, cannot move.")
            return

        primary_object = g.selected_figure
        if not primary_object.figure_id:
            print(f"primary object still selected after deletion: {primary_object}")
            g.selected_figure = None
            return

        local_figures = g.graph.get_figures_at_location(g.graph.ClickPosition)
        if not local_figures or not primary_object.figure_id in local_figures:
            print("selected figure not where clicked, returning.")
            return

        assert isinstance(primary_object, node)
        luggage = primary_object.components

        centred = bb.centre_on_target(subject=g.canvas.bbox(primary_object.figure_id), target=target_loc, target_is_point=True)

        if not luggage:# or exclude_text: # turn this off to make the movement happen only when releasing mousebutton.
            g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])
            return

        g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])

        for fig in luggage:
            centred = bb.centre_on_target(subject=g.canvas.bbox(fig.figure_id), target=target_loc, target_is_point=True)
            if fig.component_type == "text_label":

                width, height = bb.bbox_width_and_height(centred)
                centred = centred[0]+(width/2)-2, centred[1]+height/2-2, centred[2]+(width/2)-2, centred[3]+(height/2)-2

            g.graph.relocate_figure(fig.figure_id, centred[0], centred[1])

        if primary_object.connections:

            for line_inst in list(primary_object.connections):
                line_end = line_start = None
                if primary_object == line_inst.to_node :
                    line_start = line_inst.line_start
                    line_end = target_loc
                    line_inst.line_end = target_loc


                if primary_object == line_inst.from_node:
                    line_start = target_loc
                    line_end = line_inst.line_end
                    line_inst.line_start = target_loc

                line_end = (int(line_end[0]), int(line_end[1]))
                new_line = draw_newline(line_inst, line_start=line_start, line_end=line_end)

                if new_line:
                    if g.canvas.find_withtag(line_inst.figure_id):
                        g.graph.delete_figure(line_inst.figure_id)

                    line_inst.figure_id = new_line
                    line_inst.line_start = line_start
                    line_inst.line_end = line_end
                    if line_inst.figure_id in g.temp_figures:
                        g.temp_figures.remove(line_inst.figure_id)

                    g.graph.send_figure_to_back(line_inst.figure_id)

                else:
                    print("No newline created for coords ")

        if g.temp_figures:
            for figure in g.temp_figures:
                if (new_line and figure != new_line) or not new_line:
                    g.graph.delete_figure(figure)


    def draw(self, coordinates:list, values=None, temp=False): #
        """ REMEMBER: We do have to keep sending coordinates here, because it might be custom coords. Instead, send it to here, and immediately give it to g. and use that henceforth. Easiest."""

        g.currently_adding_figure = coordinates

        def add_text_to_figure_centre(leader_instance, current_coords) -> tuple[component, component]:

            text_figure_id = g.graph.draw_text(text=g.current_text, location=(current_coords[-1]))
            new_text_bbox = bb.centre_on_target(subject=g.canvas.bbox(text_figure_id), target=g.canvas.bbox(leader_instance.figure_id))
            half_text_w = (new_text_bbox[2] - new_text_bbox[0])/2
            half_text_h = (new_text_bbox[3] - new_text_bbox[1])/2

            g.graph.relocate_figure(text_figure_id, new_text_bbox[0] + half_text_w, new_text_bbox[1] + half_text_h)
            top_left = g.canvas.bbox(text_figure_id)[0]-5, g.canvas.bbox(text_figure_id)[1]-5
            bottom_right = g.canvas.bbox(text_figure_id)[2]+5, g.canvas.bbox(text_figure_id)[3]+5

            centred_rectangle = bb.centre_on_target(subject=(top_left, bottom_right), target=g.canvas.bbox(leader_instance.figure_id))
            rect = g.graph.draw_rectangle(top_left=(centred_rectangle[0], centred_rectangle[1]), bottom_right=(centred_rectangle[2], centred_rectangle[3]), fill_color="white", line_color=g.lighter_line_colour)

            g.graph.bring_figure_to_front(rect)
            g.graph.bring_figure_to_front(text_figure_id)

            text_instance, text_bg_instance = self.create_component_insts(primary_figure=leader_instance, text_figure_id=text_figure_id, text_bg_id = rect, text=g.current_text)

            return text_instance, text_bg_instance

        print("def draw")
        new_instance = None

        if g.temp_figures:
            print("deleting temp figures")
            for figure_id in g.temp_figures:
                g.graph.delete_figure(figure_id)
                instances = list(i for i in self.nodes if i.figure_id == figure_id)
                if instances:
                    for i in instances:
                        self.nodes.remove(i)
                g.temp_figures = []

        if not g.currently_adding_figure or len(g.currently_adding_figure) == 1:
            print("No g.currently_adding_figure, returning")
            return

        if g.active_tool == "rectangle":
            line_figure_id = g.graph.draw_rectangle(top_left=g.currently_adding_figure[0], bottom_right=g.currently_adding_figure[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)

            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                new_instance = self.create_node_inst(line_figure_id, shape="rectangle")

        elif g.active_tool == "circle":
            # if g.apply_ratio:
            #   import math
            #   d = math.sqrt((g.currently_adding_figure[1][0] - g.currently_adding_figure[0][0])**2 + (g.currently_adding_figure[1][1] - g.currently_adding_figure[0][1])**2)

            line_figure_id = g.graph.draw_oval(top_left=g.currently_adding_figure[0], bottom_right=g.currently_adding_figure[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)

            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                new_instance = self.create_node_inst(line_figure_id, shape="circle")

        elif g.active_tool == "line":

            line_figure_id = g.graph.draw_line(point_from=g.currently_adding_figure[0], point_to=g.currently_adding_figure[1], color=g.line_colour, width=g.line_width)

            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                print("LINE IS NOT TEMP")
                if g.line_type == "polygon": # note: this way of doing polygons doesn't work because you can't move them, selecting selects a specific line, not the full polygon obj.
                    print("Ignore polygons for now.")

                else:
                    g.last_coords = (g.currently_adding_figure[0], g.graph.ClickPosition)
                    new_instance = self.connect_nodes_with_line(line_figure_id=line_figure_id, to_coords = g.graph.ClickPosition)

        if isinstance(new_instance, line) and not g.add_labels_to_lines:
            return []

    ## Here we do the popup to see what text to add
        def get_text_from_popup():
            g.graph.ClickPosition # near to here is where the popup should be.
            popup_bg_col = "#D6D4D0"
            popup_text_col = "#24211D"

            top,right = g.graph.TopRight
            bottom, left = g.graph.BottomLeft

            adjusted_pos = g.graph.ClickPosition[0] + left + 200, g.graph.ClickPosition[1] + top + 100

            popup_window = sg.Window(title="", layout=[
                [sg.Input(default_text="", text_color=popup_text_col, key="popup_text_input", enable_events=True, focus=True)],
                [sg.Ok(button_text="Done", key="popup_text_done"), sg.Cancel(key="popup_text_cancelled")]
                ], location = adjusted_pos, background_color=popup_bg_col, button_color=popup_bg_col, no_titlebar=True, keep_on_top=True, element_justification="center", finalize=True
            )
            popup_window["popup_text_input"].set_focus(True)
            while True:
                event, value = popup_window.read(500)
                if popup_window.is_closed():
                    break
                if event == "popup_text_done":
                    new_text = value["popup_text_input"]
                    g.current_text = new_text
                    break
                if event.startswith("Escape") or event == "popup_text_cancelled":
                    g.current_text = ""
                    break

            popup_window.close()
            #print(f"After popup is closed:\nevent: {event}, value: {value}")

        if new_instance:# and g.current_text:
            get_text_from_popup()
            if g.current_text:
                add_text_to_figure_centre(new_instance, g.currently_adding_figure)
            g.selected_figure = new_instance

        return []

    def select(self, selection_area=None, no_jiggle=False): # selection defaults to clickposition.

        figures = g.graph.get_figures_at_location(selection_area) # this needs to be 'closest to mouse click' will work on it later.
        if not figures:
            return
        figure = figures[0]

        primary_object = self.get_node_by_figure_id(figure)#dd.get_node_by_figure_id(figure_id=figure)
        if not primary_object:
            for nodule in (j for j in self.nodes if j.components):
                matching_comp = list(i for i in nodule.components if nodule.components and i.figure_id == figure)
                if matching_comp and matching_comp[0].parent:
                    primary_object = matching_comp[0].parent
                    print(f"Matching comp has a parent: {matching_comp} // {matching_comp[0].parent}")
                    break
            else:
                print("No selection found, returning.")
                return

        g.selected_figure = primary_object

        if no_jiggle:
            return
        """

        selected_tag = "selected"
        prev_selected = g.canvas.find_withtag(selected_tag)
        if prev_selected:
            for prev in prev_selected:
                g.canvas.dtag(prev, selected_tag)

        coords = g.graph.ClickPosition #== the last place you mouse-up'd.
        g.canvas.addtag_closest(newtag=selected_tag, x=coords[0], y=coords[1])
        matches = g.canvas.find_withtag(selected_tag)
        if not matches:
            print("Nothing at the click site. Returning.")
            return
        #print(f"Figures at this location: {figures}")
        figure = matches[0] if matches else None
        assert len(matches) == 1 # oh now I get why they're better than print statements. They only print when something goes wrong. Ahhhhh.
"""

        if primary_object.components:
            """
            grouped = g.get_siblings(primary_object)

            if grouped:"""
            for component in primary_object.components:
                self.jiggle_figure(component)

        self.jiggle_figure(primary_object)


desk_drawer = desk()
