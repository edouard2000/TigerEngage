#!/usr/bin/env python
# -----------------------------------------------------------------------
# runserver.py
# Author: Wangari Karani, Roshaan Khalid
# -----------------------------------------------------------------------

import sys
import logging
from app import app, socketio  

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    
    if len(sys.argv) != 2:
        logging.error("Usage: " + sys.argv[0] + " port")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        logging.error("Port must be an integer.")
        sys.exit(1)

    try:
        logging.info("Starting the Flask-SocketIO application...")
        socketio.run(app, host='localhost', port=port, debug=True)
    except Exception as ex:
        logging.error("Failed to start the server: %s", ex)
        sys.exit(1)

if __name__ == "__main__":
    main()
