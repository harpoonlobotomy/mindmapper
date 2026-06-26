""" Just need to figure out the node classes for the mindmapper.
Instead of tracking and changing the figure_id on differing instances of lines etc, it's one instance per completed drawing, and you just point that at a different figure ID. There is literally no reason that can't work and it's the clearest way."""

""" Am gong to have the graph here too, but separate. At least for now."""

from uuid import uuid4
import FreeSimpleGUI as sg
from tkinter import Canvas
import bbox_manip as bb

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

    def clear_all(self):
        self.pointer_index = {}
        self.figure_id_index = {}
        self.selected_figure = None
        self.additional_connection = None
        self.currently_adding_figure = []
        self.temp_figures = []
        g.graph.erase()



    def remove_figure(self, line, replace = None):
        """ Remove from graph with
        delete_figure(line)
        , then remove from wherever it is.
        if replace:
            add replace value wherever line is being removed from."""

        """
            if replace:
            if dd.get_node_by_figure_id(line).connections:
                dd.get_node_by_figure_id(replace).connections = dd.get_node_by_figure_id(line).connections
            #dd.get_node_by_figure_id_by_id(replace).id = line"""
        g.graph.delete_figure(line)

    def clear_temp_figures(self):
        for fig in self.temp_figures:
            self.graph.delete_figure(fig)
        self.temp_figures = []


    def move_figure(self, figure_instance):
        figure_id = figure_instance.figure_id


g = graph_data()



SHAPES = {
    "rectangle": {"radius":0},
    "circle": {},
    "polygon": {"closed":True}
}

COMPONENTS = {
    "text_label": None,
    "text_bg": None
}


from copy import deepcopy

class line:
    def __init__(self, figure_id:int, from_node:node=None, to_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        """ Note: Lines can also have components."""
        self.line_id = uuid4()
        self.figure_id = figure_id
        self.from_node = from_node
        self.to_node = to_node
        self.components:dict[str:component] = deepcopy(COMPONENTS)

        self.start_coords = coords[0]
        self.end_coords = coords[1]
        print(f"line init: {self}")

    def __repr__(self):
        return (f"[[LINE_INST line_id: {str(self.line_id)[:-6]}, figure_id: {self.figure_id}, from_node: {self.from_node.figure_id if self.from_node else "None"}, to_node: {self.to_node.figure_id if self.to_node else "None"}")#{f', components: {self.components}' if self.components else ""}]]")


class component:

    def __init__(self, figure_id:int, component_type:str, primary_figure:node|line):#, text:str=None):
        assert component_type in COMPONENTS
        #assert isinstance(primary_figure, node|line)

        self.figure_id:int = figure_id
        self.parent:node|line = primary_figure
        self.component_type=component_type
        if component_type == "text_label":
            self.text = "text, change later"#text # was originally just going to copy from add_text directly, but if we add it here I can duplicate components without it just taking the current var automatically.
        #or now. self.line:line = line_instance # may merge these later, the components don't care if they're on a line or not. And if they do care they can just check later.
        # exclusively one component type per node max at this point. Design decision.
        print(f"comp init: {self}")
    def __repr__(self):
        return (f"[[COMPONENT INST component_type: {self.component_type}{f', text: {self.text}' if hasattr(self, 'text') else ''}]]")#, figure_id: {self.figure_id}, parent: {self.parent}")


class node:
    def __init__(self, figure_id:int, shape:str):
        assert shape in SHAPES

        self.node_id = uuid4()
        self.figure_id:int = figure_id
        self.shape:str = shape
        self.components:set[component] = set()#dict[str:component] = deepcopy(COMPONENTS)
        self.connections:set = set()# = {}
        print(f"Node init: {self}")

    def __repr__(self):
        return (f"[[NODE INST node_id: {str(self.node_id)[:-6]}, figure_id: {self.figure_id}, shape: {self.shape}{f', components: {self.components}' if self.components else ""}{f', connections: {self.connections}' if self.connections else ""}]]")


class desk:
    def __init__(self):
        self.nodes:set[node] = set() # just all the nodes. Can get the data from those nodes, don't think it needs a dict or anything.

        self.lines:set[line] = set() # do I need the lines separate here? Idk.

        self.components:set[component] = set() # I really shouldn't need this, but I do need to be able to click any component and have it find the match. So I do need a route back from figure_id...
        # temporarily adding this here, but it should be in the class that manages the graph, not here. This is for the elements themselves. It's a desk drawer. graph is the drawing surface.

        self.add_text:str = "test_text" # this is the presence of text in that box, not actually a var written here. Purely for testing.

        self.temp_figures:list[str] = [] # figure_ids for temp items.

    def get_node_by_figure_id(self, figure_id):

        nodes = list(i for i in self.nodes if i.figure_id == figure_id)
        if nodes:
            return nodes[0]
        else:
            components = list(i for i in self.components if i.figure_id == figure_id)
            if components:
                return components[0].parent if components[0].parent else components[0]


    def create_node_inst(self, figure_id, shape="rectangle"):
        """ This is for after the shape is drawn, once we have the figure_id. Only for /nodes/, not lines or components.
        Maybe we get shape from current_tool?"""
        node_inst = node(figure_id, shape)
        self.nodes.add(node_inst)

        return node_inst

    def create_line_inst(self, figure_id:int, to_node:node=None, from_node:node=None, coords:tuple[tuple[int,int],tuple[int,int]]=None):
        """ Just the line version of create_node_inst. Not sure if I should merge them or not. Keeping like this for now."""
        line_inst = line(figure_id, to_node, from_node, coords)
        self.lines.add(line_inst)

        #if self.add_text:
            #self.create_component_insts(line_inst)

        if from_node and to_node:
            to_node.connections.add(line_inst)#] = ({"from_node":from_node})
            from_node.connections.add(line_inst)#] = ({"to_node":to_node})

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
        #g.canvas.update_idletasks()#window.refresh() # without the refresh each time it doesn't visually update. Would like to find a better way but this is it for now.


    def move(self, target_loc, exclude_text=False):
        """ Now immediately jumps to the mouse, so works with single click or a drag. (the print lines get out of hand when dragging but I'll kill those later.)
        NOTE: Currently, drawing multiple lines is adding them all to a group. Need to undo this. Great if I wanted it, but nope."""

        def update_connections():
            """
            self.connections:dict = {} # keys = id(s) of the connective figure(s). values: {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)} # explitly adding from/to nodes and which end of the line they're on. Should be enough to do what I want.

        keys = id(s) of the connective figure(s).\n\nvalues = {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)}
            """
            #connections[line_figure_id] = {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)}


        def draw_newline(self, existing_line_instance:line, line_start, line_end):# -> tuple[None, list]:
            """returns new_line figure_id"""
            _, outline_colour, line_width = self.get_colour_data(existing_line_instance.figure_id)
            new_line = g.graph.draw_line((int(line_start[0]), int(line_start[1])), (int(line_end[0]), int(line_end[1])), color=outline_colour, width=line_width)

            g.temp_figures.append(new_line)
            #done_links.append(existing_line_instance.pointer)

            return new_line

        g.clear_temp_figures()

        if not g.selected_figure:
            print("No selected figure, cannot move.")
            return []
        print(f"g.selected_figure: {g.selected_figure}")
        primary_object = g.selected_figure
        print(f"Primary object about to get_siblings: {primary_object}")
        luggage = primary_object.components
        #siblings = g.get_grouped_figures(g.selected_figure)
        #print(f"Grouped: {grouped}")
        centred = bb.centre_on_target(subject=g.canvas.bbox(primary_object.figure_id), target=target_loc, target_is_point=True)
        print(f"CENTRED: {centred} / TYPE: {primary_object.shape}")

        if not luggage or exclude_text: # now only moves the text/rectangle on mouseup, but moves the main shape the whole time. Just think it looks nicer as it moves.
            g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])
            print("not siblings or exclude_text==True, returning after moving selected figure.")
            return [[g.selected_figure]]

# First move the main object
        g.graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])

        # going to explicitly check for the label parts, because I can see them being specifically reused/altered later. For more general attr, just store somewhere neatly.
        for fig in luggage:
            #fig = dd.get_node_by_figure_id(fig)
            centred = bb.centre_on_target(subject=g.canvas.bbox(fig.figure_id), target=target_loc, target_is_point=True)
            print(f"CENTRED: {centred} / TYPE: {fig.component_type}")
            if fig.component_type == "text":
            #print(f"Fig type: {fig.type}")
            #if fig.figure_id in g.canvas.find_withtag("text"):
            ##configs = g.canvas.itemconfig(fig.id)
            #if "text" in configs:
                width, height = bb.bbox_width_and_height(centred)
                centred = centred[0]+(width/2)-2, centred[1]+height/2-2, centred[2]+(width/2)-2, centred[3]+(height/2)-2
                # does actually correctly centre. Now all three parts act together as one. plenty of room for improvement but it's something.

            g.graph.relocate_figure(fig.figure_id, centred[0], centred[1])

        if primary_object.connections:
            new_lines = []

            for line_inst in list(primary_object.connections):
                print(f"Line: {line_inst}")

                new_line = None

                if line_inst.to_node == primary_object:
                    new_line = draw_newline(line_inst, line_start=line_inst.start_coords, line_end=target_loc)
                    print("line's to-node was the object drawn to. coords 2,3 are used.")
                elif line_inst.from_node == primary_object:
                    #new_line = draw_newline(line_inst, line_start=target_loc, line_end=line_inst.end_coords)
                    new_line = draw_newline(line_inst, line_start=line_inst.end_coords, line_end=target_loc)# not sure which order I prefer. Will add arrows later to test which feels better.
                    print("lines 0 and 1 are to be used, the from node is being moved.")

                if new_line:
                    print(f"line inst: {line_inst}")
                    print(f"line_inst.figure_id: {line_inst.figure_id}")
                    line_coords = g.canvas.coords(line_inst.figure_id)
                    print(f"line coords: {line_coords}")

                    print(f"inst.fromnode: {line_inst.from_node}")
                    print(f"inst.to_node: {line_inst.to_node}")
                    print(f"g.canvas.coords(inst.figure_id): {g.canvas.coords(line_inst.figure_id)}")
                        #line_coords = g.canvas.coords(inst.figure_id)
                        #print(f"line coords: {line_coords}")
                    if g.canvas.find_withtag(line_inst.figure_id):
                        g.graph.delete_figure(line_inst.figure_id)
                    if not self.get_node_by_figure_id(figure_id=new_line):
                        print(f"Newly created line isn't an instance yet, at lest not according to {new_line}")
                        new_inst = self.create_line_inst(new_line, line_inst.to_node, line_inst.from_node, coords=line_coords)
                        #new_inst = add_figure(new_line, type="line")
                        self.create_component_insts(line_inst)
                    else:
                        new_inst = self.get_node_by_figure_id(new_line)#dd.get_node_by_figure_id(figure_id = new_line)
                    new_lines.append(new_inst.figure_id)


                    #new_lines.append(new_inst.pointer)

        #for line in done_links:
        #    g.remove_figure(line)
        #    print("here we add the updated connection data")
#
        #    fig = add_figure(survivor)

        #if survivor in g.temp_figures:
            #g.temp_figures.remove(survivor)

        if g.temp_figures:
            for figure in g.temp_figures:
                if (new_line and figure != new_line) or not new_line:
                    g.graph.delete_figure(figure)

# Now, tricky thing here is I can't just redraw the line (which is probably simplest) because it'll change the ID. Damn. If I can manually set the ID it's fine, otherwise I'll need to figure out some other kind of categorisation because that'll get ungainly.
# Or just an autorun 'replace all instances of x index with the new one'? idk

## Need to move to back and assign + delete temp

                """remain_vert = fig.connections[line]["from_coordinate"]
                            move_vert = fig.connections[line]["to_coordinate"]
                            done_links.append(line)
                        elif fig.connections[line]["from_node"] == fig.id:
                            move_vert = fig.connections[line]["from_coordinate"]
                            remain_vert = fig.connections[line]["to_coordinate"]
                            done_links.append(line)"""



    def draw(self, current_drawing_xy, values, temp=False):

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

        if g.temp_figures:
            for line_figure_id in g.temp_figures:
                g.graph.delete_figure(line_figure_id)
                g.temp_figures = []

        if g.active_tool == "rectangle":
            line_figure_id = g.graph.draw_rectangle(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            """if w.testing:
                a = g.graph.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width = g.line_width)
                b = g.graph.draw_line(point_from=(current_drawing_xy[0][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[1][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)
                c = g.graph.draw_line(point_from=(current_drawing_xy[1][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[0][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)

                for x in (a,b,c):
                    g.temp_figures.append(x)"""

            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                #parent_instance = add_figure(figure_id)
                line_instance = self.create_node_inst(line_figure_id, shape="rectangle")#, add_components = values["add_text"])

                if values["add_text"]:
                    self.create_component_insts(line_instance)

                    figs = add_text_to_figure_centre(line_instance, current_drawing_xy)
                    #print(f"FIGS: {figs}")
                    #figs[1].group_leader=True
                    #fig.group = figs[0].group = figs[1].group = figs[1].pointer
                    #for f in fig, figs[0], figs[1]:
                    #    print(f"Group for {f.id}: {f.group}. Is group leader: {f.group_leader}")

                if line_instance.components:
                    for comp in line_instance.components:
                        g.graph.bring_figure_to_front(comp.figure_id)
                g.selected_figure = line_instance#

        elif g.active_tool == "circle":
            import math
            d = math.sqrt((current_drawing_xy[1][0] - current_drawing_xy[0][0])**2 + (current_drawing_xy[1][1] - current_drawing_xy[0][1])**2) # for properly round circles.

            line_figure_id = g.graph.draw_oval(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            #figure = g.graph.draw_circle(center_location=current_figure[0], radius=d, fill_color=g.fill_colour, line_color=g.line_colour)
            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                #g.figures.append(figure)
                line_instance = self.create_node_inst(line_figure_id, shape="circle")#,
                g.selected_figure = line_instance
                if values.get("add_text"):
                    add_text_to_figure_centre(line_instance, current_drawing_xy)

        elif g.active_tool == "line":

            line_figure_id = g.graph.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width=g.line_width)

            #parent_instance = add_figure(figure_id)
            if temp:
                g.temp_figures.append(line_figure_id)
            else:
                if g.line_type == "polygon": # note: this way of doing polygons doesn't work because you can't move them, selecting selects a specific line, not the full polygon obj.
                    print("Ignore polygons for now.")
                    g.selected_figure = line_instance
                    if values.get("add_text"):
                        add_text_to_figure_centre(self.get_node_by_figure_id(figure_id=line_figure_id), current_drawing_xy)
                    return list((current_drawing_xy[1],))
                else:

                    if values.get("attach_line_to_node"):
                        from_node = g.canvas.find_overlapping(current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10, current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10)

                        """
                            # for i in from_node if dd.get_node_by_figure_id(figure_id=i) and i != figure_id) # export the instances immediately
                        if from_node:
                                from_node = from_node[0]
                            else:
                                from_node = None"""
                        to_node = g.canvas.find_overlapping(current_drawing_xy[1][0]-10, current_drawing_xy[1][1]-10, current_drawing_xy[1][0]+10, current_drawing_xy[1][1]+10)
                        """
                        #if to_node:
                        # to_node = list(dd.get_node_by_figure_id(figure_id=i) for i in to_node if dd.get_node_by_figure_id(figure_id=i) and i != figure_id)
                            if to_node:
                                to_node = to_node[0]
                            else:
                                to_node = None"""

                        from_node = self.get_node_by_figure_id(from_node[0])
                        to_node = self.get_node_by_figure_id(to_node[0])
                        if from_node and to_node:
                            print(f"from node: {from_node}, to_node: {to_node}")
                            line_instance = self.create_line_inst(line_figure_id, from_node, to_node, coords=current_drawing_xy)
                            def replace_line(from_node, to_node, new_line):

                                for node in (from_node, to_node):
                                    if node.connections:
                                        match = list(i for i in node.connections if i.from_node == from_node and i.to_node == to_node)#for connection in from_node.connections: if connection.to_node == to_node:
                                        if match:
                                            node.connections.remove(match[0])
                                            if match[0].components:
                                                new_line.components = match[0]
                                            node.connections.add(new_line)
                                    node.connections.add(new_line)

                            replace_line(from_node, to_node, line_instance)
#                            print(f"From node: {from_node} / to_node: {to_node}")

                            # need to check to see if there's already a link between these two
                        else:
                            print(f"not tonode {to_node} and fromnode: {from_node}")

                        #if values.get("add_text"): # was 'or'
                        #    add_text_to_figure_centre(dd.get_node_by_figure_id(figure_id=line_figure_id), current_drawing_xy)
                        g.selected_figure = to_node if to_node else None
                        """    print(f"Figure_id with from_node and to_node: {line_figure_id}\\nto_node is now selected: {g.selected_figure}")
                                if from_node and to_node:
                                    print(f"g.selected_figure with from_node and to_node: {g.selected_figure}")

                                line_instance.fromnode

                                print("So we have the two and from node at this point, we know they'll be joined. And parent is the line. So we need to swap the figure_id for parent, then we're done, right?")

                            for f in (from_node, to_node):
                                print(f"fig in overlapping start/end: {f}")
                                f_instance = dd.get_node_by_figure_id_by_id_or_pointer(figure_id = f)
                                if f_instance.parent:
                                    f_instance.connections[parent_instance.pointer] =  {"fromnode": dd.get_node_by_figure_id_by_id_or_pointer(from_node).pointer, "from_coordinate": (current_drawing_xy[0]), "tonode": dd.get_node_by_figure_id_by_id_or_pointer(to_node).pointer, "to_coordinate": (current_drawing_xy[1])}
                                    print(f"Fig in overlaps: {f_instance}")
                                #for lap in overlapping:
                                #""if len(overlapping_start) == 2:
                                    g.node_links[figure] = {"from_node": overlapping_start[0], "to_node": overlapping_start[1]}

                                    g.additional_connection.append([(overlapping_start[0], figure), (overlapping_start[1], figure)])
                                    print("Assume first and second (drag order will matter here.)")#"""""
                        g.graph.draw_rectangle((current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10), (current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10), fill_color="blue") # just checking how big the selection box is, this is fine.
                        g.graph.send_figure_to_back(line_figure_id)
                                # I need to loop this into the groups, so it redraws the line when the node is moved. The other end should stay in the same place, only the this-end of the line moves.
                                # Also I kinda want to make it 'zip' to a predefined place on the main shape based on its current location. But that's later.



        return []

    def select(self, selection_area):
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
        print(f"selected: {g.selected_figure}")

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
