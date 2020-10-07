import xml
import datetime
from xml.etree import ElementTree as ET
from flask import request

def read_xml():
    file = xml.dom.minidom.parse('text.xml')
    root=file.documentElement       #3.获取dom对象元素
    ID = root.getElementsByTagName('id')[0].firstChild.data
    datastarttime =  root.getElementsByTagName('datastarttime')[0].firstChild.data
    dataendtime =  root.getElementsByTagName('dataendtime')[0].firstChild.data
    t1 = datetime.datetime.strptime(datastarttime,'%Y-%m-%d %H:%M:%S')
    t2 = datetime.datetime.strptime(dataendtime,'%Y-%m-%d %H:%M:%S')
    day = (t2 - t1).days
    return ID,datastarttime,day


def read_json(data):
	# data = request.get_json()
    ID = data["param"]["id"]
    datastarttime = data["param"]["datastarttime"]
    dataendtime = data["param"]["dataendtime"]
    t1 = datetime.datetime.strptime(datastarttime,'%Y-%m-%d %H:%M:%S')
    t2 = datetime.datetime.strptime(dataendtime,'%Y-%m-%d %H:%M:%S')
    day = (t2 - t1).days
    return ID,datastarttime,day