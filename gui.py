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

from manimlib.scene.scene import Scene
from manimlib.config import get_module
from manimlib.extract_scene import get_scene_classes_from_module

# sys.path = [".\\manim"]

print(os.getcwd())
os.chdir("C:\manim")
print(os.getcwd())


def find_scenes(file_path,raw=False):
    _file = get_module(file_path)
    # print(_file)

    scenes_classes = get_scene_classes_from_module(_file)

    # This searches for the word after the '.'
    scenes = [re.search(r'\.(\w*)', str(scene)).group()[1:]
              for scene in scenes_classes]
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
    print(f"\n\nRender for {scene} started at: {datetime.now()}\n\n")
    File = values["path"]
    quality = get_quality(values)
    preview = values["preview_bool"]
    lpb = get_progress_bars(values)

    start_at = values["n1"]
    end_at = values["n2"]

    print
    if start_at and not end_at:
        n = f"-n {start_at}"
    elif not start_at and end_at:
        n = f"-n 0,{end_at}"
    elif not (start_at and end_at):
        n = ""

    if preview:
        command = f"py -m manim {File} {scene} -p{quality} {n} {lpb}"
    elif not preview and quality != "":
        command = f"py -m manim {File} {scene} -{quality} {n} {lpb}"
    else:
        command = f"py -m manim {File} {scene} {n} {lpb}"

    args = shlex.split(command)
    print(args)
    # output = threading.Thread(target=lambda:subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE),daemon=True)
    output = subprocess.Popen(args,shell=True).wait()
    # output.start()

    # while True:
    #     output.join(timeout=0.1)
    #     if not output.is_alive():
    #         print("Done.\n")
    #         break



def main():
    layout = [
        [sg.T("Choose file: "), sg.Input("",key="path",size=(100,1)),
                                sg.FileBrowse(target="path",key="get_file")],
        [sg.T("Scenes found:"),sg.Listbox(["No scenes found"],
                                        size=(40,8),
                                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                                        enable_events=True,
                                        key="scene_select"), sg.B("Get Scenes",button_color=("black","yellow"))],
        [sg.T(" "*20),sg.B("Select All",key="select_all"),sg.B("Clear selection",key="clear")],
        [sg.T("Scene(s) selected :"),sg.T("No scene selected",size = (100,5),key="scene")],
        [sg.T("Quality: "),
            sg.Radio("l",key="l",group_id="quality", default=True),
            sg.Radio("m",key="m",group_id="quality"),
            sg.Radio("p",key="p",group_id="quality"),
            sg.Radio("s",key="s",group_id="quality"),
            sg.Radio("g",key="g",group_id="quality"),
            sg.Radio("i",key="i",group_id="quality"),
            sg.Radio("t",key="t",group_id="quality"),sg.Checkbox("Preview?",default=True,key="preview_bool"),
                                                    sg.Checkbox("Leave progress bars?",default=True,key="lpb_bool")
            ],
        [sg.T("Specify animation "),
         sg.CB("start number?",key="n1_bool"),
         sg.CB("end number?",key="n2_bool")],
        [sg.T("Start at animation number"),sg.Spin(list(range(10000)),0,True,key="n1"),
         sg.T("End at animation number"),sg.Spin(list(range(10000)),0,True,key="n2"),
         sg.B("Refresh",button_color=("black","yellow"))],
        [sg.T()],
        [sg.T("Status: "),sg.T("IDLE",key="status",size=(30,1))],
        [sg.B("RENDER",button_color=("black","green"))]
    ]

    manim_gui = sg.Window("Manim Renderer v0.1",layout,resizable=True)
    while True:
        # try:
        event,values = manim_gui.read()
        if event != sg.TIMEOUT_KEY:
            # print(f"Event: {event}")
            # print(f"Values {values}")

            pass

        if event in (None,'Exit'):
            break

        if event == "Get Scenes":
            File = values["path"]

            if not has_spaces(File):
                scenes = find_scenes(File)
                print(scenes)
                manim_gui["scene_select"].Update(values=scenes)
            else:
                sg.PopupError("Error: Spaces in file path",title="SpacesError")
        if event == "scene_select":
            manim_gui["scene"].Update(", ".join(values["scene_select"]))

        if event=="Refresh":
            manim_gui["n1"].Update(value=0,disabled=not values["n1_bool"])
            manim_gui["n2"].Update(value=0,disabled=not values["n2_bool"])

            manim_gui.read(timeout=0)

        # Render Code
        # -----------

        if event == "RENDER":
            # scene = " ".join(values["scene_select"])
            # print(scene)

            # print(quality)


            # print(args)
            current_time = time.clock()
            manim_gui["status"].Update("Rendering")
            manim_gui.read(timeout=0)

            for scene in values["scene_select"]:
                render(scene,**values)
            # print(output)
            sg.SystemTray.notify("Render complete","Check console for more details")
            manim_gui["status"].Update("Rendered")
            print(f"Render complete in {time.clock()}")

        # except Exception as e:
        #     sg.PopupError(e,title="Error")

        if event == "select_all":
            manim_gui["scene_select"].Update(set_to_index=list(range(len(scenes))))
            manim_gui.read()
            manim_gui["scene"].Update(", ".join(values["scene_select"]))

        if event == "clear":
            manim_gui["scene_select"].Update(set_to_index=False)
            manim_gui.read()
            manim_gui["scene"].Update("")


if __name__ == "__main__":
    main()
