import aprslib
import logging
logging.basicConfig(level=logging.DEBUG)

callsign = "UR5RFF-15"
password = '21924'

def antitrim(line, char, reqLength):
    if (len(line) < reqLength):
        return line + (reqLength - len(line)) * char
    else:
        return line

def callback(packet):
    try:
        obj = aprslib.parse(packet)
        print(obj)
        if obj['format'] == 'message':
            spec = obj['message_text'].split('{')
            if len(spec) == 2:
                line = callsign+'>APRS,TCPIP*::'+antitrim(obj['from'], ' ', 9)+':ack'+spec[-1]
                AIS.sendall(line)
    except  (aprslib.ParseError) as exp:
        print(packet)


AIS = aprslib.IS(callsign, passwd=password, port=14580)
AIS.connect()
AIS.sendall(callsign+'>APRS,TCPIP*:=5131.45NA03045.83EWweather bot')

AIS.consumer(callback, raw=True)
