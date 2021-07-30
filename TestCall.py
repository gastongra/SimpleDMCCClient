from configparser import ConfigParser
from time import sleep
import logging
from DmccClient import DmccClient
from XMLMessages import XMLMessages
import sys

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s|%(relativeCreated)6d|%(threadName)s|%(message)s')
    cfg = ConfigParser()
    cfg.read('config.ini')
    ip = cfg.get('AES','ip')
    port = int(cfg.get('AES','port'))
    hostname = cfg.get('AES','hostname')
    switchConnName = cfg.get('AES','switchConnName')
    switchName = cfg.get('AES','switchName')
    extension = cfg.get('DialingExtension','extension')
    password = cfg.get('DialingExtension','password')
    logging.info("Welcome to simple dialer. We will attempt to establish a DMCC session to AES over XML to make some calls ...")
    logging.info("opening secure connection to DMCC server")
    try:
        dmccClient = DmccClient(ip, port, hostname)
    except Exception as e:
        logging.debug(str(e) + " exception. Goodbye :(")
        return

    #Any DMCC client must perform below actions to do 1st party call control:
    #1. Start Application Session
    #2. GetDeviceId
    #3. MonitorStart
    #4. RegisterTerminal
    #So here we go:
    dmccClient.sendRequest(XMLMessages.getStartAppSession(), '0001')
    sessionID = dmccClient.handleStartAppSessionResponse('0001', 5)
    logging.info('Session created. Session ID is: '+sessionID)
    
    dmccClient.sendRequest(XMLMessages.getGetDeviceIdMessage(switchName, extension), '0002')
    myDeviceId=dmccClient.handleGetDeviceIdResponse('0002', 5)
    if 'resourceBusy' in myDeviceId:
        logging.info('Device is busy. Erroring out ...')
        gracefulShutdown(dmccClient)        
    
    dmccClient.sendRequest(XMLMessages.getMonitorStartMessage(switchConnName, switchName, extension), '0003')
    monitorCrossRefID=dmccClient.handleMonitorStartResponse('0003', 5)
    logging.info('Device Id: '+myDeviceId+' monitorCrossRefID: '+str(monitorCrossRefID))
    
    dmccClient.sendRequest(XMLMessages.getRegisterTerminalRequestMessage(switchConnName, switchName, extension, password), '0005')
    regTerminalResponse = dmccClient.handleRegisterTerminalResponse('0005', 60)
    logging.info('RegisterTerminal Response Code:'+str(regTerminalResponse))
    if regTerminalResponse != 1:
        logging.info('Erroring out ...')
        dmccClient.setAlldone()
        sleep(5)
        dmccClient.getConn().close()
        logging.info('Emergency shutdown completed. Ending program ...')
        sys.exit()
    
    dmccClient.sendRequest(XMLMessages.getGetDeviceIdMessage(switchName, '3301'), '0009')
    calledDeviceId=dmccClient.handleGetDeviceIdResponse('0009', 5)
    
    dmccClient.sendRequest(XMLMessages.getMakeCallRequestMessageWithDeviceId(myDeviceId, calledDeviceId), '0012')
    callId = dmccClient.handleMakeCallResponse('0012', 5)
    if callId > 1:
        logging.info('MakeCall initiated. Call ID:'+str(callId))
    else:
        logging.info('Something happenned with MakeCall. Erroring out ...')
        dmccClient.setAlldone()
        sleep(5)
        dmccClient.getConn().close()
        logging.info('Emergency shutdown completed. Ending program ...')
        sys.exit()
    callEstablished = dmccClient.waitForEstablishedEvent(callId, 60)
    if callEstablished:
        logging.info('Call established.')
    else:
        logging.info('call failed. Erroring out ...')
        gracefulShutdown(dmccClient)
    
    message='0'
    fileName='0001'
    logging.info('audio start')
    dmccClient.sendRequest(XMLMessages.getPlayMessageRequestMessage(extension, switchConnName, switchName, message, fileName), '0020')
    logging.debug(dmccClient.readResponse('0020', 5))
    dmccClient.waitForAudioStopEvent(monitorCrossRefID, 60)
    logging.info('audio stop')
    dmccClient.sendRequest(XMLMessages.getUnregisterTerminalRequestMessage(switchConnName, switchName, extension), '0030')
    logging.debug(dmccClient.readResponse('0030', 5))
    logging.info('station unregistered')
    dmccClient.sendRequest(XMLMessages.getMonitorStopMessage(), '0040')
    logging.debug(dmccClient.readResponse('0040', 5))
    logging.info('monitor stopped')
    sleep(2)
    dmccClient.sendRequest(XMLMessages.getStopApplicationSessionMessage(sessionID), '0050')
    sleep(1)
    gracefulShutdown(dmccClient)

def gracefulShutdown(dmccClient):
        logging.info('Graceful shutdown initiated ...')
        dmccClient.setAlldone()
        sleep(5)
        dmccClient.getConn().close()
        logging.info('Graceful shutdown completed. Ending program ...')
        sys.exit()

if __name__ == '__main__':
    main()