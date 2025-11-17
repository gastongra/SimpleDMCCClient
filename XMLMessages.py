class XMLMessages(object):
    @classmethod
    def get_start_app_session(cls):
        # Read the XML data from a file:
        f = open('appsession.xml', 'r')
        line = f.read()
        f.close()
        return line

    @classmethod
    def get_stop_application_session_message(cls, session_id):
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<StopApplicationSession xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<sessionID>''' + session_id + '''</sessionID>
<sessionEndReason>
<appEndReason>Application Request</appEndReason>
</sessionEndReason>
</StopApplicationSession>'''
        return message

    @classmethod
    def get_get_device_id_message(cls, switch_name, extension):
        message = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><GetDeviceId xmlns=\"http://www.avaya.com/csta\"><switchName>"+switch_name+"</switchName><extension>"+extension+"</extension></GetDeviceId>"
        return message

    @classmethod
    def get_monitor_start_message(cls, switch_conn_name, switch_name, extension):
        # mesage without physical device monitors:
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<MonitorStart xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
    <monitorObject>
        <deviceObject typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switch_conn_name+":"+switch_name+''':0</deviceObject>
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
        return message

    @classmethod
    def get_monitor_stop_message(cls):
        message = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<MonitorStop xmlns=\"http://www.avaya.com/csta\">
<monitorCrossRefID>1111111</monitorCrossRefID>
</MonitorStop>
'''
        return message

    @classmethod
    def get_snapshot_device_message(cls, switch_conn_name, switch_name, extension):
        '''#########################################################################
        message = <?xml version="1.0" encoding="utf-8"?>
<SnapshotDevice xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<snapshotObject>''' + extension + ":" + switch_conn_name + ":" + switch_name + ''':1</snapshotObject>
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
<snapshotObject>'''+extension+":" + switch_conn_name+":" + switch_name + ''':1</snapshotObject>
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
        return message

# This function returns XML String for RegisterTerminal request.
    @classmethod
    def get_register_terminal_request_message(cls, switch_conn_name, switch_name, extension, password):
        message = '''<?xml version="1.0" encoding="utf-8"?>
<RegisterTerminalRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<device typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switch_conn_name+":"+switch_name+''':0</device>
<loginInfo>
<forceLogin>true</forceLogin>
<sharedControl>false</sharedControl>
<password>''' + password + '''</password>
<mediaMode>SERVER</mediaMode>
<dependencyMode>MAIN</dependencyMode>
</loginInfo>
</RegisterTerminalRequest>
'''
        return message

# This function returns XML String for UnregisterTerminal request.
    @classmethod
    def get_unregister_terminal_request_message(cls, switch_conn_name, switch_name, extension):
        message = '''<?xml version="1.0" encoding="utf-8"?>
<UnregisterTerminalRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.avaya.com/csta">
<device typeOfNumber="other" mediaClass="notKnown">''' + extension + ":" + switch_conn_name+":"+switch_name+''':0</device>
<forceLogout>true</forceLogout>
</UnregisterTerminalRequest>
'''
        return message

# This function returns XML String for MakeCall request.
    @classmethod
    def get_make_call_request_message(cls, switch_conn_name, switch_name, calling, called):
        message = '''<MakeCall xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<callingDevice>''' + calling + ":" + switch_conn_name+":"+switch_name+''':0</callingDevice>
<calledDirectoryNumber>''' + called + ":" + switch_conn_name+":"+switch_name+''':0</calledDirectoryNumber>
<autoOriginate>doNotPrompt</autoOriginate
></MakeCall>
'''
        return message

    @classmethod
    def get_make_call_request_message_with_device_id(cls, calling_device_id, called_device_id):
        message = '''<MakeCall xmlns="http://www.ecma-international.org/standards/ecma-323/csta/ed3">
<callingDevice>''' + calling_device_id + '''</callingDevice>
<calledDirectoryNumber>''' + called_device_id + '''</calledDirectoryNumber>
<autoOriginate>doNotPrompt</autoOriginate
></MakeCall>
'''
        return message

# This function returns XML String for PlayMessage request.
    @classmethod
    def get_play_message_request_message(cls, extension, switch_conn_name, switch_name, message, file_name):
        message = '''<?xml version="1.0" encoding="utf-8"?>
<PlayMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http:// www.ecma-international.org/standards/ecma-323/csta/ed3">
<messageToBePlayed>''' + message + '''</messageToBePlayed>
<overConnection>
<deviceID typeOfNumber="other" mediaClass="voice" bitRate="constant">''' + extension + ":" + switch_conn_name+":"+switch_name+''':0</deviceID>
</overConnection>
<extensions>
<privateData>
<private><PlayMessagePrivateData><fileList>''' + file_name + '''.wav</fileList>
</PlayMessagePrivateData></private>
</privateData>
</extensions>
</PlayMessage>
'''
        return message
