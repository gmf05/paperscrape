# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 18:21:07 2016

@author: gmf
"""

# paper_scraper.py

# Import modules
import sys
import re
import requests
import numpy as np
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

reload(sys)  
sys.setdefaultencoding('utf8')

pause_secs = 3
driver = webdriver.Chrome()

# Convert list text to year, author, title segments
def preprocess_text(list_text):
  # PRE-PROCESSING: DROP TROUBLESOME CHARS, PARSE FORMATTING
  parse_text = re.findall('(.+?)[.,]', list_text)
  parse_text = [p.encode('ascii','ignore') for p in parse_text]
  # keep only text >= 3 chars besides \ \,
  long_idx = np.where([len(p.translate(None, '&,;:.? '))>=3 for p in parse_text])[0]
  parse_text = [parse_text[i].translate(None,'&,.;:?').strip() for i in long_idx]
  
  # YEAR
  try:  
    #paper_year = re.findall("\(\d{4}\)",list_text)[0].translate(None,'()')
    try:    
      year_idx = np.where([bool(re.findall('\(\d{4}\)', p)) for p in parse_text])[0]
      paper_year = re.search('\(?\d{4}\)', parse_text[year_idx]).group().translate(None,'()')
    except:
      year_idx = np.where([bool(re.findall('\d{4}', p)) for p in parse_text])[0][0]
      paper_year = re.search('\d{4}', parse_text[year_idx]).group()
  except:
    paper_year = ''

  for p in parse_text[1::]:
    if p.find(paper_year)>=0:
      parse_text.remove(p)
  
  # TITLE
  # longest one is title
  # anything before that is authors
  title_idx = np.argmax([len(p.translate(None, '&,;:.? ')) for p in parse_text])
  paper_title = parse_text[title_idx].lower()
  # cut title to ten words  
  sp =  paper_title.split(' ')
  if len(sp)>10:
    paper_title = ' '.join(paper_title.split(' ')[0:10])

  
  # AUTHORS
  if title_idx>1:
    paper_authors = ', '.join(parse_text[0:title_idx])
  else:
    paper_authors = parse_text[0]

  
  #print paper_num,paper_year, paper_title, paper_authors
  return paper_title, paper_authors, paper_year

# Part 1: Search
def part1(search_text):
  # Search for text
  driver.get('http://scholar.google.com')
  elem = driver.find_element_by_name("q")
  elem.clear()
  elem.send_keys(search_text)
  elem.send_keys(Keys.RETURN)
  
# Part 2: Click "All versions", if possible
def part2():
  try:
    elem2 = driver.find_elements_by_partial_link_text('versions')
    elem2[0].click()
  except:
    0

# Part 3: Find link to PDF, if available
def part3(search_text):
  # Get all [PDF] button links
  links = driver.find_elements_by_tag_name('a')
  possible = []
  for url in links:
    if url.get_attribute('href') and url.get_attribute('href')[-4::]=='.pdf':
     if url.text.lower().find(search_text):
       possible.append(url.get_attribute('href'))
  
  is_saved = False
  if any(possible):
    # 
    i=0
    do_loop = True
    while do_loop:
      try:
        url = possible[i]
        response = requests.get(url)
        with open('/home/gmf/Documents/BU/Thesis/refs/scraper/' + search_text + '.pdf', 'wb') as f:
          f.write(response.content)
        is_saved = True
        do_loop = False
        print 'Succeess'
      except:
        i+=1
        if i>=len(possible):
          do_loop = False
    
  if not is_saved:
    print 'Failed'

  print ''

def main():
  
  #papers = open('paper_list.txt','rb').readlines()
  papers = open(sys.argv[1],'rb').readlines()
  papers = papers[0::2] # skip empty lines every other

  for paper_num,list_text in enumerate(papers):
    paper_title,paper_authors,paper_year = preprocess_text(list_text)
    print str(paper_num) + ' ' + paper_year + ' ' + paper_authors + ' ' + paper_title
    search_text = str.lower(paper_title + ' ' + paper_year)
    part1(search_text)
    plt.pause(pause_secs)
    part2()
    plt.pause(pause_secs)
    part3(search_text)

if __name__=='__main__':
    main()
