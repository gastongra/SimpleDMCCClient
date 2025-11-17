import socket
import ssl
import pprint
import struct
from time import time, sleep
import logging
from threading import Thread
from XMLMessages import XMLMessages
import xml.etree.ElementTree as ET

class DmccClient(object):
    def __init__(self, ip, port, hostname):
        self.__responses = {}  # response dictionary (invoke_id:Message)
        self.__events = [] # list of events received by the monitors (event 1, event 2, event 3, etc.)
        self.__all_done = False
        self.__response_listener = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        tls_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        #tls_context.check_hostname = True
        tls_context.check_hostname = False
        #tls_context.verify_mode = ssl.CERT_REQUIRED
        tls_context.verify_mode = ssl.CERT_NONE
        # tls_context.load_verify_locations("cacerts.pem", None)
        self.__dmcc_conn = tls_context.wrap_socket(sock,
                                                   server_hostname=hostname)
        self.__dmcc_conn.settimeout(5.0)
        try:
            self.__dmcc_conn.connect((ip, port))
        except socket.timeout:
            raise DMCCSessionError("DMCCSessionError Exception: Timeout when trying to establish DMCC session. Check AES server availability.")
        except Exception as e:
            logging.debug(str(e) + " exception when trying to connect to AES.")
            raise
        logging.debug("Connected to: " + self.__dmcc_conn.server_hostname + " " +  repr(self.__dmcc_conn.getpeername()))
        logging.debug("Ciphers offered to the server (cipher name,protocol version,secret bits #): ")
        logging.debug(self.__dmcc_conn.shared_ciphers())
        logging.debug("SSL version negotiated with server: ")
        logging.debug(self.__dmcc_conn.version)
        logging.debug("Cipher negotiated with server (cipher name,protocol version,secret bits #): ")
        logging.debug(self.__dmcc_conn.cipher())
        logging.debug("******************************\nServer identifies itself as follows:\n\n")
        logging.debug(pprint.pformat(self.__dmcc_conn.getpeercert()))
        logging.debug("******************************\n\n")
        self.__response_listener = Thread(target=self.response_listener)
        self.__response_listener.setName("response_listener")
        self.__response_listener.start() #spawns a thread to listen for incoming XML messages from AES server

#This function handles incoming XML messages from AES server
#and loads it into a dictionary of responses with key = invoke_id
    def response_listener(self):
        # According to CSTA-ECMA 323 Standard ANNEX J Section J.2.
        # CSTA XML without SOAP, the Header is  8 bytes long:

        # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
        # |VERSION|LENGTH |   INVOKE ID   |   XML PAYLOAD

        # VERSION: 2 bytes
        # LENGTH: 2 bytes information that contains the total size (XML payload + Header)
        # INVOKE ID: 4 bytes.  The id should be unique
        while not self.__all_done:
            try:
                csta_header = self.__dmcc_conn.recv(8)
            except socket.timeout:
                logging.debug('No data received. Iterating ...')
            else: #message received
                version, length, invoke_id = struct.unpack('>hh4s', csta_header)
                message = self.__dmcc_conn.recv(length).decode("utf-8")
                str_invoke_id = str(invoke_id, 'UTF-8')
                if str_invoke_id!='9999':
                    self.__responses[str_invoke_id] = message
                else:
                    logging.debug("Event received:\t\tinvoke_id="+str_invoke_id+"\n"+message)
                    event_xml = ET.fromstring(message)
                    event_type = event_xml.tag.rpartition('}')[2]
                    #event_data is a dictionary:
                    event_data = {'event':event_type}
                    if event_type == "EstablishedEvent" :
                        event_data.update({'monitor_cross_ref_id': event_xml[0].text,'call_id': event_xml[1][0].text})
                    elif event_type == 'StopEvent':
                        event_data.update({'monitor_cross_ref_id': event_xml[0].text})
                    self.__events.append(event_data)
                sleep(0.5)
        logging.debug("All Done. Nos vamos!!!")

#This function just waits until one of the below conditions is met:
# AES sends an audio StopEvent on the monitor we started
# OR:
# the given timeout is reached
    def wait_for_audio_stop_event(self, monitor_cross_ref_id, time_to_wait):
        found = False
        start_time = time()
        elapsed__time = -1
        while not found and elapsed__time < time_to_wait:
            sleep(1)
            for event in self.__events :
                if event['event'] == 'StopEvent' and event['monitor_cross_ref_id'] == str(monitor_cross_ref_id):
                    found = True
                    break
            elapsed__time = time()-start_time
        return(found)

#This function reads the events list in search of a CallEstablished event for the given call ID.
#It returns True if such an event was found or False if the timeout was reached and the event was not received  yet
    def wait_for_established_event(self, call_id, time_to_wait):
        found = False
        start_time = time()
        elapsed__time = -1
        while not found and elapsed__time < time_to_wait:
            sleep(1)
            for event in self.__events :
                if event['event'] == 'EstablishedEvent' and event['call_id'] == str(call_id):
                    found = True
                    break
            elapsed__time = time()-start_time
        return(found)

    def get_conn(self):
        return self.__dmcc_conn

    def get_responses(self):
        return self.__responses
        
    #This function sends an XML message to the AES
    def send_request(self, message, invoke_id):
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
        self.__dmcc_conn.sendall(struct.pack('>h', version))
        self.__dmcc_conn.sendall(struct.pack('>h', length))
        self.__dmcc_conn.sendall(bytes(invoke_id, 'UTF-8'))
        self.__dmcc_conn.sendall(bytes(message, 'UTF-8'))
        logging.debug("sending message:\t\tinvoke_id=" + invoke_id+'\n'+ message)

    #This function reads the responses dictionary in search of a response with the given invoke_id
    #It returns the entire XML message as it was sent from AES
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def read_response(self, invoke_id, time_to_wait):
        for timer in range(time_to_wait):
            sleep(1)
            if invoke_id in self.__responses:
                #return(self.__responses.get(invoke_id, ''))
                return(self.__responses.get(invoke_id))
        #The loop reached the time_to_wait interval and invoke_id was not found. We have to raise an exception:
        raise DMCCResponseMissing("We didnt receive any response to invoke_id "+ invoke_id)

    #This function reads the responses dictionary in search of a response with the given invoke_id
    #and parses it assuming the response is for a "Start App Session" request
	#"NOTE: The responses dictionary gets populated by the response listener thread"
    def handle_start_app_session_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)
        xml_response = ET.fromstring(response.encode('utf-8'))
        #To keep in mind:
        #xml_response[0] = sessionID
        #xml_response[1] = actualProtocolVersion
        #xml_response[2] = actualSessionDuration
        logging.debug("DMCC session established. Tag: "+xml_response[0].tag+' --- Text: '+xml_response[0].text)
        #Returns the session ID:
        return(xml_response[0].text)

    #This function reads the responses dictionary in search of a response with the given invoke_id
    #and parses it assuming the response is for a "GetDeviceId" request
	#***NOTE: The responses dictionary gets populated by the response listener thread
    def handle_get_device_id_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)

        if any(error in response for error in ['resourceBusy', 'CSTAErrorCode']):
        #if 'resourceBusy' in response:
            raise DMCCGetDeviceIdError("DMCCGetDeviceIdError. "+response)

        xml_response = ET.fromstring(response.encode('utf-8'))
        #To keep in mind:
        #xml_response[0] = device
        logging.debug("Device Id obtained. Tag: "+xml_response[0].tag+' --- Text: '+xml_response[0].text)
                
        #Returns the device ID:
        return(xml_response[0].text)

    #This function reads the responses dictionary in search of a response with the given invoke_id
    #and parses it assuming the response is for a "MonitorStart" request
	#NOTE: The responses dictionary gets populated by the response listener thread
    def handle_monitor_start_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)
        xml_response = ET.fromstring(response.encode('utf-8'))
        #To keep in mind:
        #xml_response[0] = monitor_cross_ref_id
        logging.debug("monitor_cross_ref_id obtained. Tag: "+xml_response[0].tag+' --- Text: '+xml_response[0].text)
        #Returns the monitor_cross_ref_id
        if xml_response[0].text.isdigit():
            return(int(xml_response[0].text))
        else:
            raise DMCCMonitorStartError("DMCCMonitorStartError: Didn´t get a valid monitor_cross_ref_id. Tag: "+xml_response[0].tag+' --- Text: '+xml_response[0].text)
            return(-1)

    def handle_register_terminal_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)
        xml_response = ET.fromstring(response.encode('utf-8'))
        if xml_response[1].tag.endswith('signalingEncryption'):
            #In a successful registration: xml_response[1] = signalingEncryption and xml_response[2] = code
            logging.debug("Registration successful. "+xml_response[1].tag+': '+xml_response[1].text)
            return(int(xml_response[2].text))
        else:
            #In an unsuccessful login: xml_response[1] = code and xml_response[2] = reason
            raise DMCCRegisterTerminalError("DMCCRegisterTerminalError. Reason is:" +xml_response[2].text)


    def handle_make_call_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)
        xml_response = ET.fromstring(response.encode('utf-8'))
        if xml_response[0][0].tag.endswith('callID'):
            #For a successful call xml_response[0]-->[0] = call_id
            logging.debug("call_id is: "+xml_response[0][0].tag+': '+xml_response[0][0].text)
            return(int(xml_response[0][0].text))
        else:
            #For an unsuccessful call ????
            logging.debug('Call failed for some reason')
            raise DMCCMakeCallError(xml_response[0][0].text)

    def handle_play_message_response(self, invoke_id, time_to_wait):
        response = self.read_response(invoke_id, time_to_wait)
        xml_response = ET.fromstring(response.encode('utf-8'))
        if xml_response.tag.endswith('PlayMessageResponse'):
            #For a successful response we get this simple XML:
            #<?xml version="1.0" encoding="UTF-8"?>
            # #<PlayMessageResponse xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3"/>
            logging.debug("PlayMessage Response received from AES: "+xml_response.tag)
            return(True)
        else:
            #For an unsuccessful response
            logging.debug("PlayMessage Response is not good: "+xml_response.tag)
            raise DMCCPlayMessageError(xml_response.tag)

    def set_all_done(self):
            self.__all_done = True

class DMCCError(Exception):
    """Base class for exceptions in this module."""
    pass

class DMCCSessionError(DMCCError):
    """Exception raised when DMCC session could not be established.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class DMCCResponseMissing(DMCCError):
    """Exception raised when the response we´re looking for was not found

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

class DMCCGetDeviceIdError(DMCCError):
    """Exception raised when the response we´re looking for was not found
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

class DMCCMonitorStartError(DMCCError):
    """Exception raised when the response we´re looking for was not found

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

class DMCCRegisterTerminalError(DMCCError):
    """Exception raised when DMCC session could not be established.
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message


class DMCCMakeCallError(DMCCError):
    """Exception raised when DMCC session could not be established.
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

class DMCCEventTimeoutError(DMCCError):
    """Exception raised when DMCC session could not be established.
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

class DMCCPlayMessageError(DMCCError):
    """Exception raised when DMCC session could not be established.
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(relativeCreated)6d|%(threadName)s|%(message)s')
    logging.info("This is DmccClient, a simple python module to interact with Avaya AES through XML DMCC API.")
    logging.info("opening secure connection to DMCC server")
    global responses
    ip = '10.133.93.73' #AES server´s IP address
    port = 4722 #Secure DMCC service´s port #
    hostname = "linpubad073.gl.avaya.com" #AES server´s FQDN
    switch_conn_name = "CM" #switch connection name as configured in the AES server´s switch connections section
    switch_name = "10.133.93.66" #IP address or FQDN of the CM server
    extension = "1903"
    password = "123456"
    try:
        broker = DmccClient(ip, port, hostname)
    except Exception as e:
        logging.debug(str(e) + " exception. Goodbye :(")
        return
    broker.send_request(XMLMessages.get_start_app_session(), '0001')
    logging.debug(broker.read_response('0001', 5))
    broker.send_request(XMLMessages.get_get_device_id_message(switch_name, extension), '0002')
    logging.debug(broker.read_response('0002', 5))
    broker.send_request(XMLMessages.get_monitor_start_essage(switch_conn_name, switch_name, extension), '0003')
    logging.debug(broker.read_response('0003', 5))
    broker.send_request(XMLMessages.get_snapshot_device_message(switch_conn_name,switch_name, extension), '0004')
    logging.debug(broker.read_response('0004', 5))
    broker.send_request(XMLMessages.get_register_terminal_request_message(switch_conn_name, switch_name, extension, password), '0005')
    logging.debug(broker.read_response('0005', 15))
    input('press any key to continue')
    broker.send_request(XMLMessages.get_snapshot_device_message(switch_conn_name,switch_name, extension), '0007')
    logging.debug(broker.read_response('0007', 5))
    broker.send_request(XMLMessages.get_unregister_terminal_request_message(switch_conn_name, switch_name, extension), '0008')
    logging.debug(broker.read_response('0008', 5))
    broker.send_request(XMLMessages.get_monitor_stop_message(), '0009')
    logging.debug(broker.read_response('0009', 5))
    sleep(1)
    broker.set_all_done()
    sleep(5)
    broker.get_conn().close()
    logging.debug('Graceful shutdown completed. Ending program ...')

if __name__ == '__main__':
    responses = {}
    main()