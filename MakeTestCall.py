import sys
import configparser
import DmccClient
import XMLMessages
from time import sleep


def graceful_shutdown(dmcc_client):
    DmccClient.logging.info('Graceful shutdown initiated ...')
    dmcc_client.set_all_done()
    sleep(5)
    dmcc_client.get_conn().close()
    DmccClient.logging.info('Graceful shutdown completed.')


def main():
    """
Log Level   When it’s used
=========   ===========================================================================
DEBUG		Detailed information, typically of interest only when diagnosing problems.
INFO		Confirmation that things are working as expected.
WARNING		An indication that something unexpected happened, or indicative of some problem in the near future
            (e.g. ‘disk space low’). The software is still working as expected.
ERROR		Due to a more serious problem, the software has not been able to perform some function.
CRITICAL	A serious error, indicating that the program itself may be unable to continue running.
"""
    DmccClient.logging.basicConfig(level=DmccClient.logging.INFO,
                                   format='%(asctime)s|%(levelname)s|%(relativeCreated)6d|%(threadName)s|%(message)s')
    # read config.ini
    # ip = '10.133.93.73' #AES server´s IP address
    # port = 4722 #Secure DMCC service´s port
    # hostname = "linpubad073.gl.avaya.com" #AES server´s FQDN
    # switch_conn_name = "CM" #switch connection name as configured in the AES server´s switch connections section
    # switch_name = "10.133.93.66" #IP address or FQDN of the CM server
    # extension = "1903"
    # password = "123456"
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    ip = cfg.get('AES', 'ip')
    port = int(cfg.get('AES', 'port'))
    hostname = cfg.get('AES', 'hostname')
    switch_conn_name = cfg.get('AES', 'switch_conn_name')
    switch_name = cfg.get('AES', 'switch_name')
    extension = cfg.get('DialingExtension', 'extension')
    password = cfg.get('DialingExtension', 'password')

    DmccClient.logging.info("Welcome! We will attempt to establish a DMCC session to AES over XML to make some calls.")
    DmccClient.logging.info("opening secure connection to DMCC server")

    # Any DMCC client must perform below actions to do 1st party call control:
    # 1. Start Application Session
    # 2. GetDeviceId
    # 3. MonitorStart
    # 4. RegisterTerminal
    #
    # So here we go:

    dmcc_client = None
    try:
        # connect to AES
        dmcc_client = DmccClient.DmccClient(ip, port, hostname)

        # create DMCC session
        dmcc_client.send_request(XMLMessages.XMLMessages.get_start_app_session(), '0001')
        session_id = dmcc_client.handle_start_app_session_response('0001', 5)
        DmccClient.logging.info('Session created. Session ID is: ' + session_id)

        # send GetDeviceId for the extension we´re controlling
        dmcc_client.send_request(XMLMessages.XMLMessages.get_get_device_id_message(switch_name, extension), '0002')
        my_device_id = dmcc_client.handle_get_device_id_response('0002', 5)

        # Start a monitor on the controlled device
        dmcc_client.send_request(XMLMessages.XMLMessages.get_monitor_start_message(switch_conn_name, switch_name,
                                                                                   extension),
                                 '0003')
        monitor_cross_ref_id = dmcc_client.handle_monitor_start_response('0003', 5)
        DmccClient.logging.info('Device Id: ' + my_device_id + ' monitor_cross_ref_id: ' + str(monitor_cross_ref_id))

        # Register controlled device
        dmcc_client.send_request(XMLMessages.XMLMessages.get_register_terminal_request_message(switch_conn_name,
                                                                            switch_name, extension, password), '0005')
        reg_terminal_response = dmcc_client.handle_register_terminal_response('0005', 60)
        DmccClient.logging.info('RegisterTerminal Response Code:' + str(reg_terminal_response))

        # send GetDeviceId for the extension we´re calling
        dmcc_client.send_request(XMLMessages.XMLMessages.get_get_device_id_message(switch_name, '3301'), '0009')
        called_device_id = dmcc_client.handle_get_device_id_response('0009', 5)

        # Make a call!
        dmcc_client.send_request(XMLMessages.XMLMessages.get_make_call_request_message_with_device_id(my_device_id,
                                                                                        called_device_id), '0012')
        call_id = dmcc_client.handle_make_call_response('0012', 5)
        DmccClient.logging.info('MakeCall initiated. Call ID:' + str(call_id))

        # If call was answered, move on with the test. Otherwise raise an ugly exception
        call_established = dmcc_client.wait_for_established_event(call_id, 20)
        if call_established:
            DmccClient.logging.info('Call established.')
        else:
            raise DmccClient.DMCCEventTimeoutError("DMCCEventTimeoutError. CallEstablished event not received ")

        # Call was answered, so play a message:
        message = '0'
        file_name = '0001'
        DmccClient.logging.info('audio start')
        dmcc_client.send_request(XMLMessages.XMLMessages.get_play_message_request_message(extension, switch_conn_name,
                                                                             switch_name, message, file_name), '0020')
        dmcc_client.handle_play_message_response('0020', 5)
        audio_stop = dmcc_client.wait_for_audio_stop_event(monitor_cross_ref_id, 60)
        if audio_stop:
            DmccClient.logging.info('audio stop')
        else:
            raise DmccClient.DMCCEventTimeoutError("DMCCEventTimeoutError. AudioStopEvent not received ")

    except (DmccClient.DMCCSessionError, DmccClient.DMCCResponseMissing, DmccClient.DMCCGetDeviceIdError,
            DmccClient.DMCCMonitorStartError, DmccClient.DMCCRegisterTerminalError, DmccClient.DMCCMakeCallError,
            DmccClient.DMCCEventTimeoutError, DmccClient.DMCCPlayMessageError) as e:
        DmccClient.logging.info(str(e) + " Goodbye :(")
        graceful_shutdown(dmcc_client)
        sys.exit() 
    except Exception as e:
        DmccClient.logging.info(str(e) + " exception. Goodbye :(")
        graceful_shutdown(dmcc_client) 
        raise
    finally:
        pass

    dmcc_client.send_request(XMLMessages.XMLMessages.get_unregister_terminal_request_message(switch_conn_name,
                                                                                    switch_name, extension), '0030')
    DmccClient.logging.debug(dmcc_client.read_response('0030', 5))
    DmccClient.logging.info('station unregistered')

    dmcc_client.send_request(XMLMessages.XMLMessages.get_monitor_stop_message(), '0040')
    DmccClient.logging.debug(dmcc_client.read_response('0040', 5))
    DmccClient.logging.info('monitor stopped')
    sleep(1)

    dmcc_client.send_request(XMLMessages.XMLMessages.get_stop_application_session_message(session_id), '0050')
    sleep(1)
    
    graceful_shutdown(dmcc_client)


if __name__ == '__main__':
    main()
