# Mobile Phone HLR Reverse Index Tracking

A mobile phone can be (poorly) tracked by scraping all a countries telephone directory 
address books and creating a bulk-API reverse HLR lookup table. 

Written in aid of the 2011 rescue of the stolen Sail Yacht Rocard from: 
Marinella Pier, Castelvetrano, Trapani, Sicily, Italy, Europe

<img src="https://imgs.xkcd.com/comics/regular_expressions.png"/>


## Data 

Decompress Data
```
unzip phonebook.*.zip
```

Search area included 151 cites
```
cat cities.txt  | wc -l
151
```

767,852 unique telephone number / address / HLR record combinations where scraped 
```
cat phonebook.dump.sql* | grep INSERT | wc -l  
767821
```

13,166 telephone numbers matching the format of a mobile phone 
```
cat numbers.* | perl -p -e 's/,/\n/g' | sort | uniq | wc -l
13166
```

20,196 unique HLR location codes where recorded  
```
cat report.* | wc -l
20196
```

Target was located on Couchsurf which reported the last login GeoIP location on the public profile.
Website was scraped on a polling interval and timestamped changes in location logged.
```
cat couchsurf-spider.csv | wc -l
78
```


## Code

### Webscrapers

These scripts spider the various online Italian phonebooks, 
use regular expressions to scrape out telephone numbers and addresses,
then insert these entries into an sqlite database. 

- [phonebook-paginebianche.py](phonebook-paginebianche.py)
- [phonebook-paginebianche2.py](phonebook-paginebianche2.py)
- [phonebook-pronto.py](phonebook-pronto.py)
- [phonebook-virgilio.py](phonebook-virgilio.py)


### API Scrapers

For each telephone number, lookup the HLR via an API and update the database

- [hlr-lookup.pl](hlr-lookup.pl)
- [hlr_read.py](hlr-lookup.pl) 


### CSV Dumpers

Turn the SQLite database into a textfile for export and easier grepping

- [csvdump.py](csvdump.py)
