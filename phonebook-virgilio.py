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
db.executescript("""
CREATE TABLE IF NOT EXISTS page_count (
    page_count  INT,
    url         TEXT UNIQUE
);
""")

def latin1_to_ascii (unicrap):
    """This replaces UNICODE Latin-1 characters with
    something equivalent in 7-bit ASCII. All characters in the standard
    7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
    accented letters are stripped of their accents. Most symbol characters
    are converted to something meaninful. Anything not converted is deleted.
    """
    xlate={ 0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A', 0xc6:'Ae', 0xc7:'C', 0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E', 0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I', 0xd0:'Th', 0xd1:'N', 0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
            0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U', 0xdd:'Y', 0xde:'th', 0xdf:'ss', 0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a', 0xe6:'ae', 0xe7:'c', 0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e', 0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
            0xf0:'th', 0xf1:'n', 0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o', 0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u', 0xfd:'y', 0xfe:'th', 0xff:'y', 0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}', 0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
            0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}', 0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}', 0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'", 0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}', 0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
            0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?', 0xd7:'*', 0xf7:'/' }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r


def geturl( city, query, index ):
    city  = re.sub( "\s+", "-", city.strip() ).lower();
    query = re.sub( "\s+", "+", query.strip() );
    url = "http://%s.virgilio.it/elencotelefonico?qs=%s&ofs=%s" % (city, query, index)
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
    cities = file.readlines()
    for city in cities:
        max = 25
        city = city.strip()
        letters = [letter for letter in string.ascii_lowercase]
        letters.insert(0, city)
        for letter in letters:
            url = geturl(city, letter, 1)
            for index in range( 1, get_result_count(url, city, letter, max)+1 ):
                url = geturl(city, letter, index)
                if not urlexists(url):
                    data = scrape(url, city)
                    db_insert(data, url)

def get_result_count( url, city, letter, max ):
    try:
        result = db.execute("SELECT page_count FROM page_count WHERE url = ?", (url,) )
        page_count = result.fetchone()
        page_count = page_count[0] if page_count and page_count[0] else 0
    except:
        page_count = 0

    if page_count == 0:
        webpage = urllib.urlopen( url )
        text = webpage.read()
        page_count = re.search('<span class="tpage">(\d+)\s+di\s+(\d+)</span>', text)
        if page_count and page_count.group(2):
            page_count = int(page_count.group(2))
            db.execute("INSERT INTO page_count (page_count, url) VALUES (?,?)", (page_count,url,) )
        else:
            page_count = 1

    print "\n\n" + "-"*40 + "\n%s (%s) has %s pages" % (city, letter, page_count) + "\n" + "-"*40 + "\n" 
    page_count = max if page_count > max else page_count
    return page_count;

def scrape(url, city):
    print url
    webpage = urllib.urlopen( url )
    
    text = webpage.read()
    text = latin1_to_ascii(text)
    
    data = []
    snippits = re.findall('<div[^>]*class="scheda.*?<form', text, re.S);
    empty = re.search("()", "")
    for snippit in snippits:
        fields = {}
        fields["name"]    = string.capwords( (re.search('<h3>\s*<a[^>]*>(.*?)</a>', snippit, re.S) or empty).group(1).strip() )
        fields["address"] = "" 
        fields["number"]  = ""

        paras = re.findall('<p>(.*?)</p>', snippit, re.S)
        while len(paras) > 0:
            para = paras.pop()
            if re.search(":\s<strong>[\s\d]*</strong>", para, re.S):
                fields["number"]  = re.sub( "^0", "39", re.sub( "\D", "", para))
                fields["address"] = re.sub( "<[^>]*>", "", paras.pop() )
                break

        match = re.search('-\s*(\d+)\s*([^()]*)', fields["address"], re.S)
        fields["postcode"] = match.group(1).strip() if match and match.group(1) else ""
        fields["city"]     = string.capwords( match.group(2).strip() if match and match.group(2) else city ) 
        fields["url"]      = url

        if fields["number"]:
            data.append(fields)
            print fields
        else:
            print "ERROR: ", fields
    return data

def db_insert(data, url):                                                                                                       
    for fields in data:
        try:
            tuple = ( fields["number"], fields["name"], fields["address"], fields["city"], fields["postcode"], fields["url"] )
            db.execute( "INSERT OR IGNORE INTO phonebook ( number, name, address, city, postcode, url) VALUES ( ?, ?, ?, ?, ?, ? )", tuple)
        except:
            print "SQL Error", fields

    if len(data) > 0:
        db.execute("INSERT OR IGNORE INTO urls ( url ) VALUES ( ? )", (url,) )

loopcities()

