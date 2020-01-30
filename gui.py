import PySimpleGUI as sg
import inspect as i
import subprocess,shlex
import re
import sys,os

from manimlib.scene.scene import Scene
from manimlib.config import get_module
from manimlib.extract_scene import get_scene_classes_from_module

# sys.path = [".\\manim"]

print(os.getcwd())
# os.chdir(".\\manim")
# print(os.getcwd())

def find_scenes(file_path):
    _file = get_module(file_path)
    print(_file)

    scenes_classes = get_scene_classes_from_module(_file)
    
    ## This searches for the word after the '.'
    scenes = [re.search(r'\.(\w*)',str(scene)).group()[1:] 
              for scene in scenes_classes]
    return scenes


def get_quality(values):
    for key in ["l","m","p","s","g","i","t"]:
        print(key)
        if values[key] == True and key != "p":
            return key
        elif values[key] == True and key == "p":
            return ""

layout = [
    [sg.T("Choose file: "), sg.Input("",key="path"), 
                            sg.FileBrowse(target="path",key="get_file")],
    [sg.T("Scenes found:"),sg.Listbox(["No scenes found"],
                                    size=(40,8),
                                    select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                                    enable_events=True,
                                    key="scene_select"), sg.B("Get Scenes",button_color=("black","yellow"))],
    [sg.T("Scene(s) selected :"),sg.T("No scene selected",size = (50,3),key="scene")],
    [sg.T("Quality: "),
     sg.Radio("l",key="l",group_id="quality", default=True), 
     sg.Radio("m",key="m",group_id="quality"),
     sg.Radio("p",key="p",group_id="quality"),
     sg.Radio("s",key="s",group_id="quality"),
     sg.Radio("g",key="g",group_id="quality"),
     sg.Radio("i",key="i",group_id="quality"),
     sg.Radio("t",key="t",group_id="quality"),sg.Checkbox("Preview?",default=True,key="preview_bool")
     ],
    [sg.T()],
    [sg.T("Status: "),sg.T("IDLE",key="status",size=(30,1))],
    [sg.B("RENDER",button_color=("black","green"))]
]


manim_gui = sg.Window("Manim Renderer v0.1",layout,resizable=True)

def has_spaces(path):
    if " " in path:
        return True
    else:
        return False

while True:
    # try:
    event,values = manim_gui.read()
    if event != sg.TIMEOUT_KEY:
        print(f"Event: {event}")
        print(f"Values {values}")

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
        manim_gui["scene"].Update(values["scene_select"])

    if event == "RENDER":
        File = values["path"]
        scene = " ".join(values["scene_select"])
        # print(scene)
        quality = get_quality(values)
        preview = values["preview_bool"]
        print(quality)
        if preview:
            command = f"python -m manim {File} {scene} -p{quality} --leave_progress_bars"
        elif not preview and quality != "":
            command = f"python -m manim {File} {scene} -{quality} --leave_progress_bars"
        else:
            command = f"python -m manim {File} {scene} --leave_progress_bars"

        args = shlex.split(command)
        
        print(args)
        
        manim_gui["status"].Update("Rendering")
        manim_gui.read(timeout=0)
        output = subprocess.Popen(args, shell=True).wait()
        
        print(output)

        manim_gui["status"].Update("Rendered")

    # except Exception as e:
    #     sg.PopupError(e,title="Error")

