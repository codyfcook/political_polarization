from bs4 import BeautifulSoup
import requests
import re
import sys
from datetime import datetime
import cPickle as pickle
from custom_utilities import make_soup
sys.setrecursionlimit(10000)

'''
DESCRIPTION:
This script scrapes debate text and splits it by speaker, outputting a pickle file
Inputs are a list of ids for the links to the debates you want to scrape
'''

## Constants ##
# Debate links
BASE_LINK = 'http://www.presidency.ucsb.edu/ws/index.php?pid='
DEBATE_LINK_IDS = [76913, 76688, 76563, 76339, 76271, 76237, 76123, 76224, 76122, 76041, 75950, 75796, 76561, 75664,
                   75631, 75489, 75575, 75140, 74349, 76338, 76300, 62265, 29427, 76223, 29664, 76562, 76069, 76069,
                   75914, 75861, 75913, 75680, 75630, 75171, 74348, 74350, 63163, 72776, 72770, 29428]


def scrape_debate_text(soup):
    '''
    This function takes in a link to the page with text for debate and returns
    just the relevant text, with tags intact to be able to find speakers
    '''
    try:
        text = str(soup.find("span", {"class":"displaytext"}))
        text = re.sub("[\[].*?[\]]", " ", text) # stage directions between [] sometimes
        text = text.decode('unicode_escape').encode('ascii','ignore')
        return text
    except:
        print "ERROR IN SCRAPING TEXT"
        return ""

def get_date_for_debate(soup):
    '''
    Returns the debate (as datetime object) for the debate of a given soup page
    '''
    date_str = soup.find('span', {"class":"docdate"}).text
    date = datetime.strptime(date_str, "%B %d, %Y")
    return date

def split_text_by_speaker(debate_text):
    '''
    Takes in raw string of a speech and returns a dictionary where each key is someone who
    spoke at least once and maps to a list what they said each time they spoke
    '''
    rv = {}
    # There are some nested paragraphs that get missed by beautifulsoup. This fixes that
    debate_text = debate_text.replace('<p>', '</p><p>')
    # Turn back into soup to make easier to navigate. Find all paragraphs.
    debate_soup = BeautifulSoup(debate_text)
    paras = debate_soup.findAll("p")

    # Site uses <b></b> to denote speaker
    start_delim = ["<b>", "<i>"]
    text = ""
    name = ""
    # keep track of whether it's the first pass through loop
    first_run = True
    # Loop through all paragraphs and check if it is a new speaker
    for para in paras:
        para = str(para).strip()
        if para[3:6] in start_delim:
            end_delim = para[3]+"/"+para[4:6]
            if first_run == False:
                if name not in rv.keys():
                             rv[name] = ""
                text = re.sub('<[^>]+>', ' ', text)
                text = " ".join(text.split())
                rv[name] = rv[name] + " " + text
            try:
                name = para[6:para.index("</")]
                name = name.replace(".", "").strip().replace(":", "")
            except:
                continue
            text = para[para.index(end_delim)+4:]
            first_run = False
        else:
            if first_run!=True:
                text += para[3:-4]
    return rv


# ------------ #
#   MAIN       #
# ------------ #
if __name__=="__main__":
    rv = {}
    # Loop over all debate IDs listed above
    for debate_id in DEBATE_LINK_IDS:
        print "Scraping " + str(debate_id) + "..."
        # Constructe the link from the base and this debates ID
        link = BASE_LINK + str(debate_id)
        # Make soup and then get the text for that page split by speaker
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = scrape_debate_text(soup)
        split_text = split_text_by_speaker(text)
        # Pull the date
        date = get_date_for_debate(soup)
        # Store in the return dict, using date as the high level key
        rv[date] = split_text

    # Save as a pickle file
    pickle.dump(rv, open('../raw_data/debate_text.p', 'wb'))
