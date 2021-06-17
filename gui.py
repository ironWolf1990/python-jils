import argparse
import cProfile
import pstats
import sys

from PyQt5.QtWidgets import QApplication

from jigls.jeditor.editorwindow import JEditorWindow


def Profile(toProfile):
    def profileWrapper():
        profiler = cProfile.Profile()
        profiler.enable()

        toProfile()

        print(f"\n    {40*'='}\n         PROFILER\n    {40*'='}\n")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("ncalls")
        stats.print_stats()

    return profileWrapper


def Run():
    app = QApplication(sys.argv)

    wnd = JEditorWindow()
    wnd.show()

    try:
        app.exec_()
    except Exception as e:
        print(e)


def main(args=argparse.Namespace):

    if args.profile:
        Profile(Run)()
    else:
        Run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="command line arguments")

    parser.add_argument("--profile", action="store_false")

    main(parser.parse_args())
