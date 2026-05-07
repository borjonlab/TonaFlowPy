# Source - https://stackoverflow.com/a/72060275
# Posted by Rainer Niemann, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-07, License - CC BY-SA 4.0

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
