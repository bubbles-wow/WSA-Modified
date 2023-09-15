import os
import html
import base64
import logging
import requests

from typing import Any, OrderedDict
from xml.dom import minidom
from requests import Session

class Prop(OrderedDict):
    def __init__(self, props: str = ...) -> None:
        super().__init__()
        for i, line in enumerate(props.splitlines(False)):
            if '=' in line:
                k, v = line.split('=', 1)
                self[k] = v
            else:
                self[f".{i}"] = line

    def __setattr__(self, __name: str, __value: Any) -> None:
        self[__name] = __value

    def __repr__(self):
        return '\n'.join(f'{item}={self[item]}' for item in self)

logging.captureWarnings(True)
dir = os.path.dirname(__file__)

release_type = "WIF"

#Catagory ID
cat_id = '858014f3-3934-4abe-8078-4aa193e74ca8'

session = Session()
session.verify = False

def checker(user, release_type):
    with open("./xml/GetCookie.xml", "r") as f:
        cookie_content = f.read().format(user)
        f.close()
    try:
        out = session.post(
            'https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx',
            data=cookie_content,
            headers={'Content-Type': 'application/soap+xml; charset=utf-8'}
        )
    except:
        print("Network Error!")
        return 1
    doc = minidom.parseString(out.text)
    cookie = doc.getElementsByTagName('EncryptedData')[0].firstChild.nodeValue
    with open("./xml/WUIDRequest.xml", "r") as f:
        cat_id_content = f.read().format(user, cookie, cat_id, release_type)
        f.close()
    try:
        out = session.post(
            'https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx',
            data=cat_id_content,
            headers={'Content-Type': 'application/soap+xml; charset=utf-8'}
        )
    except:
        print("Network Error!")
        return 1
    doc = minidom.parseString(html.unescape(out.text))
    filenames = {}
    for node in doc.getElementsByTagName('ExtendedUpdateInfo')[0].getElementsByTagName('Updates')[0].getElementsByTagName('Update'):
        node_xml = node.getElementsByTagName('Xml')[0]
        node_files = node_xml.getElementsByTagName('Files')
        if not node_files:
            continue
        else:
            for node_file in node_files[0].getElementsByTagName('File'):
                if node_file.hasAttribute('InstallerSpecificIdentifier') and node_file.hasAttribute('FileName'):
                    filenames[node.getElementsByTagName('ID')[0].firstChild.nodeValue] = (f"{node_file.attributes['InstallerSpecificIdentifier'].value}_{node_file.attributes['FileName'].value}",
                                                                                          node_xml.getElementsByTagName('ExtendedProperties')[0].attributes['PackageIdentityName'].value)
    info_list = []
    for value in filenames.values():
        if value[0].find("_neutral_") != -1:
            info_list.append(value[0])
    info_list = sorted(
        info_list,
        key=lambda x: (
            x.split("_")[1].split(".")[0],
            x.split("_")[1].split(".")[1],
            x.split("_")[1].split(".")[2],
            x.split("_")[1].split(".")[3]
        ),
        reverse=False
    )
    os.popen(f"echo \"WSAVER={info_list[-1].split("_")[1]}\" >> \"$GITHUB_OUTPUT\"")

user_code = ""
try:
    response = requests.get("https://api.github.com/repos/bubbles-wow/MS-Account-Token/contents/token.cfg")
    if response.status_code == 200:
        content = response.json()["content"]
        content = content.encode("utf-8")
        content = base64.b64decode(content)
        text = content.decode("utf-8")
        user_code = Prop(text).get("user_code")
        updatetime = Prop(text).get("update_time")
        print("Successfully get user token from server!")
        print(f"Last update time: {updatetime}\n")
    else:
        user_code = ""
        print(f"Failed to get user token from server! Error code: {response.status_code}\n")
except:
    user_code = ""
    print("Failed to get user token from server!\n")
checker(user_code, release_type)

        
