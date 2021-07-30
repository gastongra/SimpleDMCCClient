import socket
import ssl
import pprint
import struct
from time import sleep
import logging
from threading import Thread
from XMLMessages import XMLMessages
import xml.etree.ElementTree as ET

class DmccClient(object):
    def __init__(self, ip, port, hostname):
        self.__responses__ = {}
        self.__events__ = []
        self.__allDone__ = False
        self.__responseListener__ = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tlsContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        tlsContext.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        tlsContext.check_hostname = False
        tlsContext.verify_mode = ssl.CERT_NONE
        self.__dmccConn__ = tlsContext.wrap_socket(sock,
                                                   server_hostname=hostname)
        self.__dmccConn__.settimeout(5.0)
        try:
            self.__dmccConn__.connect((ip, port))
        except socket.timeout:
            logging.debug("Timeout when trying to connect to AES. Check AES server availability.")
            raise
        except Exception as e:
            logging.debug(str(e) + " exception when trying to connect to AES.")
            raise
        logging.debug("Connected to: " + self.__dmccConn__.server_hostname + " " +  repr(self.__dmccConn__.getpeername()))
        logging.debug("Ciphers offered to the server (cipher name,protocol version,secret bits #): ")
        logging.debug(self.__dmccConn__.shared_ciphers())
        logging.debug("SSL version negotiated with server: ")
        logging.debug(self.__dmccConn__.version)
        logging.debug("Cipher negotiated with server (cipher name,protocol version,secret bits #): ")
        logging.debug(self.__dmccConn__.cipher())
        logging.debug("******************************\nServer identifies itself as follows:\n\n")
        logging.debug(pprint.pformat(self.__dmccConn__.getpeercert()))
        logging.debug("******************************\n\n")
        self.__responseListener__ = Thread(target=self.responseListener)
        self.__responseListener__.setName("responseListener")
        self.__responseListener__.start()

#This function spawns a thread to listen for incoming XML messages from AES server
#and loads it into a dictionary of responses with key = invokeID
    def responseListener(self):
        # According to CSTA-ECMA 323 Standard ANNEX J Section J.2.
        # CSTA XML without SOAP, the Header is  8 bytes long:

        # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
        # |VERSION|LENGTH |   INVOKE ID   |   XML PAYLOAD

        # VERSION: 2 bytes
        # LENGTH: 2 bytes information that contains the total size
        # (XML payload + Header)
        # INVOKE ID: 4 bytes.  The id should be unique
        while not self.__allDone__:
            try:
                cstaHeader = self.__dmccConn__.recv(8)
            except socket.timeout:
                logging.debug('No data received. Iterating ...')
            else: #message received
                version, length, invokeID = struct.unpack('>hh4s', cstaHeader)
                message = self.__dmccConn__.recv(length).decode("utf-8")
                strInvokeID = str(invokeID, 'UTF-8')
                if strInvokeID!='9999':
                    self.__responses__[strInvokeID] = message
                else:
                    logging.debug("Event received:\t\tInvokeID="+strInvokeID+"\n"+message)
                    eventXML = ET.fromstring(message)
                    eventType = eventXML.tag.rpartition('}')[2]
                    eventData = {'event':eventType}
                    if eventType == "EstablishedEvent" :
                        eventData.update({'monitorCrossRefId': eventXML[0].text,'callId': eventXML[1][0].text})
                    elif eventType == 'StopEvent':
                        eventData.update({'monitorCrossRefId': eventXML[0].text})
                    self.__events__.append(eventData)
                sleep(0.5)
        logging.debug("All Done. Nos vamos!!!")

#This function waits until one of the below conditions is met:
# AES sends an audio StopEvent on the monitor we started
# the given timeout is reached
    def waitForAudioStopEvent(self, monitorCrossRefId, timeToWait):
        found = False
        timer = 0
        while timer < timeToWait and not found:
            sleep(1)
            i = 0
            while i < len(self.__events__) and not found:
                event = self.__events__[i]
                if event['event'] == 'StopEvent':
                    if event['monitorCrossRefId'] == str(monitorCrossRefId):
                        found = True
                i = i + 1
            timer = timer + 1
        return(found)

#This function reads the events list in search of a CallEstablished event for the given call ID.
#It returns true if such an event was found or False if the timeout was reached and the event was not received  
    def waitForEstablishedEvent(self, callId, timeToWait):
        found = False
        timer = 0
        while timer < timeToWait and not found:
            sleep(1)
            i = 0
            while i < len(self.__events__) and not found:
                event = self.__events__[i]
                if event['event'] == 'EstablishedEvent':
                    if event['callId'] == str(callId):
                        found = True
                i = i + 1
            timer = timer + 1
        return(found)

    def getConn(self):
        return self.__dmccConn__

    def getResponses(self):
        return self.__responses__
        
    #This function sends an XML message to the AES
    def sendRequest(self, message, invokeID):
        # According to CSTA-ECMA 323 Standard ANNEX J Section J.2.
        # CSTA XML without SOAP, the Header is  8 bytes long:

        # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
        # |VERSION|LENGTH |   INVOKE ID   |   XML PAYLOAD

        # VERSION: 2 bytes
        # LENGTH: 2 bytes information that contains the total size
        # (XML payload + Header)
        # INVOKE ID: 4 bytes.  The id should be unique

        global responses
        version = 0
        length = len(message)+8
        self.__dmccConn__.sendall(struct.pack('>h', version))
        self.__dmccConn__.sendall(struct.pack('>h', length))
        self.__dmccConn__.sendall(bytes(invokeID, 'UTF-8'))
        self.__dmccConn__.sendall(bytes(message, 'UTF-8'))
        logging.debug("sending message:\t\tInvokeID=" + invokeID+'\n'+ message)

    #This function reads the responses dictionary in search of a response with the given invokeID
    #It returns the entire XML message as it was sent from AES
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def readResponse(self, invokeID, timeToWait):
        for timer in range(timeToWait):
            sleep(1)
            if invokeID in self.__responses__:
                break
        return(self.__responses__.get(invokeID, ''))

    #This function reads the responses dictionary in search of a response with the given invokeID
    #and parses it assuming the response is for a "Start App Session" request
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def handleStartAppSessionResponse(self, invokeID, timeToWait):
        response = self.readResponse(invokeID, timeToWait)
        if response != '':
            xmlResponse = ET.fromstring(response.encode('utf-8'))
            logging.debug("DMCC session established. Tag: "+xmlResponse[0].tag+' --- Text: '+xmlResponse[0].text)
            return(xmlResponse[0].text)
        else:
            return('')

    #This function reads the responses dictionary in search of a response with the given invokeID
    #and parses it assuming the response is for a "GetDeviceId" request
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def handleGetDeviceIdResponse(self, invokeID, timeToWait):
        response = self.readResponse(invokeID, timeToWait)
        if response != '':
            xmlResponse = ET.fromstring(response.encode('utf-8'))
            logging.debug("Device Id obtained. Tag: "+xmlResponse[0].tag+' --- Text: '+xmlResponse[0].text)
            return(xmlResponse[0].text)
        else:
            return('')

    #This function reads the responses dictionary in search of a response with the given invokeID
    #and parses it assuming the response is for a "MonitorStart" request
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def handleMonitorStartResponse(self, invokeID, timeToWait):
        response = self.readResponse(invokeID, timeToWait)
        if response != '':
            xmlResponse = ET.fromstring(response.encode('utf-8'))
            logging.debug("monitorCrossRefID obtained. Tag: "+xmlResponse[0].tag+' --- Text: '+xmlResponse[0].text)
            if xmlResponse[0].text.isdigit():
                return(int(xmlResponse[0].text))
            else:
                return(-1)
        else:
            return(0)

    def handleRegisterTerminalResponse(self, invokeID, timeToWait):
        response = self.readResponse(invokeID, timeToWait)
        if response != '':
            xmlResponse = ET.fromstring(response.encode('utf-8'))
            if xmlResponse[1].tag.endswith('signalingEncryption'):
                logging.debug("Regsitration successful. "+xmlResponse[1].tag+': '+xmlResponse[1].text)
                return(int(xmlResponse[2].text))
            else:
                logging.info('Station registration failed. Reason is:' +xmlResponse[2].text)
                return(int(xmlResponse[1].text))
        else:
            logging.info(str(timeToWait) + ' seconds registration timer expired. Got no response from AES')
            return(-1)

    def handleMakeCallResponse(self, invokeID, timeToWait):
        response = self.readResponse(invokeID, timeToWait)
        if response != '':
            xmlResponse = ET.fromstring(response.encode('utf-8'))
            if xmlResponse[0][0].tag.endswith('callID'):
                logging.debug("CallID is: "+xmlResponse[0][0].tag+': '+xmlResponse[0][0].text)
                return(int(xmlResponse[0][0].text))
            else:
                logging.debug('Call failed')
                return(int(xmlResponse[0][0].text))
        else:
            return(-1)

    def setAlldone(self):
            self.__allDone__ = True

def main():

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(relativeCreated)6d|%(threadName)s|%(message)s')
    logging.info("This is DmccClient, a simple python module to interact with Avaya AES through XML DMCC API.")
    logging.info("Do something here")

if __name__ == '__main__':
    responses = {}
    main()