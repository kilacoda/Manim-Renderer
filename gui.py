## TODO: Add a searchbar for quicker navigation.


import PySimpleGUI as sg
import inspect as i
import subprocess
import shlex
import re
import sys
import os
from datetime import datetime
import multiprocessing
import threading
import time
import math
import base64
from rich import print
import rich.traceback

rich.traceback.install()

from manim.utils.module_ops import get_module,get_scene_classes_from_module

with open("Thumbnail_mini.png", "rb") as logo_file:
    MANIM_LOGO_BASE64 = base64.b64encode(logo_file.read())
# sys.path = [".\\manim"]
# sg.theme_previewer(5)
sg.theme("DarkBlue")


def find_scenes(file_path):
    _file = get_module(file_path)

    scenes_classes = get_scene_classes_from_module(_file)

    # This searches for the word after the '.'
    scenes = [re.search(r"\.(\w*)", str(scene)).group()[1:] for scene in scenes_classes]
    return scenes


def get_quality(values):
    for key in ["l", "m", "p", "s", "g", "i", "t"]:
        # print(key)
        if values[key] == True and key != "p":
            return key
        elif values[key] == True and key == "p":
            return ""


def get_progress_bars(values):
    if values["lpb_bool"]:
        return "--leave_progress_bars"
    else:
        return ""


# sg.Prog(,)


def has_spaces(path):
    if " " in path:
        return True
    else:
        return False


def render(scene, **values):
    """
    A function which renders each scene in a separate thread
    """
    print("\n" + "[green]+[/green]-[green]+[/green]" * 50)
    print(
        f"\nRender for [bold yellow]{scene}[/bold yellow] started at: [blue]{datetime.now()}[/blue]\n\n"
    )
    File = values["path"]
    quality = get_quality(values)
    preview = values["preview_bool"]
    lpb = get_progress_bars(values)

    start_at = values["n1"]
    end_at = values["n2"]

    if start_at and not end_at:
        n = f"-n {start_at}"
    elif not start_at and end_at:
        n = f"-n 0,{end_at}"
    elif not (start_at and end_at):
        n = ""

    if preview:
        command = f"py -m manim {File} {scene} -p{quality} {n} {lpb} --sound"
    elif not preview and quality != "":
        command = f"py -m manim {File} {scene} -{quality} {n} {lpb} --sound"
    else:
        command = f"py -m manim {File} {scene} {n} {lpb} --sound"

    args = shlex.split(command)
    print(args)
    # output = threading.Thread(target=lambda:subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE),daemon=True)
    output = subprocess.Popen(args, shell=True).wait()
    # output.start()

    # while True:
    #     output.join(timeout=0.1)
    #     if not output.is_alive():
    #         print("Done.\n")
    #         break


def main():
    menu_def = [
        ["&Open", ["&File", "&Media dir", ["&Tex", "&Videos"]],],
        ["O&ptions", ["&Change manim", "&Add folder to sys.path", "&Show path"],],
    ]

    layout = [
        [sg.Menu(menu_def)],
        [
            sg.T("Choose file: "),
            sg.Input("", key="path", size=(100, 1)),
            sg.FileBrowse(target="path", key="get_file"),
        ],
        [
            sg.T("Scenes found:"),
            sg.Listbox(
                ["No scenes found"],
                size=(70, 12),
                select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                enable_events=True,
                key="scene_select",
            ),
            sg.B("Get Scenes", button_color=("black", "yellow")),
        ],
        [
            sg.T(" " * 20),
            sg.B("Select All", key="select_all"),
            sg.B("Clear selection", key="clear"),
        ],
        [
            sg.T("Scene(s) selected :"),
            sg.T("No scene selected", size=(100, 5), key="scene"),
        ],
        [
            sg.T("Quality: "),
            sg.Radio("l", key="l", group_id="quality", default=True),
            sg.Radio("m", key="m", group_id="quality"),
            sg.Radio("p", key="p", group_id="quality"),
            sg.Radio("s", key="s", group_id="quality"),
            sg.Radio("g", key="g", group_id="quality"),
            sg.Radio("i", key="i", group_id="quality"),
            sg.Radio("t", key="t", group_id="quality"),
            sg.Checkbox("Preview?", default=True, key="preview_bool"),
            sg.Checkbox("Leave progress bars?", default=True, key="lpb_bool"),
        ],
        [
            sg.T("Specify animation "),
            sg.CB("start number?", key="n1_bool"),
            sg.CB("end number?", key="n2_bool"),
        ],
        [
            sg.T("Start at animation number"),
            sg.Spin(list(range(10000)), 0, True, key="n1"),
            sg.T("End at animation number"),
            sg.Spin(list(range(10000)), 0, True, key="n2"),
            sg.B("Refresh", button_color=("black", "yellow")),
        ],
        [sg.T()],
        [sg.T("Status: "), sg.T("IDLE", key="status", size=(30, 1))],
        [sg.B("RENDER", button_color=("black", "green"))],
    ]
    # sg.theme_previewer()
    manim_gui = sg.Window(
        "Manim Renderer v0.1", layout, resizable=True, icon=MANIM_LOGO_BASE64
    )
    print("Opened.")
    while True:
        try:
            event, values = manim_gui.read()
            if event != sg.TIMEOUT_KEY:
                # print(f"Event: {event}")
                # print(f"Values {values}")
                pass

            if event in (None, "Exit"):
                break

            if event == "Get Scenes":
                File = values["path"]

                if not has_spaces(File):
                    scenes = find_scenes(File)
                    print(scenes)
                    manim_gui["scene_select"].Update(values=scenes)
                else:
                    sg.PopupError("Error: Spaces in file path", title="SpacesError")

            if event == "scene_select":
                manim_gui["scene"].Update(", ".join(values["scene_select"]))

            if event == "Refresh":
                manim_gui["n1"].Update(value=0, disabled=not values["n1_bool"])
                manim_gui["n2"].Update(value=0, disabled=not values["n2_bool"])

                manim_gui.read(timeout=0)

            # Render Code
            # -----------

            if event == "RENDER":
                # scene = " ".join(values["scene_select"])
                # print(scene)

                # print(quality)

                # print(args)
                start_time = time.time()
                manim_gui["status"].Update("Rendering")
                manim_gui.read(timeout=0)

                ## This is where the multiple rendering thing takes place if applicable
                for scene in values["scene_select"]:
                    values.pop(0)
                    render(scene, **values)
                # print(output)
                sg.SystemTray.notify(
                    "Render complete", "Check console for more details"
                )
                manim_gui["status"].Update("Rendered")

                end_time = time.time()

                render_time = math.trunc(end_time - start_time)
                print(f"Render complete in {render_time}s ")

                print("\n" + "[green]+[/green]-[green]+[/green]" * 50)
                print("\n\n")

            if event == "select_all":
                manim_gui["scene_select"].Update(set_to_index=list(range(len(scenes))))
                manim_gui.read()
                manim_gui["scene"].Update(", ".join(values["scene_select"]))

            if event == "clear":
                manim_gui["scene_select"].Update(set_to_index=False)
                manim_gui.read()
                manim_gui["scene"].Update("")

            ## Menu options
            if event == "File":
                file_path = sg.popup_get_file(
                    "Select file with manim scenes", no_window=True
                )

                manim_gui["path"].update(file_path)

                manim_gui.refresh()

            if event == "Tex":
                os.system("explorer .\\media\\Tex")

            if event == "videos":
                os.system("explorer .\\media\\videos")

            if event == "Change manim":
                folder_getter = sg.popup_get_folder(
                    "Select manim location", no_window=True
                )
                print("[bold blue]Old[/bold blue] manim path:", os.getcwd())
                os.chdir(folder_getter)
                print("[bold red]New[/bold red] manim path:", os.getcwd())
                
                sys.path.append(folder_getter)
                sys.path.pop(0)

            if event == "Add folder to sys.path":
                folder_getter = sg.popup_get_folder("Add folder", no_window=True)

                sys.path.append(folder_getter)
                manim_gui.refresh()
                
            if event == "Show path":
                sg.popup(*sys.path,title="sys.path")

        except Exception as e:
            sg.PopupError(e, title="Error")

        finally:
            manim_gui.refresh()

    manim_gui.close()


if __name__ == "__main__":
    main()

