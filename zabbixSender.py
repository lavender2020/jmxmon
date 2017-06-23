#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017/5/3 17:27
# @Author  : liutongsheng@hujiang.com
# @Version :


import sys
import os
import json
import socket
import struct

reload(sys)
sys.setdefaultencoding("utf-8")


from datetime import datetime

base_dir = os.path.split(os.path.realpath(sys.argv[0]))[0]  # 获取程序的运行目录
jmx_mon = base_dir + "/jmxmon.txt"

conf_file=base_dir + "/conf.properties"

def get_pro_name(port):
    jmxport=str(port).split("=")[1]
    #print jmxport
    with open(conf_file,'r') as f:
        for line in  f.readlines ():
            if(line.find("=")>-1):
                item= line.strip().split("=")[0]
                value=line.strip().split("=")[1]
                if(item=="port2project"):
                    for k in value.split(","):
                        if( k.split('@')[0]==str(jmxport)):
                            return k.split('@')[1]
    return "none-set"


class ZabbixSender:
    zbx_header = 'ZBXD'
    zbx_version = 1
    zbx_sender_data = {u'request': u'sender data', u'data': []}
    send_data = ''

    def __init__(self, server_host, server_port=10051):
        self.server_ip = socket.gethostbyname(server_host)
        self.server_port = server_port

    def AddData(self, host, key, value, clock=None):
        add_data = {u'host': host, u'key': key, u'value': value}
        if clock != None:
            add_data[u'clock'] = clock
        self.zbx_sender_data['data'].append(add_data)
        return self.zbx_sender_data

    def ClearData(self):
        self.zbx_sender_data['data'] = []
        return self.zbx_sender_data

    def __MakeSendData(self):
        zbx_sender_json = json.dumps(self.zbx_sender_data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        json_byte = len(zbx_sender_json)
        self.send_data = struct.pack("<4sBq" + str(json_byte) + "s", self.zbx_header, self.zbx_version, json_byte, zbx_sender_json)

    def Send(self):
        self.__MakeSendData()
        so = socket.socket()
        so.connect((self.server_ip, self.server_port))
        wobj = so.makefile(u'wb')
        wobj.write(self.send_data)
        wobj.close()
        robj = so.makefile(u'rb')
        recv_data = robj.read()
        robj.close()
        so.close()
        tmp_data = struct.unpack("<4sBq" + str(len(recv_data) - struct.calcsize("<4sBq")) + "s", recv_data)
        recv_json = json.loads(tmp_data[3])
        # self.ClearData()
        return recv_data


def read_from_txt():
    with open(jmx_mon, 'r') as f:
        return (f.read().strip())


def make_lld():
    jmx_json = json.loads(read_from_txt())
    # lld_lst = [{"{#JAVAKEY}": jmx['metric'] + "@" + jmx['tags'][8:]} for jmx in jmx_json]
    #lld_lst = [{"{#JAVAKEY}": jmx['metric'] + "@" + jmx['tags'][8:], "{#JAVANOTE}": jmx['tags']} for jmx in jmx_json]
    lld_lst = [{"{#JAVAKEY}": jmx['metric'] + "@" + jmx['tags'][8:], "{#JAVANOTE}": get_pro_name(jmx['tags'])} for jmx in jmx_json]
    return json.dumps({'data': lld_lst}, sort_keys=True, indent=4, separators=(',', ':'))

if __name__ == '__main__':
    jmx_json = json.loads(read_from_txt())
    host_name = jmx_json[0]["endpoint"]
    #host_name = "weathermap"
    # print host_name
    sender = ZabbixSender(u'zabbix-proxy.yeshj.com')
    if(datetime.now().strftime("%H%M") == "2300" or len(sys.argv) == 2):
        sender.AddData(host_name, u'trapper.lld', make_lld())
        res = sender.Send()
        # print "lld.Send()"
        sender.ClearData()
        print res
        sys.exit()
    for jmx in jmx_json:
        key = "trapper.get[" + jmx['metric'] + "@" + jmx['tags'][8:] + "]"
        # print (host_name,key,jmx["value"])
        sender.AddData(host_name, key, jmx["value"])
        # print "data"
    res = sender.Send()
    print res
    sender.ClearData()
