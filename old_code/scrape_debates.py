from bs4 import BeautifulSoup
import requests
import re
import sys
sys.setrecursionlimit(10000)

def scrape_debate_text(link):
	'''
	This function takes in a link to the page with text for debate and returns
	just the relevant text, with tags intact to be able to find
	'''
	try:
		response = requests.get(link)
		soup = BeautifulSoup(response.content, "html.parser")
		text = soup.findAll("span", {"class":"displaytext"})
		# Weird case where it truncates early, have to do a more hack-job scraping
		text = str(text[0])
		if len(text) < 1000:
			text = str(soup)
			text = text[text.index('''<span class="displaytext">''') + len('''<span class="displaytext">'''):text.index('''</span><hr noshade="noshade" size="1">''')]
		text = re.sub("[\[].*?[\]]", " ", text) # random stage directions between [] sometimes
		text = text.decode('unicode_escape').encode('ascii','ignore')
		return text
	except:
		print "ERROR IN SCRAPING TEXT:  " + str(link)
		return ""

def split_text_by_speaker(debate_text):
	'''
	Takes in raw string of a speech and returns a dictionary where each key is someone who
	spoke at least once and maps to a list what they said each time they spoke
	'''
	rv = {}
	debate_soup = BeautifulSoup(debate_text)
	paras = debate_soup.findAll("p")

	# Sometimes they use <b>, sometimes <i> to denote speaker. This finds out which is used
	all_bs = debate_soup.findAll("b")
	all_is = debate_soup.findAll("i")
	if len(all_bs)>(len(all_is)-50):
		start_delim = "<b>"
		end_delim = "</b>"
	elif len(all_bs)<=(len(all_is)-50):
		start_delim = "<i>"
		end_delim = "</i>"

	text = ""
	name = ""
	first_run = True
	for para in paras:
		para = str(para).strip()
		if para[3:6]==start_delim:
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
			first_run=False
		else:
			if first_run!=True:
				text += para[3:-4]
	return rv


def scrape_all_debates(link):
	'''
	Takes in link to main debates page, returns dictionary with keys
	debate -> date -> speaker, .. -> text
	'''
	rv = {}
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	t = soup.findAll("table", {"width":"700", "bgcolor":"#FFFFFF"})[0]
	rows = t.findAll("tr")
	for row in rows:
		date = row.findAll("td", {"class":"docdate"})
		if len(date)==0:
			continue
		date = date[0].text.strip()
		try:
			year = int(date[-4:])
		except:
			continue

		if int(year)<2010:
			continue

		doctext = row.findAll("td", {"class":"doctext"})
		title = doctext[0].text
		try:
			link = doctext[0].findAll("a")[0]['href']
		except:
			continue

		print "Scraping debate from: " + date
		text = scrape_debate_text(link)
		speaker_dict = split_text_by_speaker(text)
		rv[date] = {}
		rv[date]['speakers'] = speaker_dict
		rv[date]['debate_title'] = title

	return rv



# MAIN #
# ---- #

link = "http://www.presidency.ucsb.edu/debates.php"
d = scrape_all_debates(link)

# The debates that used italics to identify speakers also picked up topic headings. Clean those out
oct_3_keys = ['Mr Romney', 'Gov Romney', 'Republican Presidential Nominee W Mitt Romney', 'The President']
oct_22_keys = ['Republican Presidential Nominee W Mitt Romney',  'Gov Romney', 'The President']
oct_16_keys = ['Mr Romney',  'Gov Romney',  'The President']

for key in d['October 16th, 2012']['speakers'].keys():
	if key not in oct_16_keys:
		d['October 16th, 2012']['speakers'].pop(key, None)
for key in d['October 22nd, 2012']['speakers'].keys():
	if key not in oct_22_keys:
		d['October 22nd, 2012']['speakers'].pop(key, None)
for key in d['October 3rd, 2012']['speakers'].keys():
	if key not in oct_3_keys:
		d['October 3rd, 2012']['speakers'].pop(key, None)


import cPickle as pickle





#for key in d.keys():
#	print d[key]['speakers'].keys()
#	print key

