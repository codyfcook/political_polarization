from bs4 import BeautifulSoup
import requests 
import re 
import sys
import scrape_thomasLOC 
import cPickle as pickle
import scrape_thomasLOC
sys.setrecursionlimit(4800)


def clean_text(text_dict): 
	''' 
	Does a few things to clean all raw text. Removes any long quotes (like bills printed for the Record), 
	gets ride of some text markups, removes things between []'s, etc
	''' 
	rv = text_dict.copy()
	for date in rv: 
		for title in rv[date]: 
			if 'raw_text' in rv[date][title]:
				text = rv[date][title]['raw_text']
				# removes long, tabbed in sections
				text = re.sub(r'   .*\n', '', text)
				text = re.sub(r'      .*\n', '', text)
				text = re.sub(r'Sec.*\n', '', text)
				# Remove things in [ ]'s and replace \ns with a space
				regex = re.compile('\[.+?\]')
				text = regex.sub('', text.replace("\n", " "))
				# Remove a few other miscellaneous seperators 
				text = re.sub(",|-|'|`|\(|\)|\[|\]|:|;", " ", text)
				text = re.sub(' +',' ', text)
				# Remove any roll call votes
				if "AYES" in text:
					text = text[:text.find("AYES")]
				if "YEAS" in rv[date][title]['raw_text']:
					text = text[:text.find("YEAS")]
				rv[date][title]['raw_text'] = text 
	return rv 


def split_by_speaker(txt, speakers):
	'''
	Given raw text and a list of separators (generally possible speaker names), splits based 
	on those names and returns a dictionary of text attributable to that name 
	'''
	rv = {}
	speakers_re = re.compile('(' + '|'.join([re.escape(s) for s in speakers]) + ')')
	s = speakers_re.split(txt)
	s = [x.strip() for x in s]
	for i in range(len(s)-1): 
		if s[i] in speakers and s[i+1] not in speakers:
			if "unanimous consent" in s[i+1]: 
				continue 
			if s[i+1][-3:]=="Ms." or s[i+1][-3:]=="The" or s[i+1][-3:]=="Mr.":
				s[i+1] = s[i+1][:-3].strip()
			if s[i+1][-4:]=="Mrs.":
				s[i+1] = s[i+1][:-4]
			name = s[i]  #.replace(".", "")
			text = s[i+1].replace("\n", " ").replace("_", "")
			text = " ".join(text.split())
			if name not in rv:
				rv[name] = []
				rv[name].append(text)
			else: 
				rv[name].append(text)
	return rv 

	

def split_all_text_dict(text_dict, seps): 
	''' 
	seps are usually all names. Returns a dictionary of dict[date][title][speaker] = text said by that speaker 
	'''
	rv = {}
	for date in text_dict: 
		rv[date] = {}
		for title in text_dict[date]: 
			if 'raw_text' in text_dict[date][title]:
				rv[date][title] = {}  
				rv[date][title] = split_by_speaker(text_dict[date][title]['raw_text'], seps)
				if rv[date][title] == -1: 
					print date + " " + title 
	return rv 



