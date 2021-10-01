__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os

whl_dir = "dist"
base_url = "https://github.com/easyScience/easyDifractionLib/releases/download/eDL_alpha/"

file = [file for file in os.listdir(whl_dir) if file.endswith(".whl")][0]

header = "<!DOCTYPE html>\n<html>\n<head>\n<title>Links for easyDiffractionLib (alpha)</title>\n</head>\n<body>\n<h1>Links for easyDiffractionLib</h1>"
body = f'<a href="{base_url}{file}" data-requires-python="&gt=3.7,&lt4.0">{file[:-4]}</a><br/>'
footer = "</body>\n</html>"

content = "\n".join([header, body, footer])
with open("index.html", "w") as fid:
    fid.write(content)
