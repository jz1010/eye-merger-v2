#!/usr/bin/env python3
from website import create_app
import os

#change this to pi ip address
host="192.168.86.37"

#don't change this port
port=5000

app = create_app()

if __name__ == '__main__':
    app.secret_key=os.urandom(12)
    app.run(host=host, port=port, debug=True)
