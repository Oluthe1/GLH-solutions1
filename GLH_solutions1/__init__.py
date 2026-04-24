"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = "secretkey123" 
DATABASE = "database.db"

import GLH_solutions1.views
