import aprslib
import logging
import time
import threading
import requests

logging.basicConfig(level=logging.DEBUG)

# APRS callsign
callsign = "UR5RFF-15"
# Passcode for APRS-IS
passcode = '21924'
# AX.25 destination callsign is used to identify client software in APRS
dst = 'APRS'
# Coordinates of the beacon, negative for south and west
dec_lat = 51.524074
dec_lng = 30.765151
# lat = '5131.45N'
# lng = '03045.83E'
# Icon for APRS beacon (see http://www.aprs.org/symbols.html for info)
symbol = 'AW'
# APRS beacon comment
comment = 'Weather bot'
# API key for aprs.fi for retrieving station information (see https://aprs.fi/page/api)
aprsapikey = '108829.nt375IMvw8nlF'
# API key for OpenWeatherMap (see https://openweathermap.org/api)
weatherapikey = '867c8256a6b0b30f57dc04350ee394a6'


def decimaltoaprs(decimal, lng=False):
    if not lng:
        if decimal >= 0:
            s = 'N'
        else:
            s = 'S'
    else:
        if decimal >= 0:
            s = 'E'
        else:
            s = 'W'
    dec = abs(decimal)
    degrees = int(dec)
    minutes = 60*(dec-degrees)
    result = "{:02}".format(int(minutes)) + '.' + "{:02}".format(int(100 * (minutes - int(minutes)))) + s
    if not lng:
        result = "{:02}".format(degrees) + result
    else:
        result = "{:03}".format(degrees) + result
    return result


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
                     + '&what=loc&apikey=' + aprsapikey + '&format=json').json()
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
                line = callsign + '>' + dst + ',TCPIP*::' + antitrim(obj['from'], ' ', 9) + ':ack'\
                       + spec[-1].replace('}', '')
                AIS.sendall(line)
            obj['message_text'] = spec[0]
            respond(obj)
    except aprslib.ParseError as exp:
        print(packet)


lat = decimaltoaprs(dec_lat)
lng = decimaltoaprs(dec_lng, True)
AIS = aprslib.IS(callsign, passwd=passcode, port=14580)
AIS.set_filter('g/'+callsign)
try:
    AIS.connect()
    t = threading.Thread(target=beacon)
    t.start()
    AIS.consumer(callback, raw=True, blocking=True)
finally:
    AIS.close()
