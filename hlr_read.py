#!/usr/bin/python
import re
import sqlite3
import sys

db = sqlite3.connect("phonebook.db")
db.isolation_level = None
db = db.cursor()

# "Number","Date","Time","MCC","MNC","Delivery date","Delivery time","IMSI","MSC","Status","Operator name","Operator country","Price"
line = sys.stdin.readline()
key = [ item.strip('"') for item in line.split(",") ]
print key

OK = 0
invalid = 0
rejected = 0
for line in sys.stdin.readlines():
    fields = [ item.strip('"') for item in line.split(",") ]
    values = {}
    for i in range(len(fields)):
        values[ key[i] ] = fields[i]

    if len( re.findall("REJECTED", values["Status"]) ) == 0:
        sql = "UPDATE OR ABORT phonebook SET hlr=?, status=? WHERE number=?"
        sql_values = ( values["MSC"], values["Status"], values["Number"] );
        print sql, sql_values
        db.execute( sql, sql_values )
        if values["Status"] == "OK":
            OK = OK + 1
        else:
            invalid = invalid + 1
    else:
        print "REJECTED: ", sql_values 
        rejected = rejected + 1

print
print "-"*30
print
print "OK:       %s" % OK
print "INVALID:  %s" % invalid
print "REJECTED: %s" % rejected
