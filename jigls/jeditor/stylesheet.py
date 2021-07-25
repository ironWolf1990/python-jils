STYLE_QMENUBAR = """
QMenuBar {
    background-color: rgb(49,49,49);
    color: rgb(255,255,255);
    border: 1px solid #000;
}

QMenuBar::item {
    background-color: rgb(49,49,49);
    color: rgb(255,255,255);
}

QMenu {
    background-color: rgb(49,49,49);
    color: rgb(255,255,255);
    border: 1px solid #000;           
}

QMenu::item {
    padding: 5px 18px 2px;
    background-color: transparent;
}
QMenu::item:selected {
    color: rgba(98, 68, 10, 255);
    background-color: rgba(219, 158, 0, 255);
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 50);
    margin: 4px 8px;
}
"""

STYLE_SPLASH = """
QFrame {
    background-color: #0A052C;
}
"""

STYLE_TREE = """
QTreeView {
    color: #000000;
    background-color: #B6B6B6;
    alternate-background-color: #FFFFFF;
    selection-color: #FF0000;
    selection-background-color: #7FB3E6;
}
"""

STYLE_NODECONTEXTTABSEARCH = """
QLineEdit {
    border: 2px solid rgba(170, 140, 0, 255);
    border-radius: 0px;
    padding: 2px;
    margin: 4px;
    color: rgba(255, 255, 255, 150);
    background: rgba(20, 20, 20, 255);
    selection-background-color: rgba(219, 158, 0, 255);
}
"""

STYLE_NODECONTEXTMENU = """
QMenu {
    color: rgba(255, 255, 255, 200);
    background-color: rgba(47, 47, 47, 255);
    border: 1px solid rgba(0, 0, 0, 30);
}
"""