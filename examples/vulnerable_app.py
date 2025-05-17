"""
File: vulnerable_app.py

Description:
This file demonstrates high-risk vulnerabilities for testing Nuvai's engine.
All examples use built-in Python libraries only — no external dependencies.
"""

import os
import pickle
import logging
import hashlib
import urllib.request  # Replaces requests (standard library only)

DEBUG = True

password = "123456"
token = "abc.def.ghi"

user_input = input("Enter your command: ")
eval(user_input)

os.system(user_input)

file_path = "../../etc/passwd"
open(file_path, "r")

url = "https://example.com/" + user_input
try:
    urllib.request.urlopen(url)
except:
    pass

data = pickle.loads(user_input.encode())

hashed = hashlib.md5(password.encode()).hexdigest()

logging.info("Logging sensitive info: password=%s", password)
