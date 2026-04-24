"""
This script runs the GLH_solutions1 application using a development server.
"""

from os import environ
from GLH_solutions1 import app

if __name__ == '__main__':
    app.run(ssl_context = "adhoc")
