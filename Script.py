#-*- coding: utf-8 -*-
import os
import time
import threading
import subprocess
import urllib.request
import urllib.error
import json as json
import mimetypes
from gps3 import gps3


def signin():
    global refreshToken
    my_data = dict()
    my_data["email"] = "admin@miag5.uadec.mx"
    my_data["password"] = "proyectoMIAg5"
    my_data["returnSecureToken"] = True

    json_data = json.dumps(my_data).encode()
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + firebase_apikey, data=json_data, headers=headers)

    try:
        loader = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        message = json.loads(e.read().decode("utf-8"))
        print(message["error"]["message"])
    else:
        data = json.loads(loader.read().decode("utf-8"))
        refreshToken = data['refreshToken']
        print(data)


def refresh_accesstoken(token):
    global refreshToken
    global access_token
    my_data = dict()
    my_data["grant_type"] = "refresh_token"
    my_data["refresh_token"] = token

    json_data = json.dumps(my_data).encode()
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(
        "https://securetoken.googleapis.com/v1/token?key=" + firebase_apikey, data=json_data, headers=headers)

    try:
        loader = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        message = json.loads(e.read().decode("utf-8"))
        print(message["error"]["message"])
    else:
        data = json.loads(loader.read().decode("utf-8"))
        access_token = data['access_token']
        print(access_token)


def upload_file():
    global access_token
    global app_id
    global filename
    my_file = open(filename, "rb")
    my_bytes = my_file.read()
    my_url = "https://firebasestorage.googleapis.com/v0/b/" + \
        app_id + ".appspot.com/o/images%2F" + filename
    my_type = mimetypes.guess_type(filename)
    print(my_type[0])
    my_headers = {"Authorization": "Bearer " +
                  access_token, "Content-Type": my_type[0]}

    my_request = urllib.request.Request(
        my_url, data=my_bytes, headers=my_headers, method="POST")

    try:
        loader = urllib.request.urlopen(my_request)
    except urllib.error.URLError as e:
        message = json.loads(e.read().decode("utf-8"))
        print(message["error"]["message"])
    else:
        print(loader.read().decode("utf-8"))


def save_entry(lat,lon,app_id,numCamion,access_token):
    my_data = dict()
    my_data["lat"] = lat
    my_data["lon"] = lon
    my_data["timestamp"] = {".sv": "timestamp"}

    json_data = json.dumps(my_data).encode()
    print("https://"+app_id+".firebaseio.com/camiones/"+numCamion+".json")
    try:
        loader = urllib.request.urlopen("https://"+app_id+".firebaseio.com/camiones/"+numCamion+".json?auth="+access_token, data=json_data)
        print("https://"+app_id+".firebaseio.com/camiones/"+numCamion)
    except urllib.error.URLError as e:
        message = json.loads(e.read().decode("utf-8"))
        print(message["error"])
    else:
        print(loader.read().decode("utf-8"))

def takePicture():
    bashCommand = "fswebcam -d /dev/video0 --set brightness=50% foto_"+numCamion+".png"
    output = subprocess.check_output(['bash','-c', bashCommand])
    time.sleep(3)

    
def gpsPoll(lat,lon):
    conexion = gps3.GPSDSocket()
    stream = gps3.DataStream()
    conexion.connect()
    conexion.watch()
    for datos in conexion:
        if datos:
            stream.unpack(datos)
            print(stream.TPV['time'])
            lat = stream.TPV['lat']
            lon = stream.TPV['lon']
            print(lat,"\n",lon,"\n")
            takePicture()
            save_entry(lat,lon,app_id,numCamion,access_token)
            upload_file()


    
refreshToken = 0
access_token = 0
lat = " "
lon = " "
numCamion = "2"
app_id = "testfire-miag5"
filename = "foto_"+numCamion+".png"
firebase_apikey = "AIzaSyA-TEtL45EZDYWF28aNRfWzXXG6-yJaxlM"
signin()
while True:
    refresh_accesstoken(refreshToken)
    gpsPoll(lat,lon)
