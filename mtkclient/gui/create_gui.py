import re
import sys
from PySide6.scripts.pyside_tool import qt_tool_wrapper
if __name__ == '__main__':
    sys.argv[0] = "main_gui.ui -o main_gui.py"
    sys.exit(qt_tool_wrapper("uic", ['-g', 'python', 'main_gui.ui', '-o', 'main_gui.py'], True))
