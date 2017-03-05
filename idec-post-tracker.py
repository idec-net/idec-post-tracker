#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys, os, urllib.request, urllib.parse, json, base64

configFile = "tracker.cfg"
cacheDir = "tracker_cache"
address = ""
auth = ""
echoarea = ""

def isEmpty(string):
    return string == "" or string == None

def changedLastTime(number, time):
    try:
        f = open(cacheDir + "/" + number).read()
        return not (f == time)
    except:
        return True

class Seventeen:
    def receiveData(self, number):
        baseurl = 'http://www.17track.net/restapi/handlertrack.ashx'
        form_data = bytes('{"guid":"","data":[{"num":"' + number + '"}]}', "UTF-8")

        data = urllib.request.urlopen(baseurl, form_data).read().decode("UTF-8")
        return json.loads(data)

    def parser(self, data):
        k = data['dat'][0]
        time = k['track']['z0']['a']
        location = k['track']['z0']['c']
        message = k['track']['z0']['z']

        return time, location + " - " + message

class Cainiao:
    def receiveData(self, number):
        baseurl = "https://global.cainiao.com/trackWebQueryRpc/getTrackingInfos.json?mailNoList="
        data = urllib.request.urlopen(baseurl + number).read().decode("UTF-8")
        return json.loads(data)

    def parser(self, data):
        lastparcel = data["data"][0]["section2"]["detailList"][0]
        time = lastparcel["time"]
        message = lastparcel["desc"]

        return time, message

try:
    config = open("tracker.cfg").read()
except:
    print("Error reading config, exiting")
    sys.exit(1)

if not os.path.exists(cacheDir):
    print("Directory " + cacheDir + " does not exist. Creating...")
    os.makedirs(cacheDir)

for line in config.splitlines():
    line = line.strip()

    if isEmpty(address):
        address = line
        continue
    elif isEmpty(auth):
        auth = line
        continue
    elif isEmpty(echoarea):
        echoarea = line
        continue

    keys = line.split(" ")

    if len(keys) < 2:
        continue

    number = keys[0]
    provider = keys[1]

    if len(keys[2:]) > 0:
        extra = " ".join(keys[2:])
    else:
        extra = "None"

    try:
        worker = None
        if provider == "cainiao":
            worker = Cainiao()
        elif provider == "17track":
            worker = Seventeen()
        else:
            print("Wrong provider, please specify real name!")
            continue

        print("Processing " + number + " with " + provider + "...")

        data = worker.receiveData(number)
        if isEmpty(data):
            print("Error getting data")
            continue

        try:
            time, message = worker.parser(data)
        except Exception as e:
            print(data)
            print(str(e))
            continue

        if isEmpty(time):
            print("Error: time is empty")
            continue

        if changedLastTime(number, time):
            tmsg = echoarea + "\n" + "All" + "\n" + extra + "\n\n" + number + "\n\n" + (time + " - " + message).strip()
            tmsg = base64.b64encode(tmsg.encode("utf-8"))

            post_data = urllib.parse.urlencode({"tmsg": tmsg, "pauth": auth}).encode("utf-8")
            request = urllib.request.Request(address + "u/point")
            result = urllib.request.urlopen(request, post_data).read().decode("utf-8")

            if result.startswith("msg ok"):
                open(cacheDir + "/" + number, "w").write(time)
            print(result)

    except Exception as e:
        print("Exception: " + str(e))
        raise
        continue
