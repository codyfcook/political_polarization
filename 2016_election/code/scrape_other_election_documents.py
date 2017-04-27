from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import cPickle as pickle
from custom_utilities import make_soup

'''
DESCRIPTION:
This script scrapes all other election documents for candidates, i.e. speeches,
statements, and press releases. It outputs a pickle file.
'''

## Constants ##
# Link to main page for 2016 documents
MAIN_LINK = "http://www.presidency.ucsb.edu/2016_election.php"


def get_links_to_documents_pages(link):
    '''
    Given the main link, traverses page and gets all links to the pages with
    statements, etc. on them. Stores in dictionary by candidate name
    '''
    rv = {}

    # Get soup for the main page and parse it into the rows
    soup = make_soup(link)
    rows = soup.findAll('td', {'class': 'doctext'})
    # Loop over rows
    for row in rows:
        elems = row.findAll("span")
        # if no span elements, is not a row with links
        if len(elems) != 0:
            candidate = elems[0].text
            rv[candidate] = {}
            links = row.findAll("a")
            for l in links:
                rv[candidate][l.text] = "http://www.presidency.ucsb.edu/" + l['href']
    return rv

def scrape_document_text(link):
    '''
    This function takes in a link to the page with text for speech/statement/press and returns
    just the relevant text
    '''
    soup = make_soup(link)
    text = soup.find("span", {"class":"displaytext"}).text
    return text

def get_text_of_individual_documents(link):
    '''
    Takes in link to the page with a table of |candidate -- date -- link| and returns a
    dictionary of {date: text of link}
    '''
    rv = {}
    soup = make_soup(link)
    # Find the table of links to individual documents and pull out the rows
    cand_table = soup.findAll("table", {"width":"700", "border":"0", "align":"center"})
    rows = cand_table[0].findAll("tr")
    rows = rows[1:]
    # For each row, find each column. Then scrape the text for the link in that row
    # and store in return dictionary
    for row in rows:
        elems = row.findAll("td")
        link = "http://www.presidency.ucsb.edu" + elems[2].findAll("a", href=True)[0]['href'][2:]
        rv[elems[1].text] = scrape_document_text(link)
    return rv


# ------------ #
#   MAIN       #
# ------------ #
if __name__ == "__main__" :
    rv = {}
    # From the main link, get links to documents for each candidate
    # Stores dict of candidate - document type - link to page of links
    links_to_document_pages = get_links_to_documents_pages(MAIN_LINK)
    # For each candidate-document_type, get the text of all actual documents
    for candidate in links_to_document_pages:
        print "Scraping for " + candidate + "..."
        rv[candidate] = {}
        for doc_type in links_to_document_pages[candidate]:
            rv[candidate][doc_type] = get_text_of_individual_documents(links_to_document_pages[candidate][doc_type])

    # Export to a pickle file
    pickle.dump(rv, open('../raw_data/other_election_documents_text.p', 'wb'))
