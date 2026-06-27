""" Just need to figure out the node classes for the mindmapper.
Instead of tracking and changing the figure_id on differing instances of lines etc, it's one instance per completed drawing, and you just point that at a different figure ID. There is literally no reason that can't work and it's the clearest way."""

""" Am gong to have the graph here too, but separate. At least for now."""

from uuid import uuid4
import FreeSimpleGUI as sg
from tkinter import Canvas
import bbox_manip as bb


SHAPES = {
    "rectangle": {"radius":0},
    "circle": {},
    "polygon": {"closed":True}
}

COMPONENTS = {
    "text_label": None,
    "text_bg": None
}


def print_s(string:str):
    pass

class graph_data():

    def __init__(self):

        self.graph:sg.Graph = None
        self.canvas:Canvas = None

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

        self.last_line:line = None # literally just here to fix the infinite lines, so I can just store the last one. It's so stupid.

    def clear_all(self):
        self.pointer_index = {}
        self.figure_id_index = {}
        self.selected_figure = None
        self.additional_connection = None
        self.currently_adding_figure = []
        self.temp_figures = []
        g.graph.erase()



    def remove_figure(self, figure_id, replace = None):

        if g.canvas.find_withtag(figure_id):
            g.graph.delete_figure(figure_id)



    def clear_temp_figures(self):
        for fig in self.temp_figures:
            self.remove_figure(fig)

        self.temp_figures = []


g = graph_data()




class line:


    def __init__(self, figure_id:int, from_node:node=None, to_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        from copy import deepcopy
        """ Note: Lines can also have components."""
        self.line_id = uuid4()
        self.figure_id = figure_id
        self.from_node = from_node
        self.to_node = to_node
        self.components:dict[str:component] = deepcopy(COMPONENTS)

        self.set_coords(coords)

        print(f"line init: {self} / coords: {coords}")

    def set_coords(self, coords):
        print(f"COORDS: {coords}")
        if len(coords) == 1:
            coords = coords[0]
        if len(coords) == 4:
            coords = (int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3]))

        self.line_start = coords[0]
        self.line_end = coords[1]
        print(f"self.line_start: {self.line_start}, self.line_end: {self.line_end}")

    def __repr__(self):
        return (f"[[LINE_INST line_id: {str(self.line_id)[:-6]}, figure_id: {self.figure_id}, from_node.figure_id: {self.from_node.figure_id if self.from_node else "None"}, to_node.figure_id: {self.to_node.figure_id if self.to_node else "None"}, line_start: {self.line_start}, line_end: {self.line_end}]]")


class component:

    def __init__(self, figure_id:int, component_type:str, primary_figure:node|line):#, text:str=None):
        assert component_type in COMPONENTS
        assert isinstance(primary_figure, node|line)

        self.figure_id:int = figure_id
        self.parent:node|line = primary_figure
        self.component_type=component_type
        self.text = None # used to store after init, not for init fetching.text is given at each instance's init, not globally.
        print(f"comp init: {self}")
    def __repr__(self):
        return (f"[[COMPONENT INST component_type: {self.component_type}{f', text: {self.text}' if hasattr(self, 'text') else ''}]]")#, figure_id: {self.figure_id}, parent: {self.parent}")


class node:
    def __init__(self, figure_id:int, shape:str, bbox:tuple[int]):
        assert shape in SHAPES

        self.node_id = uuid4()
        self.figure_id:int = figure_id
        self.shape:str = shape

        self.centrepoint = bb.get_half_dimensions(bbox)

        self.components:set[component] = set()#dict[str:component] = deepcopy(COMPONENTS)
        self.connections:set[line] = set()# = {}
        print(f"Node init: {self}")

    def __repr__(self):
        return (f"[[NODE INST node_id: {str(self.node_id)[:-6]}, figure_id: {self.figure_id}, shape: {self.shape}{f', components: {self.components}' if self.components else ""}{f', connections: {self.connections}' if self.connections else ""}]]")


class desk:
    def __init__(self):
        self.nodes:set[node] = set() # just all the nodes. Can get the data from those nodes, don't think it needs a dict or anything.

        self.lines:set[line] = set() # do I need the lines separate here? Idk.

        self.components:set[component] = set() # I really shouldn't need this, but I do need to be able to click any component and have it find the match. So I do need a route back from figure_id...
        # temporarily adding this here, but it should be in the class that manages the graph, not here. This is for the elements themselves. It's a desk drawer. graph is the drawing surface.

        self.temp_figures:list[str] = [] # figure_ids for temp items.

    def get_node_by_figure_id(self, figure_id):

        nodes = list(i for i in self.nodes if i.figure_id == figure_id)
        if nodes:
            return nodes[0]
        else:
            components = list(i for i in self.components if i.figure_id == figure_id)
            if components:
                return components[0].parent if components[0].parent else components[0]


    def update_node_line_data(self, _node:node, _line:line, new_figure_id):
        """ This should be a nodes fn probably."""
        ## to update:
        old_id = _node.figure_id
        _node.figure_id = new_figure_id
        """
        If any existing connections with this to_ and from_ node:
            that's the line you need to redraw.

        """

        #
        print("Here we make sure the coordinate/start/end are up to date, and that both nodes have updated the connection. This runs per node, during the connection check.")
        print(f"Node to update: {_node.figure_id}")


    def create_node_inst(self, figure_id, shape="rectangle", bbox=None):
        """ This is for after the shape is drawn, once we have the figure_id. Only for /nodes/, not lines or components.
        Maybe we get shape from current_tool?"""
        node_inst = node(figure_id, shape, bbox)
        self.nodes.add(node_inst)

        return node_inst

    def create_line_inst(self, figure_id:int, from_node:node=None, to_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        """ Just the line version of create_node_inst. Not sure if I should merge them or not. Keeping like this for now."""
        line_inst = line(figure_id, from_node, to_node, coords)
        print(f"ADDING {self} TO LINES NOW.")
        self.lines.add(line_inst)

        if from_node and to_node:
            to_node.connections.add(line_inst)#] = ({"from_node":from_node})
            from_node.connections.add(line_inst)#] = ({"to_node":to_node})

        print(f"Returning line_inst: {line_inst}")
        return line_inst


    def create_component_insts(self, primary_figure:node|line, text_figure_id:int=None, text_bg_id:int=None):#node_inst:node=None, line_inst:line=None):
        """ Can be used on its own to add components"""
        #assert isinstance(node_inst, node) if node_inst else isinstance(line_inst, line)

        #primary_figure = node_inst if node_inst else line_inst # so I don't have to do it separately depending. Might merge them later, idk.

        if text_figure_id:
            primary_figure.components.add(component(figure_id = text_figure_id, component_type="text_label", primary_figure=primary_figure))
        #text_figure_id, text_bg_id = 6,7#"fn here where we make the text figure + bg rectangle, can't be bothered rn"
    # then once those are created:
        if text_bg_id:
            primary_figure.components.add(component(figure_id=text_bg_id, component_type="text_bg", primary_figure=primary_figure))
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


    def move(self, target_loc, exclude_text=False):

        def draw_newline(existing_line_instance:line, line_start, line_end) -> int:
            line_start = (int(line_start[0]), int(line_start[1]))
            line_end = (int(line_end[0]), int(line_end[1]))
            """returns new_line figure_id"""
            print(f"in draw_newline. Existing line: {existing_line_instance} // line_start: {line_start} / line_end: {line_end}")
            if existing_line_instance.line_start == line_start and existing_line_instance.line_end == line_end:
                print("Existing instance is already at these positions; returning existing ID, no further action.")
                return 5
            _, outline_colour, line_width = self.get_colour_data(existing_line_instance.figure_id)
            new_line = g.graph.draw_line(line_start, line_end, color=outline_colour, width=line_width)

            g.temp_figures.append(new_line)

            return new_line

        if not g.selected_figure:
            print("No selected figure, cannot move.")
            return

        primary_object = g.selected_figure

        luggage = primary_object.components

        centred = bb.centre_on_target(subject=g.canvas.bbox(primary_object.figure_id), target=target_loc, target_is_point=True)

        if not luggage or exclude_text:
            g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])
            return

# First move the main object
        g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])

        for fig in luggage:
            centred = bb.centre_on_target(subject=g.canvas.bbox(fig.figure_id), target=target_loc, target_is_point=True)
            if fig.component_type == "text_label":

                width, height = bb.bbox_width_and_height(centred)
                centred = centred[0]+(width/2)-2, centred[1]+height/2-2, centred[2]+(width/2)-2, centred[3]+(height/2)-2

            g.graph.relocate_figure(fig.figure_id, centred[0], centred[1])

        if primary_object.connections:
            new_lines = []

            for line_inst in list(primary_object.connections):
                print(f"Line: {line_inst} / target_loc: {target_loc}")
                if line_inst.line_end == target_loc or line_inst.line_start == target_loc:#line_start = line_inst.line_start
                                                #line_end=target_loc
                    if line_inst.figure_id in g.temp_figures:
                        g.temp_figures.remove(line_inst.figure_id)
                    print("The existing one has the same coords, just reuse this.\n---------------------------------------------------\n")
                    return
                line_start = line_end = new_line = None


                if line_inst.to_node == primary_object:
                    "check if from_node would also match if created by draw_newline - if so, then the existing instance is perfect and should remain exactly where it is."
                    line_start = line_inst.line_start
                    line_end=target_loc

                elif line_inst.from_node == primary_object:
                    line_start = line_inst.line_end
                    line_end=target_loc

                else:
                    print(f"line inst does not match from node or to node: {line_inst.figure_id}")
                    return

                line_start = (int(line_start[0]), int(line_start[1]))
                line_end = (int(line_end[0]), int(line_end[1]))
                #new_line = draw_newline(line_inst, line_start=target_loc, line_end=line_inst.line_end)
                new_line = draw_newline(line_inst, line_start=line_start, line_end=line_end)
                if new_line == 5:
                    print("Using existing line instead of newline. Returning from def move().")
                    return
                if new_line:

                    if g.canvas.find_withtag(line_inst.figure_id):
                        g.graph.delete_figure(line_inst.figure_id)

                    line_inst.figure_id = new_line
                    line_inst.line_start = line_start
                    line_inst.line_end = line_end
                    if line_inst.figure_id in g.temp_figures:
                        g.temp_figures.remove(line_inst.figure_id)
                    print("line_inst is updated, returning now.")
                    return
                    """
                    if not self.get_node_by_figure_id(figure_id=new_line):
                        print("THIS IS WHERE I NEED TO FIND THE EXISTING LINE.")
                        coord_matches = list(i for i in self.lines if i.line_start == line_start and i.line_end == line_end)
                        if coord_matches:
                            print("IF COORD MATCHES:")
                            print("coord_matches\n\n\n\n\n")
                    print(f"Newly created line isn't an instance yet, at lest not according to {new_line}")
                    new_inst = self.create_line_inst(new_line, line_inst.from_node, line_inst.to_node, coords=(line_start, line_end))


                    else:
                        new_inst = self.get_node_by_figure_id(new_line)
                    if new_line not in new_lines:
                        new_lines.append(new_inst.figure_id)
                """
                else:
                    print("No newline created for coords ")

        if g.temp_figures:
            for figure in g.temp_figures:
                if (new_line and figure != new_line) or not new_line:
                    g.graph.delete_figure(figure)


    def draw(self, current_drawing_xy:tuple, values:dict, temp=False):

        def find_nodes_for_line():

            from_node = g.canvas.find_overlapping(current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10, current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10)

            to_node = g.canvas.find_overlapping(current_drawing_xy[1][0]-10, current_drawing_xy[1][1]-10, current_drawing_xy[1][0]+10, current_drawing_xy[1][1]+10)

            if not from_node or not to_node:
                print("Either no from or no to node at click, returning null.")
                return None

            from_node = self.get_node_by_figure_id(from_node[0])
            to_node = self.get_node_by_figure_id(to_node[0])
            return from_node, to_node

        def connect_nodes_with_line(newly_drawn_line_fID):
            from_node = g.canvas.find_overlapping(current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10, current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10)

            to_node = g.canvas.find_overlapping(current_drawing_xy[1][0]-10, current_drawing_xy[1][1]-10, current_drawing_xy[1][0]+10, current_drawing_xy[1][1]+10)

            from_node = self.get_node_by_figure_id(from_node[0])
            to_node = self.get_node_by_figure_id(to_node[0])
            if from_node and to_node:
                def remove_previous_connection(from_node, to_node):

                    for _node in (from_node, to_node):
                        if not isinstance(_node, node):
                            print("from or to node is not a node-node.")
                            return
                        print(f"NODE in replace_line: {_node.figure_id}\n")
                        if _node.connections:
                            match = list(i for i in _node.connections if (i.from_node == from_node and i.to_node == to_node) or (i.to_node == from_node and i.from_node == to_node))#for connection in from_node.connections: if connection.to_node == to_node:
                            if match:
                                print(f"match founbd in node.connections: {match[0]}")
                                self.update_node_line_data(_node, _line=match, new_figure_id=newly_drawn_line_fID)
                                print(f"instance after update_node_line_data: {_node}")
                                #match.figure_id = newly_drawn_line_fID
                                #print(f"replacing old figure_id with the new one to see if that works: {match}")
                                return 5
                outcome = remove_previous_connection(from_node, to_node)

                new_instance = self.create_line_inst(newly_drawn_line_fID, from_node, to_node, coords=current_drawing_xy)

            else:
                print(f"not tonode {to_node} and/or fromnode: {from_node}")

            g.selected_figure = to_node if to_node else None

            g.graph.send_figure_to_back(newly_drawn_line_fID)

        def add_text_to_figure_centre(leader_instance, current_coords) -> tuple[component, component]:

            text_figure_id = g.graph.draw_text(text=values["add_text"], location=(current_coords[-1]))
            new_text_bbox = bb.centre_on_target(subject=g.canvas.bbox(text_figure_id), target=g.canvas.bbox(leader_instance.figure_id))
            half_text_w = (new_text_bbox[2] - new_text_bbox[0])/2
            half_text_h = (new_text_bbox[3] - new_text_bbox[1])/2

            g.graph.relocate_figure(text_figure_id, new_text_bbox[0] + half_text_w, new_text_bbox[1] + half_text_h)
            #text_instance = add_figure(text_figure_id, type="text", parent=leader_instance)

            #text_instance.type="text"

            #g.canvas.itemconfig(text, {"tags": [["text"], [leader_instance.pointer]]})

            top_left = g.canvas.bbox(text_figure_id)[0]-5, g.canvas.bbox(text_figure_id)[1]-5
            bottom_right = g.canvas.bbox(text_figure_id)[2]+5, g.canvas.bbox(text_figure_id)[3]+5

            centred_rectangle = bb.centre_on_target(subject=(top_left, bottom_right), target=g.canvas.bbox(leader_instance.figure_id))
            rect = g.graph.draw_rectangle(top_left=(centred_rectangle[0], centred_rectangle[1]), bottom_right=(centred_rectangle[2], centred_rectangle[3]), fill_color="white", line_color=g.lighter_line_colour)
            #text_bg_instance = add_figure(rect, "rectangle_sml", parent=leader_instance)
            #text_bg_instance.parent=leader_instance.pointer
            #text_bg_instance.type="rectangle_sml"
            #g.canvas.itemconfig(rect, {"tags": [["sml_rect"], [leader_instance.pointer]]})
            #leader_instance.text_bg_child = text_bg_instance.pointer
            #leader_instance.children.append(text_bg_instance.pointer)
            g.graph.bring_figure_to_front(rect)
            g.graph.bring_figure_to_front(text_figure_id)

            text_instance, text_bg_instance = self.create_component_insts(primary_figure=leader_instance, text_figure_id=text_figure_id, text_bg_id = rect)

            return text_instance, text_bg_instance

        new_instance = None

        if g.temp_figures:
            for figure_id in g.temp_figures:
                g.graph.delete_figure(figure_id)
                instances = list(i for i in self.nodes if i.figure_id == figure_id)
                if instances:
                    for i in instances:
                        self.nodes.remove(i)
                g.temp_figures = []

        if g.active_tool == "rectangle":
            rectangle_figure_id = g.graph.draw_rectangle(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            """if w.testing:
                a = g.graph.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width = g.line_width)
                b = g.graph.draw_line(point_from=(current_drawing_xy[0][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[1][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)
                c = g.graph.draw_line(point_from=(current_drawing_xy[1][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[0][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)

                for x in (a,b,c):
                    g.temp_figures.append(x)"""

            if temp:
                g.temp_figures.append(rectangle_figure_id)
            else:
                bbox = g.canvas.bbox(rectangle_figure_id)
                new_instance = self.create_node_inst(rectangle_figure_id, shape="rectangle", bbox=bbox)#, add_components = values["add_text"])

        elif g.active_tool == "circle":
            import math
            d = math.sqrt((current_drawing_xy[1][0] - current_drawing_xy[0][0])**2 + (current_drawing_xy[1][1] - current_drawing_xy[0][1])**2) # for properly round circles.

            circle_figure_id = g.graph.draw_oval(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            #figure = g.graph.draw_circle(center_location=current_figure[0], radius=d, fill_color=g.fill_colour, line_color=g.line_colour)
            if temp:
                g.temp_figures.append(circle_figure_id)
            else:
                bbox = g.canvas.bbox(circle_figure_id)
                new_instance = self.create_node_inst(circle_figure_id, shape="circle", bbox = bbox)

        elif g.active_tool == "line":

            line_figure_id = g.graph.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width=g.line_width)

            #parent_instance = add_figure(figure_id)
            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                if g.line_type == "polygon": # note: this way of doing polygons doesn't work because you can't move them, selecting selects a specific line, not the full polygon obj.
                    print("Ignore polygons for now.")
                    g.selected_figure = new_instance
                    if values.get("add_text"):
                        add_text_to_figure_centre(self.get_node_by_figure_id(figure_id=line_figure_id), current_drawing_xy)
                    return list((current_drawing_xy[1],))
                else:
                    if values.get("attach_line_to_node"):
                        outcome = connect_nodes_with_line(newly_drawn_line=line_figure_id)
                        if outcome == 5:
                            print("Using the existing instance, just with the new coords and figure_id")


# just turning off the components for now.
        """if new_instance and values["add_text"]:
            self.create_component_insts(new_instance)

            figs = add_text_to_figure_centre(new_instance, current_drawing_xy)

            if new_instance.components:
                for comp in new_instance.components:
                    g.graph.bring_figure_to_front(comp.figure_id)
            """


        return []

    def select(self, selection_area):
        print(f"selection area: {selection_area}")
        figures = g.graph.get_figures_at_location(selection_area) # this needs to be 'closest to mouse click' will work on it later.
        if not figures:
            print("No figures at location.")
            return
        #print(f"Figures at this location: {figures}")
        figure = figures[0] if figures else None

        #print(f"g.canvas coords for newly selected figure: {g.canvas.coords(figure)} / figure: {figure}")
        primary_object = self.get_node_by_figure_id(figure)#dd.get_node_by_figure_id(figure_id=figure)
        if not primary_object:
            print("No selection found, returning.")
            return

        if primary_object.components:
            """
            grouped = g.get_siblings(primary_object)

            if grouped:"""
            for component in primary_object.components:
                self.jiggle_figure(component)

        self.jiggle_figure(primary_object)
        g.selected_figure = primary_object
        print(f"selected: {g.selected_figure.figure_id}")

desk_drawer = desk()

"""     These are all elements that should be in the main script, not here.
def draw_line(start, end, temp=False):

    ### Oh. I could have a defined graph 'layer' for lines, and draw them all at that height, and same for primary shapes/text/etc. Oh I should actually do that.

    line_figure_id = 1#"draw_line_fn(start, end)"

    if temp:
        # move to back
        drawer.temp_figures.append(line_figure_id)

    # here we check for start/end nodes
    start_node, end_node = node_1, node_2#"checking fn"

    drawer.create_line_inst(line_figure_id, from_node=start_node, to_node=end_node)
    # Then move the line to the back


def draw_rectangle(start, end, temp=False):

    force_square=False # get this from the gui
    if force_square:
        "make radio 1:1 when drawing. Whichever is larger, x or y."

    # here grab the radius for rounded corners.

    rect_figure_id = 2 # draw_rectangle(top_left, bottom_right)

    if temp:
        drawer.temp_figures.append(rect_figure_id)

    node_inst = drawer.create_node_inst(rect_figure_id, shape="rectangle")
    return node_inst


def draw_circle(start, end):

    force_round=False # get this from the gui

    if not force_round:
        circle_figure_id = 3 # draw_oval(start, end)
    else:
        distance = 60 # math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        circle_figure_id = 3 # draw_circle(start, distance)

    drawer.create_node_inst(circle_figure_id, shape="circle")



node_1 = draw_rectangle(start=(0,0), end=(200,200))

node_2 = draw_rectangle(start=(400,400), end=(600,600))

 line_xy = (190,195), (403,400)

line_figure_id = 3#draw_line(start=line_xy[0], end=line_xy[1])
line_inst = drawer.create_line_inst(figure_id=line_figure_id, from_node=node_1, to_node=node_2)

#print(f"drawer.nodes: {drawer.nodes}")
#for node_inst in drawer.nodes:
#    print(f"node_inst: {node_inst.__dir__}")


for line_inst in drawer.lines:
    print(f"\n\nline inst: {line_inst}\n\n\n")



## Maybe lines can /only/ connect two things. Trying to draw a line that doesn't go anywhre just disappears. I hate that though. no.
"""
