import re
import sys
from pathlib import Path
import PySide6 as ref_mod
import os
import subprocess
import sysconfig


def qt_tools_wrapper(qt_tool, args, libexec=False):
	pyside_dir = Path(ref_mod.__file__).resolve().parent
	if libexec and sys.platform != "win32":
		exe = pyside_dir / 'Qt' / 'libexec' / qt_tool
	else:
		exe = pyside_dir / qt_tool
	cmd = [os.fspath(exe)] + args
	cmd = ' '.join(cmd)
	proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	out, err = proc.communicate()
	if err:
		msg = err.decode("utf-8")
		print(f"Error: {msg}\nwhile executing '{cmd}'")
	sys.exit(proc.returncode)
    
if __name__ == '__main__':
	sys.exit(qt_tools_wrapper("lrelease", ['*.ts']))
