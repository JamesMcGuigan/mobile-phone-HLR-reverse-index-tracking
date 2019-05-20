#!/usr/bin/python
import re
import sqlite3
import time
import urllib
import random
import string

db = sqlite3.connect("phonebook.db")
db.isolation_level = None
db = db.cursor()

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


def geturl( city, index ):         
    url = "http://www.pronto.it/?q="+urllib.quote_plus(city)+","+str(index);
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

def loopcities():
    file = open("cities.txt", "r")
    cities = file.readlines();
    for city in cities:
        city = city.strip()
        for index in range(1, 22):
            url = geturl(city, index)
            if not urlexists(url):
                data = scrape(url, city)
                db_insert( data, url )
                time.sleep(1)


def scrape(url, city):
    print url
    webpage = urllib.urlopen( url )
    
    text = webpage.read()
    data = []
    empty = re.search("()", "")
    snippits = re.findall('<div[^>]*class="row_normal.*?<div class="action_icons', text, re.S);
    for snippit in snippits:
        fields = {}
        fields["name"]     = string.capwords( (re.search('<span[^>]*class="cognome[^>]*>(.*?)</span>', snippit, re.S) or empty).group(1).strip() ) 
        fields["address"]  = string.capwords( (re.search('<span[^>]*class="via[^>]*>(.*?)</span>', snippit, re.S) or empty).group(1).strip() )
        fields["number"]   = (re.search('^.*?<div[^>]*id="(\d*)', snippit, re.S) or empty).group(1).strip()
        fields["number"]   = re.sub('^0', '39', fields["number"])
        
        match = re.search('-\s*(\d+)\s*([^()]*)', fields["address"], re.S)
        fields["postcode"] = match.group(1).strip() if match else ""
        fields["city"]     = string.capwords( match.group(2).strip() ) if match else city
        fields["url"]      = url

        data.append(fields)
        print fields
    return data

def db_insert(data, url):                                                                                                       
    for fields in data:                                                                                                                                                                                    
        tuple = ( fields["number"], fields["name"], fields["address"], fields["city"], fields["postcode"], fields["url"] )
        db.execute( "INSERT OR IGNORE INTO phonebook ( number, name, address, city, postcode, url) VALUES ( ?, ?, ?, ?, ?, ? )", tuple)
    
    if len(data) > 0:
        db.execute("INSERT OR IGNORE INTO urls ( url ) VALUES ( ? )", (url,) )

loopcities()
