from logging import fatal


class JCONSTANTS:
    class EDITOR:
        WIDTH: int = 1280
        HEIGHT: int = 900
        TITLE: str = "J-Editor"
        SPLASH: bool = False
        SPLASH_IMAGE: str = r"resources/splash.png"
        SPLASH_TIME: int = 1300
        START_CENTER_ON_MOUSE: bool = False

    class MODEL:
        DEFAULT_SAVE_PATH: str = r"models/"
        EXTENSION: str = "jigls"

    class GRSCENE:
        BACKGROUND_COLOR: str = "#393939"
        WIDTH: int = 64000
        HEIGHT: int = 64000
        GRID_SIZE: int = 20
        LINE_SPACING: int = 5
        MAJOR_LINE_COLOR: str = "292929"
        MINOR_LINE_COLOR: str = "2f2f2f"
        MAJOR_LINE_PEN_WIDTH: int = 2
        MINOR_LINE_PEN_WIDTH: int = 1
        GRID_LINES: bool = False

    class GRVIEW:
        # * Qt.ScrollBarPolicy 1 OFF 2 ON
        VERT_SCROLLBAR: int = 1
        HORZ_SCROLLBAR: int = 1
        ZOOM_IN_FACTOR: float = 1.25
        ZOOM_CLAMPED: bool = True
        ZOOM: int = 10
        ZOOM_STEP: int = 1
        ZOOM_RANGE_MIN: int = 0
        ZOOM_RANGE_MAX: int = 10
        MODE_DEFAULT: int = 0
        MODE_PAN_VIEW: int = 1
        MODE_SELECTION: int = 2
        MODE_EDGE_DRAG: int = 3
        MODE_EDGE_REROUTE: int = 4

    class GRNODE:
        # https://www.w3schools.com/colors/colors_picker.asp
        TITLE_COLOR: str = "#ffffff"
        TITLE_FONT: str = "Ubuntu"
        TITLE_FONT_SIZE: int = 10
        TITLE_HEIGHT: float = 24.0
        TITLE_PADDING: int = 4
        NODE_WIDHT: int = 240
        NODE_HEIGHT: int = 180
        NODE_PADDING: int = 9
        COLOR_DEFAULT: str = "#000000"
        COLOR_SELECTED: str = "#00ff00"
        COLOR_TITLE: str = "#99cc00"
        COLOR_BACKGROUND: str = "#E3232323"

    class SOCKET:
        TYPE_INPUT: int = 1
        TYPE_OUTPUT: int = 2

    class GRSOCKET:
        RADIUS: float = 8.0
        WIDTH_OUTLINE: float = 2.0
        COLOR_OUTLINE: str = "#FF000000"
        COLOR_BACKGROUND: str = "#FFFF7700"
        COLOR_HOVER: str = "#00ff80"
        POS_LEFT_TOP: int = 1
        POS_LEFT_BOTTOM: int = 2
        POS_RIGHT_TOP: int = 3
        POS_RIGHT_BOTTOM: int = 4
        SPACING: int = 25

    class GREDGE:
        COLOR_DEFAULT: str = "#8BC34A"
        COLOR_SELECTED: str = "#FF0000"
        COLOR_DRAG: str = "#F5DD29"
        WIDTH: int = 3
        PATH_DIRECT: int = 1
        PATH_SQUARE: int = 2
        PATH_BEZIER: int = 3
        PATH_DRAG: int = 4

    class CLIPBOARD:
        MODE_COPY: int = 1
        MODE_CUT: int = 2
