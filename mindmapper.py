"""shit I should just make a mind-map script. Goddamn. 10.41am 23/6/26
switching to more instance based to get rid of so many damn ids. Will use nodes_lines_components as a separate script to try to keep it clearer."""


import FreeSimpleGUI as sg
from tkinter import Canvas
import bbox_manip as bb


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
import uuid
class figure_data():

    def __init__(self, id, parent:figure_data=False, figure_type=w.active_tool):
        """
        figure_id\n
        pointer\n
        group\n
        type\n
        connections
        """
        self.figure_id=id
        """ self.figure_id is just the original figure_id that Canvas expects."""
        self.pointer:int = uuid.uuid4()
        """ self.pointer is the address, figure_id is the current resident. Residents can change but we're always at the same house."""

        self.parent:int = parent.pointer if parent else self.pointer
        self.type:str = figure_type

        if self.type == "line":
            self.fromnode = None
            self.tonode = None

        if self.parent == self.pointer and not self.type == "line":
            self.text_child = None
            self.text_bg_child = None
            self.lines=[]

#  CURRENTLY: line works for the first move, then disappears. Just a simple logic fix.

        self.children = []
    # alt:


        self.coords:tuple[int] = g.canvas.coords(self.figure_id)

        self.connections:dict = {} # keys = id(s) of the connective figure(s). values: {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)} # explitly adding from/to nodes and which end of the line they're on. Should be enough to do what I want.
        """
        keys = id(s) of the connective figure(s).\n\nvalues = {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)}
        """
    def __repr__(self):
        return (f"``[ID: {self.figure_id} / Pointer: {self.pointer} / parent: {self.parent} / type: {self.type}]``")

    #def has_connections(self):

"""
I'm thinking I need a layer of abstraction. Give each figure a uuid (which is dumb, but stick with me), and literally set up a dict of uuid:figure_id. Then I can aim everything at the uuid, and can just swap out what it points to.  Much better than whatever else I forgot I was about to do.
"""




class graph_data():

    def __init__(self):
        self.graph_access:sg.Graph = None
        self.canvas:Canvas = None
        self.pointer_index:dict[int:figure_data] = {}
        """[fig.pointer] = fig"""
#        self.reversed_index:dict[figure_data:list[int]] = {}
#        """[figure_data] = fig.pointer"""
        self.figure_id_index:dict[int:figure_data] = {}
        """ There's definitely a better way than three goddamn dictionaries but I'll figure it out tomorrow."""
        self.figure_data:list[figure_data] = []
        self.temp_figures:list[int] = []

        self.background_colour:str = "#D6ECF1"
        self.fill_colour:str = self.background_colour#None
        self.line_colour:str = "black"#None
        self.lighter_line_colour:str = "#494949"

        self.line_width = 3
        self.line_type = "single_line"

        self.currently_adding_figure = []

        self.selection_area = []
        self.selected_figure:int = None
        """ Should always be the pointer. """
        #self.selected_coords:list[int] = []

        self.additional_connection = [] #
        """self.additional_connection.append([(overlapping[0], figure), (overlapping[1], figure)])\n
          just a place to keep all the various connections raw.
          overlapping[0] and [1] are the start and end points of the (updated) line."""

    def clear_all(self):
        self.pointer_index = {}
        self.figure_id_index = {}
        self.selected_figure = None
        self.additional_connection = None
        self.currently_adding_figure = []
        self.temp_figures = []
        g.graph_access.erase()


    def get_siblings(self, instance=None):
        """ Returns a list of pointers for any siblings.
        Optional: It can include the parent, so the parent is moved the same way as the other components. Yes? Will try."""

        if not instance:
            instance = g.get_fig_instance(g.selected_figure)


        parent = g.get_fig_instance(instance.parent)
        siblings = parent.children#(set(parent.children)|set((parent.pointer,))) if parent.children else set((parent.pointer,))


        return siblings

    def get_grouped_figures(self, pointer:int=None, coord:tuple[int,int,int,int]=None) -> list[figure_data]:

        if pointer:

            matches = self.get_siblings(g.get_fig_instance(pointer))
            if matches:
                return matches
            else:
                print(f"No matches for {pointer} in get_grouped. Maybe an error, maybe not.")

    def get_fig_instance(self, pointer=None, figure_id:int=None) -> figure_data:

        """ Here, we need to get the pointer, and only use the figure_id to get to that. We shouldn't apply anything outside of graph elements themselves using figure_id."""

        if pointer and self.pointer_index.get(pointer):
            return self.pointer_index[pointer] # returns the instance from pointer, figure ID is irrelevant until the end of the process.

        if figure_id and self.figure_id_index.get(figure_id):
                return self.figure_id_index[figure_id]


    def remove_figure(self, line, replace = None):
        """ Remove from graph with
        delete_figure(line)
        , then remove from wherever it is.
        if replace:
            add replace value wherever line is being removed from."""

        if replace:
            if g.get_fig_instance(line).connections:
                g.get_fig_instance(replace).connections = g.get_fig_instance(line).connections
            #g.get_fig_instance_by_id(replace).id = line


        g.graph_access.delete_figure(line)

    def clear_temp_figures(self):
        for fig in self.temp_figures:
            self.graph_access.delete_figure(fig)
        self.temp_figures = []


g = graph_data()

def add_figure(figure_id, type=w.active_tool, parent=None) -> figure_data:
    """inits and appends figure instance to figure_data"""
    #g.figures.append(figure)
    fig = figure_data(figure_id, parent=parent, figure_type=type)
    #print(f"Added {figure} to figure_data.")
    """ Going to swap out figure_data for the new index. I want to try to be intentional about when I use pointer vs anything else."""
    g.pointer_index[fig.pointer] = fig
    g.figure_id_index[fig.figure_id] = fig

    return fig


def make_window():
# back at it, 2:56pm

    def get_colour_data(figure_id):
        """Returns fill colour, outline colour, line width"""

        figure_data = g.canvas.itemconfigure(figure_id)
        fill = figure_data["fill"][-1] if figure_data.get("fill") else g.background_colour
        outline = figure_data["outline"][-1] if figure_data.get("outline") else "black"
        width = figure_data["width"][-1] if figure_data.get("width") else  g.line_width
        return fill, outline, width

    def jiggle_figure(figure_instance:figure_data):

        from time import sleep
        #window["figures_list"].set_focus(True)
        move_distance = 2
        sleeptime = .02

        g.graph_access.move_figure(figure_instance.figure_id, move_distance, move_distance)
        g.canvas.update_idletasks()
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph_access.move_figure(figure_instance.figure_id, -move_distance, move_distance)
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph_access.move_figure(figure_instance.figure_id, -move_distance, -move_distance)
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh()
        g.graph_access.move_figure(figure_instance.figure_id, move_distance, -move_distance)
        sleep(sleeptime)
        #g.canvas.update_idletasks()#window.refresh() # without the refresh each time it doesn't visually update. Would like to find a better way but this is it for now.


    def move(target_loc, exclude_text=False):
        """ Now immediately jumps to the mouse, so works with single click or a drag. (the print lines get out of hand when dragging but I'll kill those later.)
        NOTE: Currently, drawing multiple lines is adding them all to a group. Need to undo this. Great if I wanted it, but nope."""

        def update_connections():
            """
            self.connections:dict = {} # keys = id(s) of the connective figure(s). values: {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)} # explitly adding from/to nodes and which end of the line they're on. Should be enough to do what I want.

        keys = id(s) of the connective figure(s).\n\nvalues = {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)}
            """
            #connections[line_figure_id] = {"fromnode": fromnode.id, "from_coordinate": (line_start_xy), "tonode": tonode.id, "to_coordinate": (line_end_xy)}


        def draw_newline(existing_line_instance:figure_data, line_start, line_end):# -> tuple[None, list]:
            """returns new_line figure_id"""
            _, outline_colour, line_width = get_colour_data(existing_line_instance.figure_id)
            new_line = g.graph_access.draw_line(line_start, line_end, color=outline_colour, width=line_width)

            g.temp_figures.append(new_line)
            #done_links.append(existing_line_instance.pointer)

            return new_line

        g.clear_temp_figures()

        if not g.selected_figure:
            print("No selected figure, cannot move.")
            return []
        print(f"g.selected_figure: {g.selected_figure}")
        primary_object = g.get_fig_instance(g.selected_figure)
        print(f"Primary object about to get_siblings: {primary_object}")
        luggage = g.get_siblings(primary_object)
        #siblings = g.get_grouped_figures(g.selected_figure)
        #print(f"Grouped: {grouped}")
        centred = bb.centre_on_target(subject=g.canvas.bbox(primary_object.figure_id), target=target_loc, target_is_point=True)
        print(f"CENTRED: {centred} / TYPE: {primary_object.type}")

        if not luggage or exclude_text: # now only moves the text/rectangle on mouseup, but moves the main shape the whole time. Just think it looks nicer as it moves.
            graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])
            print("not siblings or exclude_text==True, returning after moving selected figure.")
            return [[g.selected_figure]]

# First move the main object
        graph.relocate_figure(primary_object.figure_id, centred[0], centred[1])

        # going to explicitly check for the label parts, because I can see them being specifically reused/altered later. For more general attr, just store somewhere neatly.
        for fig in luggage:
            fig = g.get_fig_instance(fig)
            centred = bb.centre_on_target(subject=g.canvas.bbox(fig.figure_id), target=target_loc, target_is_point=True)
            print(f"CENTRED: {centred} / TYPE: {fig.type}")
            if fig.type == "text":
            #print(f"Fig type: {fig.type}")
            #if fig.figure_id in g.canvas.find_withtag("text"):
            ##configs = g.canvas.itemconfig(fig.id)
            #if "text" in configs:
                width, height = bb.bbox_width_and_height(centred)
                centred = centred[0]+(width/2)-2, centred[1]+height/2-2, centred[2]+(width/2)-2, centred[3]+(height/2)-2
                # does actually correctly centre. Now all three parts act together as one. plenty of room for improvement but it's something.

            graph.relocate_figure(fig.figure_id, centred[0], centred[1])

        if primary_object.lines:
            new_lines = []
            for line in primary_object.lines:
                # MAKE LINE BE THE POINTER
                new_line = None

                print(f"line in primary object lines: {line}")
                line_inst = g.get_fig_instance(line)
                print(f"line inst: {line_inst}")
                # oops: line inst: ``[Pointer: b51be5ad-cfd3-4398-8630-433959a2d4ce / parent: efd45782-9c56-4ace-be55-1fb16fcbc5fd / type: move]``
                # this is a line, but because it was created while I was moving something, it thinks its a 'move' obj which does not exist. No wonder it breaks.
                if not line_inst:
                    print(f"no inst for {line}")
                    exit()

                if line_inst.tonode == primary_object.pointer:
                    new_line = draw_newline(line_inst, line_start=(line_inst.coords[0], line_inst.coords[1]), line_end=target_loc)
                    print("line's to-node was the object drawn to. coords 2,3 are used.")
                elif line_inst.fromnode == primary_object.pointer:
                    new_line = draw_newline(line_inst, line_start=target_loc, line_end=(line_inst.coords[2], line_inst.coords[3]))
                    print("lines 0 and 1 are to be used, the from node is being moved.")

                if new_line:
                    print(f"line inst: {line_inst}")
                    print(f"line_inst.figure_id: {line_inst.figure_id}")
                    line_coords = g.canvas.coords(line_inst.figure_id)
                    print(f"line coords: {line_coords}")

                    print(f"inst.fromnode: {line_inst.fromnode}")
                    print(f"inst.to_node: {line_inst.tonode}")
                    print(f"g.canvas.coords(inst.figure_id): {g.canvas.coords(line_inst.figure_id)}")
                        #line_coords = g.canvas.coords(inst.figure_id)
                        #print(f"line coords: {line_coords}")
                    if g.canvas.find_withtag(line_inst.figure_id):
                        g.graph_access.delete_figure(line_inst.figure_id)
                    if not g.get_fig_instance(figure_id=new_line):
                        print(f"Newly created line isn't an instance yet, at lest not according to {new_line}")
                        new_inst = add_figure(new_line, type="line")
                    else:
                        new_inst = g.get_fig_instance(figure_id = new_line)
                    new_inst.pointer = line_inst.pointer
                    line_inst.pointer = None # god way of showing it's done for.
                    if new_inst.pointer not in new_lines:
                        primary_object.lines.append(new_inst.pointer)
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
                    g.graph_access.delete_figure(figure)

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



    def draw(current_drawing_xy, temp=False):

        def add_text_to_figure_centre(leader_instance:figure_data, current_coords) -> tuple[figure_data, figure_data]:

            text_figure_id = graph.draw_text(text=values["add_text"], location=(current_coords[-1]))
            new_text_bbox = bb.centre_on_target(subject=g.canvas.bbox(text_figure_id), target=g.canvas.bbox(leader_instance.figure_id))
            half_text_w = (new_text_bbox[2] - new_text_bbox[0])/2
            half_text_h = (new_text_bbox[3] - new_text_bbox[1])/2

            graph.relocate_figure(text_figure_id, new_text_bbox[0] + half_text_w, new_text_bbox[1] + half_text_h)
            text_instance = add_figure(text_figure_id, type="text", parent=leader_instance)
            #text_instance.type="text"
            print(f"parent type: {leader_instance.type}")
            text_instance.parent=leader_instance.pointer
            leader_instance.text_child = text_instance.pointer
            leader_instance.children.append(text_instance.pointer)

            #g.canvas.itemconfig(text, {"tags": [["text"], [leader_instance.pointer]]})

            top_left = g.canvas.bbox(text_figure_id)[0]-5, g.canvas.bbox(text_figure_id)[1]-5
            bottom_right = g.canvas.bbox(text_figure_id)[2]+5, g.canvas.bbox(text_figure_id)[3]+5

            centred_rectangle = bb.centre_on_target(subject=(top_left, bottom_right), target=g.canvas.bbox(leader_instance.figure_id))
            rect = graph.draw_rectangle(top_left=(centred_rectangle[0], centred_rectangle[1]), bottom_right=(centred_rectangle[2], centred_rectangle[3]), fill_color="white", line_color=g.lighter_line_colour)
            text_bg_instance = add_figure(rect, "rectangle_sml", parent=leader_instance)
            text_bg_instance.parent=leader_instance.pointer
            #text_bg_instance.type="rectangle_sml"
            #g.canvas.itemconfig(rect, {"tags": [["sml_rect"], [leader_instance.pointer]]})
            leader_instance.text_bg_child = text_bg_instance.pointer
            leader_instance.children.append(text_bg_instance.pointer)
            graph.bring_figure_to_front(text_figure_id)

            return text_instance, text_bg_instance

        if g.temp_figures:
            for figure_id in g.temp_figures:
                g.graph_access.delete_figure(figure_id)
                g.temp_figures = []

        if w.active_tool == "rectangle":
            figure_id = g.graph_access.draw_rectangle(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            if w.testing:
                a = g.graph_access.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width = g.line_width)
                b = g.graph_access.draw_line(point_from=(current_drawing_xy[0][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[1][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)
                c = g.graph_access.draw_line(point_from=(current_drawing_xy[1][0], current_drawing_xy[0][1]), point_to=(current_drawing_xy[0][0], current_drawing_xy[1][1]), color=g.line_colour, width = g.line_width)

                for x in (a,b,c):
                    g.temp_figures.append(x)

            if temp:
                g.temp_figures.append(figure_id)
            else:
                parent_instance = add_figure(figure_id)
                parent_instance.parent=parent_instance.pointer
                parent_instance.type=w.active_tool
                #g.canvas.itemconfig(text, {"tags": [["text"], [leader_instance.pointer]]})
                parent_instance.text_child = None # just let it carry its own damn children.
                parent_instance.text_bg_child = None
                if values["add_text"]:
                    figs = add_text_to_figure_centre(parent_instance, current_drawing_xy)
                    print(f"FIGS: {figs}")
                    #figs[1].group_leader=True
                    #fig.group = figs[0].group = figs[1].group = figs[1].pointer
                    #for f in fig, figs[0], figs[1]:
                    #    print(f"Group for {f.id}: {f.group}. Is group leader: {f.group_leader}")

                g.selected_figure = parent_instance.pointer


        elif w.active_tool == "circle":
            import math
            d = math.sqrt((current_drawing_xy[1][0] - current_drawing_xy[0][0])**2 + (current_drawing_xy[1][1] - current_drawing_xy[0][1])**2) # for properly round circles.

            figure_id = g.graph_access.draw_oval(top_left=current_drawing_xy[0], bottom_right=current_drawing_xy[1], fill_color=g.fill_colour, line_color=g.line_colour, line_width=g.line_width)
            #figure = g.graph.draw_circle(center_location=current_figure[0], radius=d, fill_color=g.fill_colour, line_color=g.line_colour)
            if temp:
                g.temp_figures.append(figure_id)
            else:
                #g.figures.append(figure)
                g.selected_figure = figure_id
                if values.get("add_text"):
                    add_text_to_figure_centre(g.get_fig_instance(figure_id=figure_id), current_drawing_xy)

        elif w.active_tool == "line":

            figure_id = g.graph_access.draw_line(point_from=current_drawing_xy[0], point_to=current_drawing_xy[1], color=g.line_colour, width=g.line_width)
            parent_instance = add_figure(figure_id)
            if temp:
                g.temp_figures.append(figure_id)
            else:
                if g.line_type == "polygon": # note: this way of doing polygons doesn't work because you can't move them, selecting selects a specific line, not the full polygon obj.
                    print("Ignore polygons for now.")
                    if not temp:
                        g.selected_figure = parent_instance.pointer
                        if values.get("add_text"):
                            add_text_to_figure_centre(g.get_fig_instance(figure_id=figure_id), current_drawing_xy)
                        return list((current_drawing_xy[1],))
                else:
                    g.selected_figure = parent_instance.pointer

                    if values.get("attach_line_to_node"):
                        from_node = g.canvas.find_overlapping(current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10, current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10)
                        if from_node:
                            from_node = list(g.get_fig_instance(figure_id=i) for i in from_node if g.get_fig_instance(figure_id=i) and i != figure_id) # export the instances immediately
                            if from_node:
                                from_node = from_node[0]
                            else:
                                from_node = None


                        to_node = g.canvas.find_overlapping(current_drawing_xy[1][0]-10, current_drawing_xy[1][1]-10, current_drawing_xy[1][0]+10, current_drawing_xy[1][1]+10)
                        if to_node:
                            to_node = list(g.get_fig_instance(figure_id=i) for i in to_node if g.get_fig_instance(figure_id=i) and i != figure_id)
                            if to_node:
                                to_node = to_node[0]
                            else:
                                to_node = None

                        if from_node and to_node:
                            print(f"From node: {from_node} / to_node: {to_node}")
                            parent_instance.fromnode = from_node.pointer
                            parent_instance.tonode = to_node.pointer
                            parent_instance.figure_id = figure_id
                            if parent_instance.pointer not in from_node.lines:
                                from_node.lines.append(parent_instance.pointer)
                            if parent_instance.pointer not in to_node.lines:
                                to_node.lines.append(parent_instance.pointer)

                            # check to see if there's already a link between these two
                            g.graph_access.draw_rectangle((current_drawing_xy[0][0]-10, current_drawing_xy[0][1]-10), (current_drawing_xy[0][0]+10, current_drawing_xy[0][1]+10), fill_color="blue") # just checking how big the selection box is, this is fine.
                            if from_node and to_node:
                                print(f"g.selected_figure with from_node and to_node: {g.selected_figure}")
                                g.selected_figure = to_node.pointer
                                print(f"Figure_id with from_node and to_node: {figure_id}\nto_node is now selected: {g.selected_figure}")

                                parent_instance.fromnode

                                print("So we have the two and from node at this point, we know they'll be joined. And parent is the line. So we need to swap the figure_id for parent, then we're done, right?")





                            """
                            for f in (from_node, to_node):
                                print(f"fig in overlapping start/end: {f}")
                                f_instance = g.get_fig_instance_by_id_or_pointer(figure_id = f)
                                if f_instance.parent:
                                    f_instance.connections[parent_instance.pointer] =  {"fromnode": g.get_fig_instance_by_id_or_pointer(from_node).pointer, "from_coordinate": (current_drawing_xy[0]), "tonode": g.get_fig_instance_by_id_or_pointer(to_node).pointer, "to_coordinate": (current_drawing_xy[1])}
                                    print(f"Fig in overlaps: {f_instance}")
                                #for lap in overlapping:
                                #""if len(overlapping_start) == 2:
                                    g.node_links[figure] = {"from_node": overlapping_start[0], "to_node": overlapping_start[1]}

                                    g.additional_connection.append([(overlapping_start[0], figure), (overlapping_start[1], figure)])
                                    print("Assume first and second (drag order will matter here.)")#"""""
                        else:
                            print(f"not tonode {to_node} and fromnode: {from_node}")
                        g.graph_access.send_figure_to_back(figure_id)
                                # I need to loop this into the groups, so it redraws the line when the node is moved. The other end should stay in the same place, only the this-end of the line moves.
                                # Also I kinda want to make it 'zip' to a predefined place on the main shape based on its current location. But that's later.

                    if values.get("add_text") and values.get("attach_line_to_node"): # was 'or'
                        add_text_to_figure_centre(g.get_fig_instance(figure_id=figure_id), current_drawing_xy)

        return []

    def select(selection_area):
        figures = graph.get_figures_at_location(selection_area)
        if not figures:
            print("No figures at location.")
            return
        #print(f"Figures at this location: {figures}")
        figure = figures[0] if figures else None

        #print(f"g.canvas coords for newly selected figure: {g.canvas.coords(figure)} / figure: {figure}")
        primary_object = g.get_fig_instance(figure_id=figure)

        grouped = g.get_siblings(primary_object)

        if grouped:
            for i in grouped:
                jiggle_figure(g.get_fig_instance(pointer=i))

        jiggle_figure(primary_object)


    def update_ratio(event, values):

        if event == "ratio_part_1" and values["ratio_part_1"] != w.ratio_part_1:
            print(f"updated ratio_part_1 to {values['ratio_part_1']}")
            w.ratio_part_1 = values["ratio_part_1"]

        if event == "ratio_part_2" and values["ratio_part_2"] != w.ratio_part_2:
            print(f"updated ratio_part_2 to {values['ratio_part_2']}")
            w.ratio_part_2 = values["ratio_part_2"]


    def show_set_ratio(force_visible=False, force_hidden=False, ignore_checkbox=False):

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
        select_tool(w.active_tool)
        g.graph_access = window["graph"] ## type: sg.Graph
        g.canvas = window["graph"].Widget


    setup_window()
    g.currently_adding_figure = []

    while True and not window.is_closed():
        event, values = window.read(3000)
        if event and event != "__TIMEOUT__":

            if (isinstance(event, str) and event.startswith("Escape")) or window.is_closed():
                break

            if event == "new":
                print("event new")
                g.graph_access.erase()
                print("also a fn here to clear all the data regarding said figures.")

            #print(f"EVENT: {event}")
            if event.startswith("graph"):

                if w.active_tool in ("rectangle", "circle", "line"):

                    if event == "graph+UP":
                        g.currently_adding_figure.append(values["graph"])
                        g.currently_adding_figure = draw(g.currently_adding_figure)

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
                        if event == "graph":
                            move(values["graph"], exclude_text=True)
                        if event == "graph+UP":
                            print("graph UP")
                            move(values["graph"])


            elif g.currently_adding_figure:
                g.currently_adding_figure = []#= draw(g.current_figure) # so that if you click anything non-graph while drawing a polygon, it just ends drawing that polygon.

            elif event in ("rectangle", "circle", "line", "select", "move"):
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
                w.active_tool = "rectangle"
                continue
        else:
            break


run()
