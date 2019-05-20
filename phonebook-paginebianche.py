#!/usr/bin/python
import re
import sqlite3
import time
import urllib
import random

db = sqlite3.connect("phonebook.db")
db.isolation_level = None
db = db.cursor()

#db.executescript("DROP TABLE IF EXISTS phonebook;")
#db.executescript("DROP TABLE IF EXISTS urls;")

db.executescript("""
CREATE TABLE IF NOT EXISTS phonebook (
    id          INTEGER PRIMARY KEY,
    number      TEXT UNIQUE,
    name        TEXT,
    address     TEXT,
    city        TEXT,
    postcode    TEXT,
    url         TEXT,
    hlr         TEXT,
    status      TEXT
);
""")
db.executescript("""
CREATE TABLE IF NOT EXISTS urls (
    id          INTEGER PRIMARY KEY,
    url         TEXT UNIQUE
);
""")
sqlmapping = { "tel": "number", "org": "name", "locality": "city", "postal-code": "postcode", "street-address": "address" }


    

def geturl( query ):
    url = "http://paginebianche.it/execute.cgi"
    params = { "btt": 1, "mr": 30, "qs": query }
    url = url + "?" + urllib.urlencode(params)
    return url


def urlexists( url ):
    sql = "SELECT COUNT(*) FROM urls where url='"+url+"'"
    db.execute(sql)
    row = db.fetchone()[0]
    if row:
        print "URL Skipped: " + url
        return True
    else:
        return False


def loadpage( url ):
    print url
    webpage = urllib.urlopen( url )
    text = webpage.read()
    db.execute("INSERT OR IGNORE INTO urls ( url ) VALUES ( '"+url+"' )")
    return text


def scrape( text ):
    entries = re.findall("(<div[^>]*class=\"client-identifying-pg\".*?)<div class=\"identifying-data-action", text)
    rows = []
    for entry in entries:
        fields = {}
        tags = re.findall( r"<(\w+)[^>*]class=\"(\w+)\"[^>]*>(.*?)</\1", entry)
        for tag in tags:
            if sqlmapping.has_key(tag[1]):
                if tag[1] == "tel":
                    value = re.findall( "<li.*?(\d+\s*\d*\s*\d*\s*\d*).*?</li>", tag[2] )
                    value = re.findall( "^0", "39" ) # switch to 
                else: 
                    value = str( re.sub( "<[^>]*>|^\s*|\s*$", "", tag[2] ) )
                fields[sqlmapping[tag[1]]] = value
            
        if fields.has_key("number"):
            for number in fields["number"]:
                row = fields
                row["number"] = re.sub( "\D", "", number )
                rows.append(row)
    return rows


def dump( rows, url ):
    for row in rows:
        row["url"] = url
        print row
        sql = "INSERT OR REPLACE INTO phonebook ( " + ", ".join( row.keys() ) +  " ) VALUES ( ?" + ", ?" * (len(row)-1) + " )"
        try:
            db.execute( sql, row.values() )
        except:
            print "SQL Error:", sql, row



letters = map(chr, range(97, 123)) # a-z
letters = map(chr, range(97, 120)) # a-w
#letters.append(chr(32))            # space
for A in random.sample(letters,16): 
    for B in random.sample(letters,16): 
        for C in random.sample(letters,16): 
            for D in random.sample(letters,23): 
                url = geturl( C+A+D+D+B )
                if urlexists( url ) == False: 
                    text = loadpage( url )
                    rows = scrape( text )
                    dump( rows, url )

#letters = map(chr, range(97, 123)) # a-z
##letters.append(chr(32))            # space
#letters.reverse();
#for A in letters: 
#    for B in letters: 
#        for C in letters: 
#            url = geturl( A+B+C )
#            if urlexists( url ) == False: 
#                text = loadpage( url )
#                rows = scrape( text )
#                dump( rows, url )
