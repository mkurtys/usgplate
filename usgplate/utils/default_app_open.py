import os
import subprocess
import sys


def open_file_with_default_app(file_path: str):
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":
        subprocess.run(['open', file_path], check=True)
    else:
        subprocess.run(['xdg-open', file_path], check=True)