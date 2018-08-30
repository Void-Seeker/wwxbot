import aprslib
import logging
import time
import threading
import requests

logging.basicConfig(level=logging.DEBUG)

callsign = "UR5RFF-15"
password = '21924'
dst = 'APRS'
lat = '5131.45N'
lng = '03045.83E'
symbol = 'AW'
comment = 'Weather bot'
# TODO Specify longitude and latitude in decimal format and convert into APRS format


def antitrim(line, char, reqlength):
    if len(line) < reqlength:
        return line + (reqlength - len(line)) * char
    else:
        return line


def beacon():
    global AIS
    while True:
        AIS.sendall(callsign + '>' + dst + ',TCPIP*:=' + lat + symbol[0] + lng + symbol[1] + comment)
        time.sleep(600)


def respond(msg):
    print(msg)
    r = requests.get('https://api.aprs.fi/api/get?name=' + msg['from']
                     + '&what=loc&apikey=108829.nt375IMvw8nlF&format=json').json()
    if r['found'] != 1:
        print('Warning: Found ' + r['found'] + ' entries')
    sender = r['entries'][0]
    print(sender)


def callback(packet):
    try:
        obj = aprslib.parse(packet)
        print(obj)
        if obj['format'] == 'message' and obj['addresse'] == callsign:
            spec = obj['message_text'].split('{')
            if len(spec) == 2:
                line = callsign + '>' + dst + ',TCPIP*::' + antitrim(obj['from'], ' ', 9) + ':ack' + spec[-1]
                AIS.sendall(line)
            obj['message_text'] = spec[0]
            respond(obj)
    except aprslib.ParseError as exp:
        print(packet)


AIS = aprslib.IS(callsign, passwd=password, port=14580)
AIS.set_filter('g/'+callsign)
try:
    AIS.connect()
    t = threading.Thread(target=beacon)
    t.start()
    AIS.consumer(callback, raw=True, blocking=True)
finally:
    AIS.close()
