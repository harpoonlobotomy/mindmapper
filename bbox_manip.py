"""collection of reusable PIL/pillow functions. v v v early version.\nNeed to get my old util files and pull the useful things.\nAlso need to formalise the formatting for elements."""


from random import randint

from PIL import Image, ImageDraw, ImageFont

def expand_bbox_tuples(bbox:tuple[float, float, float, float]|tuple[tuple, tuple], default_to_point=True) -> tuple[float, float, float, float]:
    """ Just exists to convert ((0,0), (0,0)) to (0,0,0,0). Will modify to offer the inverse."""
    if not isinstance(bbox, tuple) or len(bbox) == 4:
        return bbox

    elif len(bbox) == 2 and isinstance(bbox[0], int|float):
        if default_to_point:
            bbox = bbox[0]-2, bbox[1]-2, bbox[0], bbox[1]
            return bbox

        # here i assume it's xy given as dimensions, so we give 0,0 as origin.
        bbox = (0,0, bbox[0], bbox[1])
        return bbox

    bbox = bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1]
    return bbox


def condense_bbox_tuple(bbox:tuple[float, float, float, float]|tuple[tuple, tuple]) -> tuple[tuple[float, float],tuple[float,float]]:
    """ Returns `tuple((0,0),(0,0))` constructed from bbox (assumed to be `tuple(0,0,0,0)`)"""
    if len(bbox) == 2 and isinstance(bbox[0], tuple):
        pass
        #(already nested tuples.)
    elif len(bbox) == 2 and isinstance(bbox[0], int|float):
        # here i assume it's xy given as dimensions, so we give 0,0 as origin.
        bbox = (0,0), bbox
    else:
        bbox = (bbox[0], bbox[1]), (bbox[2], bbox[3])
    return bbox


def bbox_width_and_height(bbox) -> tuple[float, float]:
    """Returns `width, height` for the given bbox."""

    left, top, right, bottom = expand_bbox_tuples(bbox)
    width = right - left
    height = bottom - top
    return width, height


def get_half_dimensions(bbox):
    width, height = bbox_width_and_height(bbox)
    return int(width/2), int(height/2)


def align_to(bbox:tuple[float,float,float,float], destination:tuple[float|int, float|int]|float|int=380, direction:str="right", margin:int=4):
    """Align given bbox against a given coordinate. Does not change scale etc.\n
    Example using defaults: move bbox to have its right edge sitting at 380px - 4px for margin\n
    destination can either be a single value, or a tuple.
    If a tuple, it's either (x,y), ((x,y),(x2,y2)) or (x,y,x2,y2)"""

    if direction in ("left", "right"):
        left_right=True
    else:
        left_right=False

    if direction in ("left", "top"):
        left_top=True
    else:
        left_top=False

    left_edge, top_edge, right_edge, bottom_edge = bbox


    if not isinstance(destination, float|int):

        if len(destination) == 2 and isinstance(destination[0], float|int):
            if left_right:
                value = destination[0]
            else:
                value = destination[1]

        elif len(destination) == 2 and isinstance(destination[0], float|int):
            if direction in left_top:
                if direction == "left":
                    value = destination[0][0]
                else:
                    value = destination[0][1]
            else:
                if direction == "right":
                    value = destination[1][0]
                else:#if direction == "bottom":
                    value = destination[1][1]
        else:
            if direction == "left":
                value = destination[0]
            elif direction == "top":
                value = destination[1]
            elif direction == "right":
                value = destination[2]
            else:#if direction == "bottom":
                value = destination[3]

    else:
        value = destination

    if left_top:
        value = value+margin
    else:
        value = value-margin

    left_edge, top_edge, right_edge, bottom_edge = bbox
    if left_right:
        w,_ = bbox_width_and_height(bbox)
        if direction == "left":
            left_edge = value
            right_edge = value + w
        else: # direction == "right":
            left_edge = value - w
            right_edge = value

    else:
        _, h = bbox_width_and_height(bbox)
        if direction == "top":
            top_edge = value
            bottom_edge = value + h#(bottom_edge-top_edge)
        else: # direction == "bottom":
            top_edge = value - h#(bottom_edge-top_edge)
            bottom_edge = value

    return left_edge, top_edge, right_edge, bottom_edge


def scale_rect(bbox:tuple[float,float,float,float], scale_x:float=.8, scale_y=0, scale_is_percentage=True, expand_from_centre=True) -> tuple[tuple[float,float],tuple[float,float]]:
    """ Applies the scale to the bbox; negatively for idx 0 and idx 1, positively for idx 2 and idx 3. Set scale_is_percentage to False to provide pixel amount.\n\
        scale_x is default 'scale'; if no scale_y is given, will apply scale_x on both axes."""
    bbox = expand_bbox_tuples(bbox)

    if not scale_y:
        scale_y = scale_x

    if not scale_is_percentage:
        new_top_left = bbox[0] - (scale_x/2), bbox[1] - (scale_y/2)
        new_bottom_right = bbox[2] + (scale_x/2), bbox[3] + (scale_y/2)
        new_bbox = new_top_left, new_bottom_right
        return new_bbox

    new_top_left = bbox[0]*scale_x, bbox[1]*scale_y
    new_bottom_right = bbox[2]*scale_x, bbox[3]*scale_y
    new_bbox = new_top_left, new_bottom_right

    if expand_from_centre:
        centre_on_target(new_bbox, bbox)

    return new_bbox

def move_rect(bbox:tuple[float,float,float,float], left:int=None, right:int=None, up:int=None, down:int=None) -> tuple[float,float,float,float]:
    """ Left and Up are applied negatively (so left=10 moves -10 on x)"""

    bbox = expand_bbox_tuples(bbox)

    bbox_l = bbox[0]
    bbox_r = bbox[2]
    bbox_t = bbox[1]
    bbox_b = bbox[3]

    if left and right:
        print("both left and right given; moving left to the left and right to the right; this is a workaround to manual resizing.")
        bbox_l = bbox_l - left
        bbox_r = bbox_r + right

    elif left or right:
        if left:
            bbox_l = bbox_l - left
            bbox_r = bbox_r - left
        else:
            bbox_l = bbox_l + right
            bbox_r = bbox_r + right


    if up and down:
        bbox_t = bbox_t - up
        bbox_b = bbox_b + down

    elif up or down:
        if up:
            bbox_t = bbox_t - up
            bbox_b = bbox_b - up
        else:
            bbox_t = bbox_t + down
            bbox_b = bbox_b + down


    new_bbox = bbox_l, bbox_t, bbox_r, bbox_b

    return new_bbox


def center_vertically(bbox_a, bbox_b):

    bbox_a = expand_bbox_tuples(bbox_a)
    height_line_a = bbox_a[3] - bbox_a[1]

    bbox_b = expand_bbox_tuples(bbox_b)
    height_line_b = bbox_b[3] - bbox_b[1]

    midpoint_in_b = bbox_b[1] + int(height_line_b/2)
    half_height = int(height_line_a/2)

    top = midpoint_in_b - half_height
    bottom = midpoint_in_b + half_height

    new_bbox = bbox_a[0], top, bbox_a[2], bottom

    return new_bbox


def center_horizontally(bbox_a, bbox_b):

    bbox_a = expand_bbox_tuples(bbox_a)
    width_line_a = bbox_a[2] - bbox_a[0]
    midpoint_in_a = bbox_a[0] + int(width_line_a/2)

    bbox_b = expand_bbox_tuples(bbox_b)
    width_line_b = bbox_b[2] - bbox_b[0]

    midpoint_in_b = bbox_b[0] + int(width_line_b/2)

    left = midpoint_in_b-(width_line_a/2)
    right = left + width_line_a

    new_bbox = left, bbox_a[1], right, bbox_a[3]

    return new_bbox

def centre_on_target(subject, target, centre_on_horizontal=True, centre_on_vertical=True, target_is_point=False) -> tuple[float, float, float, float]:

    print(f"Subject arriving to centre_on_target: {subject}")
    def do_centre(a_first, a_second, b_first, b_second) -> tuple[float,float]:

        width_line_a = a_second - a_first
        width_line_b = b_second - b_first
        print(f"width line a: {width_line_a} // width_line_b: {width_line_b}")

        midpoint_in_b = b_first + int(width_line_b/2)

        first = midpoint_in_b-(width_line_a/2)
        second = first + width_line_a

        return first, second

    subject = expand_bbox_tuples(subject, default_to_point=False)
    target = expand_bbox_tuples(target, default_to_point=target_is_point)
    if target_is_point:
        target = (target[2]-2, target[3]-2, target[2], target[3])

    subj_left, subj_top, subj_right, subj_bottom = subject
    targ_left, targ_top, targ_right, targ_bottom = target

    if centre_on_vertical:
        updated = do_centre(subj_top, subj_bottom, targ_top, targ_bottom)
        subject = int(subject[0]), int(updated[0]), int(subject[2]), int(updated[1])

    if centre_on_horizontal:
        updated = do_centre(subj_left, subj_right, targ_left, targ_right)
        subject = int(updated[0]), int(subject[1]), int(updated[1]), int(subject[3])

    return subject


def run_test():

    with Image.new("RGBA", (1920, 1080), "white") as im:
        draw = ImageDraw.Draw(im, "RGBA")
        """#draw.rectangle(xy=subject, fill="orange", outline="black")

        #base_font = ImageFont.FreeTypeFont("C:\\WINDOWS\\FONTS\\CORBELLI.TTF", size=40)

        #target = expand_bbox_tuples(target)
        #draw.rectangle(xy=target, fill="blue", outline="black")

        #new_bbox = centre_on_target(subject, target, target_is_point=True)
        #draw.rectangle(xy=new_bbox, outline="red", width=2)

        #draw.line(xy=[(900,0), (900,900)], fill="black", width=3)

        #aligned = align_to((88,88,250,120), destination=(300,300), direction="top")
        #draw.rectangle(aligned, fill="#06A563", outline="black", width=3)
        #aligned = align_to((88,88,250,120), destination=(900,300), direction="bottom")
        #draw.rectangle(aligned, fill="#46A506", outline="black", width=3)
    """

        base_bbox = (670,170)

        for _ in range(6): # lil bit of recursion
            colour=randint(50,225)
            transparency=30
            base_bbox = centre_on_target(base_bbox, target=(700,500), target_is_point=True)
            print(f"base_bbox: {base_bbox}")
            draw.rectangle(xy=base_bbox, fill=(colour, colour, colour, transparency), outline="black")
            base_bbox = scale_rect(base_bbox, scale_x=.8)
        im.show()

if __name__ == "__main__":
    run_test()
