#!/usr/bin/python
import re
import sqlite3
import time
import urllib
import random

db = sqlite3.connect("phonebook.db")
db.isolation_level = None
db = db.cursor()

db.execute("SELECT number FROM phonebook WHERE number LIKE '3933%' AND status is null ORDER by number") # ORDER BY random() LIMIT 3000")
db.execute('select number from phonebook where number like "393%" and postcode not like "2%" and status is null')
rows = db.fetchall()
numbers = []
for row in rows:
    numbers.append( re.sub("^0", "39", row[0]) )

print ",".join(numbers) 
