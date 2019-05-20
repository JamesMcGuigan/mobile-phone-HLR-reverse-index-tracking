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


def geturl( query, index ):
    query = re.sub("\+", " ", query)
    url = "http://paginebianche.it/execute.cgi"
    params = { "btt": 1, "mr": 30, "be": index*30, "qs": query }
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

def loopcities():
    file = open("cities.txt", "r")
    cities = file.readlines()
    cities = [ i[0] for i in db.execute('SELECT DISTINCT substr(url, 46, 3) FROM phonebook WHERE url LIKE "%pagine%qs=___&%" ORDER BY random()').fetchall() ]
    cities = [ url[0] for url in db.execute('SELECT DISTINCT url FROM phonebook WHERE url LIKE "%pagine%qs=%" and postcode is null and status is not null ORDER BY random()').fetchall() ]

    for city in cities:
        max = 250
        city = city.strip()
        #url = geturl(city, 1)
        #result_count = get_result_count(url, city, max)
        result_count = 1
        for index in range( 1, result_count+1 ):
            #url = geturl(city, index)
            url = city
            #if not urlexists(url):
            data = scrape(url, city)
            db_insert(data, url)

def get_result_count( url, city, max ):
    try:
        result = db.execute("SELECT page_count FROM page_count WHERE url = ?", (url,) )
        page_count = result.fetchone()
        page_count = page_count[0] if page_count and page_count[0] else 0
    except:
        page_count = 0

    if page_count == 0:
        webpage = urllib.urlopen( url )
        text = webpage.read()

        try:
            page_count = re.findall('<p class="pagination-total">.*?</p>', text, re.S)
            page_count = re.search("\d+.*?di.*?(\d+)", page_count[0], re.S)
            page_count = int(page_count.group(1))
            db.execute("INSERT INTO page_count (page_count, url) VALUES (?,?)", (page_count,url,) )
        except:
            page_count = -1

    print "\n\n" + "-"*40 + "\n%s has %s pages" % (city, page_count) + "\n" + "-"*40 + "\n" 
    page_count = max if page_count > max else page_count
    return page_count;

def scrape(url, city):
    print url
    webpage = urllib.urlopen( url )
    text = webpage.read()
    text = latin1_to_ascii(text)
    
    sqlmapping = { "tel": "number", "org": "name", "locality": "city", "postal-code": "postcode", "street-address": "address" }
    
    rows = []
    entries = re.findall("(<div[^>]*class=\"client-identifying-pg\".*?)<div class=\"identifying-data-action", text, re.S)
    for entry in entries:
        fields = { "url":url, "number": "", "city":"", "postcode":"", "name":"", "address":"", }
        keys = "|".join( sqlmapping.keys() )
        tags = re.findall( r'<(\w+)[^>*]class="(%s)"[^>]*>(.*?)</\1' % keys, entry, re.S)
        for tag in tags:
            if sqlmapping.has_key(tag[1]):
                if tag[1] == "tel":
                    value = re.findall( "<li>(.*?)</li>", tag[2], re.S )
                else: 
                    value = str( re.sub( "<[^>]*>", "", tag[2].strip() ) )
                fields[sqlmapping[tag[1]]] = value
            
        if fields.has_key("number"):
            for number in fields["number"]:
                row = fields
                row["number"] = re.sub( "\D", "", number )
                row["number"] = re.sub( "^0", "39", row["number"] )
                if row["number"]:
                    rows.append(row)
                    print row
                else:
                    print "ERROR: ", row
    return rows


def db_insert(data, url):
    count = 0
    for fields in data:
        tuple = ( fields["number"], fields["name"], fields["address"], fields["city"], fields["postcode"], fields["url"] )
        try:
            #db.execute( "INSERT OR IGNORE INTO phonebook ( number, name, address, city, postcode, url) VALUES ( ?, ?, ?, ?, ?, ? )", tuple)
            db.execute( "UPDATE phonebook SET number = ?, name = ?, address = ?, city = ?, postcode = ?, url = ? WHERE number = '%s'" % fields["number"], tuple)
            count = count + 1
        except:
            print "SQL Error", fields

    if len(data) > 0 and count > 0:
        db.execute("INSERT OR IGNORE INTO urls ( url ) VALUES ( ? )", (url,) )

loopcities()

