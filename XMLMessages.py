class XMLMessages(object):
    @classmethod
    def getStartAppSession(cls):
        # Read the XML data from a file:
        f = open('appsession.xml', 'r')
        line = f.read()
        f.close()
        return(line)

    def getStopApplicationSessionMessage(sessionID):
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<StopApplicationSession xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<sessionID>''' + sessionID + '''</sessionID>
<sessionEndReason>
<appEndReason>Application Request</appEndReason>
</sessionEndReason>
</StopApplicationSession>'''
        return(message)
        
    def getGetDeviceIdMessage(switchName, extension):
        message = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><GetDeviceId xmlns=\"http://www.avaya.com/csta\"><switchName>"+switchName+"</switchName><extension>"+extension+"</extension></GetDeviceId>"
        return(message)

    def getMonitorStartMessage(switchConnName, switchName, extension):
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<MonitorStart xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
    <monitorObject>
        <deviceObject typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switchConnName+":"+switchName+''':0</deviceObject>
    </monitorObject>
    <requestedMonitorFilter>
        <physicalDeviceFeature>
            <displayUpdated>true</displayUpdated>
            <hookswitch>true</hookswitch>
            <lampMode>true</lampMode>
            <ringerStatus>true</ringerStatus>
        </physicalDeviceFeature>
    <voice>
        <play>true</play>
        <record>true</record>
        <stop>true</stop>
        <suspendPlay>true</suspendPlay>
        <suspendRecord>true</suspendRecord>
    </voice>
    <callcontrol>
        <conferenced>true</conferenced>
        <connectionCleared>true</connectionCleared>
        <delivered>true</delivered>
        <established>true</established>
        <failed>true</failed>
        <originated>true</originated>
        <retrieved>true</retrieved>
        <transferred>true</transferred>
    </callcontrol>
    </requestedMonitorFilter>
    <extensions>
        <privateData>
            <private>
                <AvayaEvents xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="">
                    <invertFilter xmlns="http://www.avaya.com/csta">true</invertFilter>
                    <terminalUnregisteredEvent xmlns="http://www.avaya.com/csta">
                        <unregistered>true</unregistered>
                        <reregistered>true</reregistered>
                    </terminalUnregisteredEvent>
                    <physicalDeviceFeaturesPrivateEvents xmlns="http://www.avaya.com/csta">
                        <serviceLinkStatusChanged>true</serviceLinkStatusChanged>
                    </physicalDeviceFeaturesPrivateEvents>
                </AvayaEvents>
            </private>
        </privateData>
    </extensions>
</MonitorStart>
'''
#mesage without physical device monitors:
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<MonitorStart xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
    <monitorObject>
        <deviceObject typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switchConnName+":"+switchName+''':0</deviceObject>
    </monitorObject>
    <requestedMonitorFilter>
    <voice>
        <play>true</play>
        <record>true</record>
        <stop>true</stop>
        <suspendPlay>true</suspendPlay>
        <suspendRecord>true</suspendRecord>
    </voice>
    <callcontrol>
        <conferenced>true</conferenced>
        <connectionCleared>true</connectionCleared>
        <delivered>true</delivered>
        <established>true</established>
        <failed>true</failed>
        <originated>true</originated>
        <retrieved>true</retrieved>
        <transferred>true</transferred>
    </callcontrol>
    </requestedMonitorFilter>
    <extensions>
        <privateData>
            <private>
                <AvayaEvents xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="">
                    <invertFilter xmlns="http://www.avaya.com/csta">true</invertFilter>
                    <terminalUnregisteredEvent xmlns="http://www.avaya.com/csta">
                        <unregistered>true</unregistered>
                        <reregistered>true</reregistered>
                    </terminalUnregisteredEvent>
                    <physicalDeviceFeaturesPrivateEvents xmlns="http://www.avaya.com/csta">
                        <serviceLinkStatusChanged>true</serviceLinkStatusChanged>
                    </physicalDeviceFeaturesPrivateEvents>
                </AvayaEvents>
            </private>
        </privateData>
    </extensions>
</MonitorStart>
'''
        return(message)

    @classmethod
    def getMonitorStopMessage(cls):
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<MonitorStop xmlns=\"http://www.avaya.com/csta\">
<monitorCrossRefID>1111111</monitorCrossRefID>
</MonitorStop>
'''
        return(message)

    def getSnapshotDeviceMessage(switchConnName, switchName, extension):
        '''#########################################################################
        message = <?xml version="1.0" encoding="utf-8"?>
<SnapshotDevice xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<snapshotObject>''' + extension +":"+switchConnName+":"+switchName+ ''':1</snapshotObject>
<extensions>
<privateData>
<private>
<SnapshotDevicePrivateData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<getStationStatus>true</getStationStatus>
</SnapshotDevicePrivateData>
</private>
</privateData>
</extensions>
</SnapshotDevice>
#########################################################################'''
        message = '''<?xml version="1.0" encoding="utf-8"?>
<SnapshotDevice xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<snapshotObject>'''+extension+":"+switchConnName+":"+switchName+''':1</snapshotObject>
<extensions>
<privateData>
<private>
<SnapshotDevicePrivateData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<getStationStatus>true</getStationStatus>
</SnapshotDevicePrivateData>
</private>
</privateData>
</extensions>
</SnapshotDevice>
'''
        return(message)

#This function returns XML String for RegisterTerminal request.
    def getRegisterTerminalRequestMessage(switchConnName, switchName, extension, password):
        message = '''<?xml version="1.0" encoding="utf-8"?>
<RegisterTerminalRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<device typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switchConnName+":"+switchName+''':0</device>
<loginInfo>
<forceLogin>true</forceLogin>
<sharedControl>false</sharedControl>
<password>''' + password + '''</password>
<mediaMode>SERVER</mediaMode>
<dependencyMode>MAIN</dependencyMode>
</loginInfo>
</RegisterTerminalRequest>
'''
        return(message)

#This function returns XML String for UnregegisterTerminal request.
    def getUnregisterTerminalRequestMessage(switchConnName, switchName, extension):
        message = '''<?xml version="1.0" encoding="utf-8"?>
<UnregisterTerminalRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<device typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switchConnName+":"+switchName+''':0</device>
<forceLogout>true</forceLogout>
</UnregisterTerminalRequest>
'''
        return(message)

#This function returns XML String for MakeCall request.
    def getMakeCallRequestMessage(switchConnName, switchName, calling, called):
        message = '''<MakeCall xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<callingDevice>''' + calling + ":" + switchConnName+":"+switchName+''':0</callingDevice>
<calledDirectoryNumber>''' + called + ":" + switchConnName+":"+switchName+''':0</calledDirectoryNumber>
<autoOriginate>doNotPrompt</autoOriginate
></MakeCall>
'''
        return(message)

    def getMakeCallRequestMessageWithDeviceId(callingDeviceId, calledDeviceId):
        message = '''<MakeCall xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<callingDevice>''' + callingDeviceId + '''</callingDevice>
<calledDirectoryNumber>''' + calledDeviceId + '''</calledDirectoryNumber>
<autoOriginate>doNotPrompt</autoOriginate
></MakeCall>
'''
        return(message)

#This function returns XML String for PlayMessage request.
    def getPlayMessageRequestMessage(extension, switchConnName, switchName, message, fileName):
        message='''<?xml version="1.0" encoding="utf-8"?>
<PlayMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http:// www.ecma-international.org/standards/ecma-323/csta/ed3">
<messageToBePlayed>'''+ message +'''</messageToBePlayed>
<overConnection>
<deviceID typeOfNumber="other" mediaClass="voice" bitRate="constant">''' + extension + ":" + switchConnName+":"+switchName+''':0</deviceID>
</overConnection>
<extensions>
<privateData>
<private><PlayMessagePrivateData><fileList>'''+ fileName +'''.wav</fileList>
</PlayMessagePrivateData></private>
</privateData>
</extensions>
</PlayMessage>
'''
        return(message)