from bs4 import BeautifulSoup
import requests 
import re 
import sys
import scrape_thomasLOC 
import cPickle as pickle
import scrape_thomasLOC_links
import process_thomasLOC_text
import add_parties
sys.setrecursionlimit(4800)


## MAIN ## 
# Find links
links = scrape_thomasLOC_links.scrape_all_links(2011, 1, 2012, 12, False)
pickle.dump(links, open("house_links_dict.p", "wb"))

# Find all text on those links 
links = pickle.load(open("house_links_dict.p", "rb"))
text_dict = scrape_thomasLOC.create_text_dict(links)
pickle.dump(text_dict, open("house_text_dict.p", "wb"))

# Clean text dict 
text_dict = pickle.load(open("house_text_dict.p", "rb"))
cleaned_text = process_thomasLOC_text.clean_text(text_dict)
pickle.dump(cleaned_text, open("house_cleaned_text_dict.p", "wb"))

# Create speakers dictionary -- splitting by speaker within each day-topic 
cleaned_text = pickle.load(open("house_cleaned_text_dict.p", "rb"))
all_names = scrape_thomasLOC.find_all_names_in_text_dict(cleaned_text) 
speakers_dict = process_thomasLOC_text.split_all_text_dict(cleaned_text, all_names)

# Add party affiliations and dwnom scores to speakers dict
party_map = add_parties.create_name_to_party_map(all_names, False)
speakers_dict = add_parties.add_dwnom_and_party(speakers_dict, party_map)

pickle.dump(speakers_dict, open("house_speakers_dict.p", "wb"))