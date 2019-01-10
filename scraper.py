#!/usr/bin/python3

import argparse
import logging
import json
from requests import get
from bs4 import BeautifulSoup as soup

#clear logfile
with open('debug.log','w') as f:
  pass

EMAIL_CRED_FILEPATH = "./data/emailcreds.json"
LOGGER_LEVEL = logging.DEBUG

manga_data = {
              'bnh':  {'base_url':'https://w10.readheroacademia.com/',
                       'most_recent_ep_url':'',
                       'full_name':'Boku No Hero',
                       'alternate_name':'My Hero Academia'},
              'bc':   {'base_url':'https://blackclovermanga.com/',
                       'most_recent_ep_url':'',
                       'full_name':'Black Clover',
                       'alternate_name':''}
              }


logging.basicConfig(filename='debug.log',level=LOGGER_LEVEL)

def get_volumes(code,latest_only=False,starting_at=0):

  logging.info("entering get_volumes")
  logging.debug("args are latest_only={},starting_at={}".format(latest_only,starting_at))

  #get source of page with episode links
  homepage_data = soup(get(manga_data[code]['base_url'])._content, 'html.parser')
  #find the main table where the episode list is structured
  table = homepage_data.find('table')
  #get the link tags of the table
  def volume_pattern_match(tag):
    if tag.name == 'a':
      if tag.contents[0].strip().split()[-1].isdigit():
        if int(tag.contents[0].strip().split()[-1]) > starting_at:
          return True
    return False

  volumes = table.find_all(volume_pattern_match)

  logging.debug("returning {} volume".format("latest" if latest_only else "every"))
  logging.info("leaving get_volumes")

  return volumes[0] if latest_only else volumes

def isBookmark(url):

  logging.info("checking if page is bookmark")

  logging.debug("getting page data")
  volume_page_data = soup(get(url['href'])._content, 'html.parser')
  logging.debug("got page data")

  #every page has entry-content block, only bookmark page has h2
  bookmark_block = volume_page_data.find('div','entry-content').h2

  logging.info("page {} a bookmark".format("is" if bool(bookmark_block) else "is not"))
  #variable will have a value i.e. be True if it's a bookmark
  return bool(bookmark_block)

def getEmailCreds(credfile):
  logging.info("retrieving email creds")

  creds = json.load(open(credfile,'r'))

  logging.info("successfully retrieved email creds")

  return creds['email'],creds['password']

if __name__ == "__main__":
  #init parser
  parser = argparse.ArgumentParser()

  #add args
  parser.add_argument("code",help="code of manga, e.g. bnh-Boku No Hero")
  parser.add_argument("--volume","--v",help="last volume of said manga you've read", type=int)
  parser.add_argument("--latestonly",help="get only the latest volume of the specified manga",action="store_true")
  args = parser.parse_args()

  email,password = getEmailCreds(EMAIL_CRED_FILEPATH)

  #get only the latest volume
  if args.latestonly:
    logging.info("returning latest volume only")

    latest_volume = get_volumes(args.code,latest_only=True)
    isBookmark(latest_volume)

    logging.info("got all latest volume only")

  #get all volumes
  elif args.volume is None:
    logging.info("returning all volumes from start to finish")

    all_volumes = get_volumes(args.code)

    logging.info("got all volumes from start to finish")

  #get all volumes from specified to current
  else:
    logging.info("returning all volumes from first to finish")

    #get list of volumes for this manga
    volumes = get_volumes(args.code, starting_at = args.volume)

    logging.info("got all volumes from first to finish")