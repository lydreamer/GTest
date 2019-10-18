#coding=utf-8

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import math
import json
import os
import re
import sys
import shutil

os.chdir(os.path.dirname(sys.argv[0]))
road_layer_name = "road"
obstacle_layer_name = "obstacle"
copy_file_path = "../Json/"

def read_layer(root, arr, layer_name):
    dstLayer = None
    for layer in root.findall("layer"):
        if layer.get("name") == layer_name:
            dstLayer = layer
            break
    
    if dstLayer != None:
        data = dstLayer.find("data")
        text = data.text.strip("\n")
        strList = str.split(text, "\n")
        arrLen = len(strList)
        for i in list(range(0, arrLen)):
            dictarr = str.split(strList[i].strip(","), ",")
            for j in list(range(0, len(dictarr))):
                id = int(dictarr[j])
                if id != 0:
                    arr[arrLen-1-i][j] = id
    else:
        print("[Warn]layer %s not exist!" % layer_name)

def read_entrances(root, entrances_arr, entrances_map, tile_width, tile_height, map_height):
    dstObjGroup = None
    for objgroup in root.findall("objectgroup"):
        if objgroup.get("name") == "entrance":
            dstObjGroup = objgroup
            break
    
    if dstObjGroup != None:
        objects = dstObjGroup.findall("object")
        for i in range(len(objects)): 
            info = {}
            entrances_arr.append(info)
            objectAttr = objects[i].attrib
            info["id"] = int(float(objectAttr["name"]))
            info["x"] = int(float(objectAttr["x"])/tile_width)
            info["y"] = map_height - 1 - int(float(objectAttr["y"])/tile_height)
            entrances_map[info["id"]] = info
    else:
        tkinter.messagebox.showinfo("错误")

def read_exit(root, tile_width, tile_height, map_height):
    dstObjGroup = None
    for objgroup in root.findall("objectgroup"):
        if objgroup.get("name") == "exit":
            dstObjGroup = objgroup
            break
    
    if dstObjGroup != None:
        objects = dstObjGroup.findall("object")
        if len(objects) != 1:
              print("错误exit_point不等于一个")
              os.system("exit")
        else:
            objectAttr = objects[0].attrib
            info = {}
            info["x"] = int(float(objectAttr["x"])/tile_width)
            info["y"] = map_height -1- int(float(objectAttr["y"])/tile_height)
            return info
    else:
        tkinter.messagebox.showinfo("错误")

def readTmx(tmx_file):
    try:
        tree = ET.parse(tmx_file)
    except FileNotFoundError:
        tkinter.messagebox.showinfo("错误", tmx_file + "文件没找到")
        return

    mapName = tmx_file.split('.', 1 )[0]; 
    root = tree.getroot()
    attr = root.attrib

    map_width = int(attr["width"])
    map_height = int(attr["height"])
    tile_width = int(attr["tilewidth"])
    tile_height = int(attr["tileheight"])

    road_map = [[0] * map_width for i in range(0, map_height) ]
    obstacle_map = [[0] * map_width for i in range(0, map_height) ]
    entrances_arr = []
    entrances_map = {}

    #加载道路数据
    read_layer(root, road_map, road_layer_name)
    read_layer(root, obstacle_map, obstacle_layer_name)
    read_entrances(root, entrances_arr, entrances_map,  tile_width, tile_height, map_height)
    exit_point = read_exit(root,tile_width, tile_height, map_height)

    map_info = {
        "name": mapName,
        "stage": int(re.findall('(\d+)',tmx_file)[0]),
        "width": map_width,
        "height": map_height,
        "tileWidth": tile_width,
        "tileHeight": tile_height,
        "roadMap": road_map,
        "obstacleMap": obstacle_map,
        "entrances": entrances_arr,
        "entrances_map": entrances_map,
        "exit_point": exit_point,
    }

    jsonarray = json.dumps(map_info)
    json_name = tmx_file[:-3] + "json"

    with open(json_name, "w+") as f:
        f.write(jsonarray)

    shutil.copyfile(json_name, copy_file_path + json_name)  
    os.remove(json_name)
    

if __name__ == "__main__":
    path_list = os.listdir('./')
    for filename in path_list:
        if os.path.splitext(filename)[1] == '.tmx':
            print('processing map: %s ...' % filename)
            readTmx(filename)
 
    
    