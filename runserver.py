#!/usr/bin/env python
# -----------------------------------------------------------------------
# runserver.py
# Author: Wangari Karani, Roshaan Khalid
# -----------------------------------------------------------------------

import sys
from app import app, socketio  

def main():
    print("Starting the Flask-SocketIO application...")
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " port", file=sys.stderr)
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Port must be an integer.", file=sys.stderr)
        sys.exit(1)

    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print("Failed to start the server:", ex, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
