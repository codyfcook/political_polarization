from bs4 import BeautifulSoup
import requests 
import re 
import sys
import scrape_thomasLOC_links
import cPickle as pickle
sys.setrecursionlimit(4800)



def get_page_text(link): 
	''' 
	Given a link to a senate doc, returns relevant text on that get_page_text
	'''
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	text = soup.findAll("pre", {"class":"styled"})
	if len(text) != 1: 
		print "PROBLEM: " + str(link)
		return ""  

	text = re.sub('<[^>]+>', ' ', str(text[0]))
	text = re.sub("[\[].*?[\]]", " ", text)
	#text = text.replace("\n", "")
	return text

def create_text_dict(links_dict): 
	'''
	Given a dictionary of links to different senate/house docs, returns a dictionary 
	with the text on the page for each link
	'''
	rv = links_dict.copy()
	n = len(links_dict.keys())
	i = 1
	for key in links_dict.keys(): 
		print "Getting text for " + str(i) + " of " + str(n)
		i+=1 
		for key2 in links_dict[key].keys(): 
			try: 
				rv[key][key2]['raw_text'] = get_page_text(links_dict[key][key2]['link'])
			except: 
				print "Error scraping: " + links_dict[key][key2]['link']
				rv[key][key2]['raw_text'] = ""
	return rv


def is_starting_speaker(word): 
	word = word.strip()
	count_upper = sum(1 for lett in word if lett.isupper()) # less than 2 lowercase letter in word
	if "." == word[:-1]: 
		word = word[:-1]	
	if (len(word) - count_upper <= 1) and len(word)>=3: 
		return True
	else: 
		return False 

def find_all_names_in_text_dict(t_dict): 
	text_dict = t_dict.copy()
	all_names = [] 
	for key1 in text_dict: 
		for key2 in text_dict[key1]: 
			text = text_dict[key1][key2]['raw_text']
			words = text_dict[key1][key2]['raw_text'].split()
			for i in range(1, len(words)):
				if is_starting_speaker(words[i]) and (words[i-1] in ["Mr.", "Mrs.", "Ms.", "Dr."]): 
					text = text[text.find(words[i]):]
					name = words[i-1] + " " + text[:text.find(".")].strip()
					text = text[text.find("."):]
					#if name[-1]!=".": 
					#	name = name + "."
					for title in ["Messrs", "Mrs", "Mr", "Ms", "Dr"]: 
						if title in name[5:]: 
							name = ""
					if (name not in all_names) and (len(name.split())<3 or ("of" in name and len(name.split())<6)):
						all_names.append(name)
	#all_names += ["DeMINT", "UDALL of Colorado", "UDALL of New Mexico", "VICE PRESIDENT", 
	#			"NELSON of Florida", "NELSON of Nebraska", "JOHNSON of South Dakota", "JOHNSON of Wisconsin", 
	#			"BROWN of Ohio", "BROWN of Massachusetts", "McCAIN"]
	for i in range(len(all_names)): 
		all_names[i] = all_names[i]+"."
	all_names += ["PRESIDING OFFICER.", "ACTING PRESIDENT.", "SPEAKER.", "SPEAKER pro tempore.", "The Acting CHAIR.", "The Chair."]

	return [name for name in all_names if len(name)>3]









