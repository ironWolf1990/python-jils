from argparse import Namespace, ArgumentParser
from jigls.package.node import Action, DisableNode, EnableNode, WebElementNode
from jigls.profiler import Profile

import sys
from PyQt5.QtWidgets import QApplication
from jigls.jeditor.editorwindow import JEditorWindow


def Run():

    app = QApplication(sys.argv)
    wnd = JEditorWindow()

    wnd.editorWidget.RegisterNode("WebElement", WebElementNode)
    wnd.editorWidget.RegisterNode("Action", Action)
    wnd.editorWidget.RegisterNode("EnableNode", EnableNode)
    wnd.editorWidget.RegisterNode("DisableNode", DisableNode)

    try:
        wnd.show()
        app.exec_()
    except Exception as e:
        print(e)


def main(args=Namespace):

    if args.profile:
        Profile(sortBy="ncalls")(Run)
    else:
        Run()


if __name__ == "__main__":

    parser = ArgumentParser(description="command line arguments")

    parser.add_argument("--profile", action="store_true", default=True)

    main(parser.parse_args())
