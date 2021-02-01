import re

import aiohttp

from tars import tarscore
from tars.models import *

ayyuid_int = 0


class Huya:
    heartbeat = b'\x00\x03\x1d\x00\x00\x69\x00\x00\x00\x69\x10\x03\x2c\x3c\x4c\x56\x08\x6f\x6e\x6c\x69\x6e\x65\x75\x69\x66\x0f\x4f\x6e\x55\x73\x65\x72\x48\x65\x61\x72\x74\x42\x65\x61\x74\x7d\x00\x00\x3c\x08\x00\x01\x06\x04\x74\x52\x65\x71\x1d\x00\x00\x2f\x0a\x0a\x0c\x16\x00\x26\x00\x36\x07\x61\x64\x72\x5f\x77\x61\x70\x46\x00\x0b\x12\x03\xae\xf0\x0f\x22\x03\xae\xf0\x0f\x3c\x42\x6d\x52\x02\x60\x5c\x60\x01\x7c\x82\x00\x0b\xb0\x1f\x9c\xac\x0b\x8c\x98\x0c\xa8\x0c'

    async def get_ws_info(url):
        reg_datas = []
        url = 'https://m.huya.com/' + url.split('/')[-1]
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                room_page = await resp.text()
                global ayyuid_int
                # print(room_page)
                m = re.search(r"ayyuid: +'([0-9]+)'", room_page, re.MULTILINE)
                ayyuid = m.group(1)
                ayyuid_int = int(ayyuid)
                m = re.search(r"TOPSID += +'([0-9]+)'", room_page, re.MULTILINE)
                tid = m.group(1)
                m = re.search(r"SUBSID += +'([0-9]+)'", room_page, re.MULTILINE)
                sid = m.group(1)
                # print(ayyuid)
                # print(tid)
                # print(sid)

        oos = tarscore.TarsOutputStream()
        oos.write(tarscore.int64, 0, int(ayyuid))
        oos.write(tarscore.boolean, 1, True)  # Anonymous
        oos.write(tarscore.string, 2, "")  # sGuid
        oos.write(tarscore.string, 3, "")
        oos.write(tarscore.int64, 4, int(tid))
        oos.write(tarscore.int64, 5, int(sid))
        oos.write(tarscore.int64, 6, 0)
        oos.write(tarscore.int64, 7, 0)

        wscmd = tarscore.TarsOutputStream()
        wscmd.write(tarscore.int32, 0, 1)
        wscmd.write(tarscore.bytes, 1, oos.getBuffer())

        reg_datas.append(wscmd.getBuffer())
        return 'wss://cdnws.api.huya.com/', reg_datas

    def decode_msg(data):
        stream = tarscore.TarsInputStream(data)
        command = WebSocketCommand()
        command.readFrom(stream)
        return [command]

    def create_msg(message):

        wup = Wup()
        wup.set_Req(SendMessageReq(message, ayyuid_int))

        command = WebSocketCommand()
        command.iCmdType = 3
        command.vData = wup.bin_buffer()

        return command.bin_buffer()

    def login():
        command = WebSocketCommand()
        command.iCmdType = 10
        command.vData = WSVerifyCookieReq().bin_buffer()
        return command.bin_buffer()