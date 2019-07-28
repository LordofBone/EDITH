#thanks to https://www.w3resource.com/python-exercises/basic/python-basic-1-exercise-8.php

import bs4
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen

news_url="https://news.google.com/news/rss"
Client=urlopen(news_url)
xml_page=Client.read()
Client.close()

def getNews():
  newsOut = []
  
  soup_page=soup(xml_page,"xml")

  newsOut = [news.title.text for news in soup_page.find_all("item")]
    
  return newsOut

#if called direct then run the function
if __name__ == '__main__':
  theNews = getNews()
  for i in theNews:
    print (i)
