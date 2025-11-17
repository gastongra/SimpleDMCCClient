# SimpleDMCCClient

A Python client for interacting with Avaya AES (Application Enablement Services) via the XML DMCC API. This project demonstrates how to establish a secure connection, control devices, monitor events, and perform call operations using Avaya's DMCC protocol.

## Features
- Secure TLS connection to Avaya AES
- Start and stop application sessions
- Device registration and monitoring
- Make and control calls
- Play audio messages
- Graceful shutdown and error handling

## Project Structure
- `DmccClient.py`: Core client logic for DMCC protocol and AES communication
- `TestCall.py`: Example script to perform a test call and play a message
- `XMLMessages.py`: Generates required XML messages for DMCC operations
- `config.ini` / `config.ini.template`: Configuration for AES connection and extension
- `appsession.xml` / `appsession.xml.template`: XML template for starting an application session

## Requirements
- Python 3.x
- Avaya AES server with DMCC enabled

## Setup
1. Copy `config.ini.template` to `config.ini` and update with your AES server and extension details.
2. Copy `appsession.xml.template` to `appsession.xml` and update with your application credentials.
3. Install required Python packages (if any, e.g., `pip install -r requirements.txt`).

## Usage
Run the test call script:
```bash
python TestCall.py
```

## Configuration
Edit `config.ini` to set your AES server IP, port, hostname, switch name, and extension credentials.

## Notes
- The client uses TLS for secure communication. Certificate verification is disabled by default for simplicity.
- Logging is set to INFO level by default. Adjust as needed in the code.

## License
MIT License

## Disclaimer
This project is for educational and demonstration purposes. Use at your own risk.
