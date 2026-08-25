import sys
import time
import tkinter
import os.path

_root_window = None
_canvas = None
_canvas_xs = None
_canvas_ys = None
_canvas_x = None
_canvas_y = None


def formatColor(r, g, b):
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def colorToVector(color):
    return list(map(lambda x: int(x, 16) / 256.0, [color[1:3], color[3:5], color[5:7]]))


def sleep(secs):
    global _root_window
    if _root_window is None:
        time.sleep(secs)
    else:
        _root_window.update_idletasks()
        _root_window.after(int(1000 * secs), _root_window.quit)
        _root_window.mainloop()


def _setup_window_bindings():
    _root_window.bind("<KeyPress>", _keypress)
    _root_window.bind("<KeyRelease>", _keyrelease)
    _root_window.bind("<FocusIn>", _clear_keys)
    _root_window.bind("<FocusOut>", _clear_keys)
    _root_window.bind("<Button-1>", _leftclick)
    _root_window.bind("<Button-2>", _rightclick)
    _root_window.bind("<Button-3>", _rightclick)
    _root_window.bind("<Control-Button-1>", _ctrl_leftclick)
    _clear_keys()


def begin_graphics(width=640, height=480, color=formatColor(0, 0, 0), title=None):
    global \
        _root_window, \
        _canvas, \
        _canvas_x, \
        _canvas_y, \
        _canvas_xs, \
        _canvas_ys, \
        _bg_color

    if _root_window is not None:
        _root_window.destroy()

    _canvas_xs, _canvas_ys = width - 1, height - 1
    _canvas_x, _canvas_y = 0, _canvas_ys
    _bg_color = color

    _root_window = tkinter.Tk()
    _root_window.protocol("WM_DELETE_WINDOW", _destroy_window)
    _root_window.title(title or "Graphics Window")
    _root_window.resizable(0, 0)

    try:
        _canvas = tkinter.Canvas(_root_window, width=width, height=height)
        _canvas.pack()
        draw_background()
        _canvas.update()
    except:
        _root_window = None
        raise

    _setup_window_bindings()


def begin_graphics_scrollable(
    viewport_width,
    viewport_height,
    content_width,
    content_height,
    color=formatColor(0, 0, 0),
    title=None,
):
    """
    Create a graphics window with scrollbars when content is larger than viewport.
    Drawing uses content coordinates (0,0) to (content_width-1, content_height-1).
    """
    global \
        _root_window, \
        _canvas, \
        _canvas_x, \
        _canvas_y, \
        _canvas_xs, \
        _canvas_ys, \
        _bg_color

    if _root_window is not None:
        _root_window.destroy()

    _canvas_xs = content_width - 1
    _canvas_ys = content_height - 1
    _canvas_x, _canvas_y = 0, _canvas_ys
    _bg_color = color

    _root_window = tkinter.Tk()
    _root_window.protocol("WM_DELETE_WINDOW", _destroy_window)
    _root_window.title(title or "Graphics Window")
    _root_window.resizable(1, 1)

    try:
        frame = tkinter.Frame(_root_window)
        frame.pack(fill=tkinter.BOTH, expand=True)

        vscroll = tkinter.Scrollbar(frame)
        hscroll = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)

        _canvas = tkinter.Canvas(
            frame,
            width=viewport_width,
            height=viewport_height,
            scrollregion=(0, 0, content_width, content_height),
            yscrollcommand=vscroll.set,
            xscrollcommand=hscroll.set,
        )
        vscroll.config(command=_canvas.yview)
        hscroll.config(command=_canvas.xview)

        vscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        hscroll.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        _canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        draw_background()
        _canvas.update()
    except Exception:
        _root_window = None
        raise

    _setup_window_bindings()


_leftclick_loc = None
_rightclick_loc = None
_ctrl_leftclick_loc = None


def _leftclick(event):
    global _leftclick_loc
    _leftclick_loc = (event.x, event.y)


def _rightclick(event):
    global _rightclick_loc
    _rightclick_loc = (event.x, event.y)


def _ctrl_leftclick(event):
    global _ctrl_leftclick_loc
    _ctrl_leftclick_loc = (event.x, event.y)


def wait_for_click():
    while True:
        global _leftclick_loc
        global _rightclick_loc
        global _ctrl_leftclick_loc
        if _leftclick_loc is not None:
            val = _leftclick_loc
            _leftclick_loc = None
            return val, "left"
        if _rightclick_loc is not None:
            val = _rightclick_loc
            _rightclick_loc = None
            return val, "right"
        if _ctrl_leftclick_loc is not None:
            val = _ctrl_leftclick_loc
            _ctrl_leftclick_loc = None
            return val, "ctrl_left"
        sleep(0.05)


def draw_background():
    corners = [(0, 0), (0, _canvas_ys), (_canvas_xs, _canvas_ys), (_canvas_xs, 0)]
    polygon(corners, _bg_color, fillColor=_bg_color, filled=True, smoothed=False)


def _destroy_window(event=None):
    sys.exit(0)


def end_graphics():
    global _root_window, _canvas, _mouse_enabled
    try:
        try:
            sleep(1)
            if _root_window is not None:
                _root_window.destroy()
        except SystemExit as e:
            print("Ending graphics raised an exception:", e)
    finally:
        _root_window = None
        _canvas = None
        _mouse_enabled = 0
        _clear_keys()


def clear_screen(background=None):
    global _canvas_x, _canvas_y
    _canvas.delete("all")
    draw_background()
    _canvas_x, _canvas_y = 0, _canvas_ys


def polygon(
    coords, outlineColor, fillColor=None, filled=1, smoothed=1, behind=0, width=1
):
    c = []
    for coord in coords:
        c.append(coord[0])
        c.append(coord[1])
    if fillColor is None:
        fillColor = outlineColor
    if filled == 0:
        fillColor = ""
    poly = _canvas.create_polygon(
        c, outline=outlineColor, fill=fillColor, smooth=smoothed, width=width
    )
    if behind > 0:
        _canvas.tag_lower(poly, behind)
    return poly


def square(pos, r, color, filled=1, behind=0):
    x, y = pos
    coords = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color, filled, 0, behind=behind)


def circle(
    pos, r, outlineColor, fillColor=None, endpoints=None, style="pieslice", width=2
):
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    return _canvas.create_arc(
        x0,
        y0,
        x1,
        y1,
        outline=outlineColor,
        fill=fillColor or outlineColor,
        extent=e[1] - e[0],
        start=e[0],
        style=style,
        width=width,
    )


def refresh():
    _canvas.update_idletasks()


def moveCircle(id, pos, r, endpoints=None):
    global _canvas_x, _canvas_y

    x, y = pos
    x0 = x - r - 1
    y0 = y - r - 1
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    if os.path.isfile("flag"):
        edit(id, ("extent", e[1] - e[0]))
    else:
        edit(id, ("start", e[0]), ("extent", e[1] - e[0]))
    move_to(id, x0, y0)


def edit(id, *args):
    _canvas.itemconfigure(id, **dict(args))


def text(pos, color, contents, font="Helvetica", size=12, style="normal", anchor="nw"):
    global _canvas_x, _canvas_y
    x, y = pos
    font = (font, str(size), style)
    return _canvas.create_text(
        x, y, fill=color, text=contents, font=font, anchor=anchor
    )


def changeText(id, newText, font=None, size=12, style="normal"):
    _canvas.itemconfigure(id, text=newText)
    if font is not None:
        _canvas.itemconfigure(id, font=(font, "-%d" % size, style))


def changeColor(id, newColor):
    _canvas.itemconfigure(id, fill=newColor)


def line(here, there, color=formatColor(0, 0, 0), width=2):
    x0, y0 = here[0], here[1]
    x1, y1 = there[0], there[1]
    return _canvas.create_line(x0, y0, x1, y1, fill=color, width=width)


_keysdown = {}
_keyswaiting = {}
_got_release = None


def _keypress(event):
    global _got_release

    _keysdown[event.keysym] = 1
    _keyswaiting[event.keysym] = 1
    _got_release = None


def _keyrelease(event):
    global _got_release

    try:
        del _keysdown[event.keysym]
    except Exception:
        pass
    _got_release = 1


def remap_arrows(event):
    if event.char in ["a", "s", "d", "w"]:
        return
    if event.keycode in [37, 101]:
        event.char = "a"
    if event.keycode in [38, 99]:
        event.char = "w"
    if event.keycode in [39, 102]:
        event.char = "d"
    if event.keycode in [40, 104]:
        event.char = "s"


def _clear_keys(event=None):
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed(
    d_o_e=lambda arg: _root_window.dooneevent(arg), d_w=tkinter._tkinter.DONT_WAIT
):
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return _keysdown.keys()


def keys_waiting():
    global _keyswaiting
    keys = _keyswaiting.keys()
    _keyswaiting = {}
    return keys


def wait_for_keys():
    keys = []
    while not keys:
        keys = keys_pressed()
        sleep(0.05)
    return keys


def remove_from_screen(
    x, d_o_e=lambda arg: _root_window.dooneevent(arg), d_w=tkinter._tkinter.DONT_WAIT
):
    _canvas.delete(x)
    d_o_e(d_w)


def move_to(
    object,
    x,
    y=None,
    d_o_e=lambda arg: _root_window.dooneevent(arg),
    d_w=tkinter._tkinter.DONT_WAIT,
):
    if y is None:
        try:
            x, y = x
        except Exception:
            raise "incomprehensible coordinates"

    horiz = True
    newCoords = []
    current_x, current_y = _canvas.coords(object)[0:2]
    for coord in _canvas.coords(object):
        if horiz:
            inc = x - current_x
        else:
            inc = y - current_y
        horiz = not horiz

        newCoords.append(coord + inc)

    _canvas.coords(object, *newCoords)
    d_o_e(d_w)
