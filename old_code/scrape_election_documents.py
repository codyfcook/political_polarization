from bs4 import BeautifulSoup
import requests 
import re 

temp_link = "http://www.presidency.ucsb.edu/ws/index.php?pid=90456"

def scrape_speech_text(link): 
	''' 
	This function takes in a link to the page with text for speech/statement/press and returns 
	just the relevant text 
	'''
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	text = soup.findAll("span", {"class":"displaytext"})
	text = re.sub('<[^>]+>', ' ', str(text[0]))
	text = re.sub("[\[].*?[\]]", " ", text) # random stage directions between [] sometimes
	text = text.decode('unicode_escape').encode('ascii','ignore')
	return text 

def scrape_speeches_on_page(link): 
	''' 
	Takes in link to the page with a table of |candidate -- date -- link| and returns a 
	dictionary of {date: text of link}
	'''
	rv = {}
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	cand_table = soup.findAll("table", {"width":"700", "border":"0", "align":"center"})	
	rows = cand_table[0].findAll("tr")
	rows = rows[1:]
	for row in rows:
		elems = row.findAll("td")
		link = "http://www.presidency.ucsb.edu" + elems[2].findAll("a", href=True)[0]['href'][2:]
		rv[elems[1].text] = scrape_speech_text(link)
	return rv 


def scrape_all_speeches(link): 
	''' 
	From main page linking to all candidates and their speeches, creates a dictionary with 
	keys for each candidate --> speech/statement/press --> date --> text. 
	''' 
	rv = {}
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	rows = soup.findAll("td", {"class":"doctext"})
	for row in rows: 
		elems = row.findAll("span")
		if len(elems) == 0: 
			continue
		candidate = elems[0].text
		rv[candidate] = {}
		links = row.findAll("a")
		for l in links: 
			link = "http://www.presidency.ucsb.edu/" + l['href']
			rv[candidate][l.text] = scrape_speeches_on_page(link)
	return rv


## MAIN ##
# ------ #

link = "http://www.presidency.ucsb.edu/2012_election.php"
d = scrape_all_speeches(link)
import cPickle as pickle 
pickle.dump(d, open("speeches.p", "wb"))


