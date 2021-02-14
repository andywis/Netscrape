# Netscrape
A library that helps you automate reading something from a website

## Description

The Netscraper is a Python library that helps you automate reading
something from a website, where submitting forms is necessary.

The original purpose was to read what day the garden waste wil be collected
from my driveway. Find out my collection day, I have to enter my postcode,
hit "submit", choose my address and hit "submit" again. There was no way
I could save the page as a bookmark. So I wrote this library to do it for me.

It uses the "requests" library to fetch web pages and post the form, and
the "BeautifulSoup" library to interrogate the HTML.


To use this library, it is useful to have a basic knowledge of the
'requests' library and the 'BeautifulSoup' (or 'bs4') library.

https://requests.readthedocs.io/en/master/index.html

https://www.crummy.com/software/BeautifulSoup/bs4/doc/

The name of this library is based on the cheeky name we gave to the old web
browser that we all loved in the earlier days of the World Wide Web.


## Installation
```
python3 -m venv ./venv
./venv/bin/activate
pip install requests bs4


```

N.B. on a Raspberry Pi, you probably need to "apt install lxml"
before you can use 'bs4'
