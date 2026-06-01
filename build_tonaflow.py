# update_spec.py
#
# Automatically injects all imgs/ assets into a PyInstaller .spec file
# while preserving folder structure.
#
# Usage:
#   python update_spec.py

from pathlib import Path
import pprint
import re
import subprocess



SPEC_FILE = "TonaFlow.spec"
IMGS_DIR = "./imgs"


def build_datas(imgs_dir="imgs"):
    imgs_path = Path(imgs_dir)

    if not imgs_path.exists():
        return []

    datas = []

    for file_path in imgs_path.rglob("*"):
        if file_path.is_file():

            src = str(file_path).replace("\\", "/")
            dest = str(file_path.parent).replace("\\", "/")

            datas.append((src, dest))

    # Adding a line to append the ssqueezepy_config.ini, because we need that :(
    datas.append(('venv/lib/python3.11/site-packages/ssqueezepy/configs.ini', 'ssqueezepy/'))
    return datas


def update_spec_file(spec_path, datas):

    spec_text = Path(spec_path).read_text(encoding="utf-8")

    datas_string = pprint.pformat(datas, width=120)

    replacement = f"datas={datas_string},"

    updated = re.sub(
        r"datas=\[(.*?)\],",
        replacement,
        spec_text,
        flags=re.DOTALL,
    )

    Path(spec_path).write_text(updated, encoding="utf-8")

    print(f"Updated {spec_path} with {len(datas)} assets.")


if __name__ == "__main__":

    datas = build_datas(IMGS_DIR)

    update_spec_file(SPEC_FILE, datas)
    subprocess.run(["pyinstaller","TonaFlow.spec"])