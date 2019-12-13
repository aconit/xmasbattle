"""
The flask application package.
"""

from flask import Flask, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

import Xmas2019.views
