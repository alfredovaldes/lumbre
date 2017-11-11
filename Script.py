import urllib.request
import urllib.error
import json
import mimetypes


def signin(email, password):
    global refreshToken
    my_data = dict()
    my_data["email"] = email
    my_data["password"] = password
    my_data["returnSecureToken"] = True

    json_data = json.dumps(my_data).encode()
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + firebase_apikey, data=json_data, headers=headers)

    try:
        loader = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        message = json.loads(e.read())
        print(message["error"]["message"])
    else:
        data = json.loads(loader.read())
        refreshToken = data['refreshToken']
        # print(data['idToken'])


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
        message = json.loads(e.read())
        print(message["error"]["message"])
    else:
        data = json.loads(loader.read())
        access_token = data['access_token']


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
        message = json.loads(e.read())
        print(message["error"]["message"])
    else:
        print(loader.read())


refreshToken = 0
access_token = 0
app_id = "app_id"
filename = "filename"
firebase_apikey = "apikey"
signin("email", "password")
refresh_accesstoken(refreshToken)
upload_file()
