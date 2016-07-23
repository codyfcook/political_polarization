from bs4 import BeautifulSoup
import requests
import re
import sys
import cPickle as pickle
import thomasLOC_utilities
import csv
import numpy as np
import pandas as pd
import difflib
sys.setrecursionlimit(4800)

# ----------- #
#  CONSTANTS  #
# ----------- #
START_YEAR = 2015
START_MONTH = 1
END_YEAR = 2016
END_MONTH = 6
CONG_NUM = 113
PARTY_COL = 5
NAME_COL = 6
DWNOM_COL = 7
STATE_COL = 4

# ------------ #
#  CLEAN DWNOM #
# ------------ #

'''
The DWNOMinate comes for all congresses. This restricts the dataset
as desired and limits some of the fields to those needed
'''

# Senate DW-Nominate
senate_dwnom = pd.read_csv("../raw_data/senate_dwnom.csv", header=None)
senate_dwnom = senate_dwnom[senate_dwnom[0]==CONG_NUM][[NAME_COL, STATE_COL, PARTY_COL, DWNOM_COL]]
senate_dwnom['chamber'] = pd.Series('senate', index=senate_dwnom.index)
senate_dwnom.columns = ['name', 'statenm', 'party', 'dwnominate', 'chamber']
senate_dwnom.to_csv("../working_data/senate_dwnom_clean.csv", header=True)

# House DW-Nominate
house_dwnom = pd.read_csv("../raw_data/house_dwnom.csv", header=None)
house_dwnom = house_dwnom[house_dwnom[0]==CONG_NUM][[NAME_COL, STATE_COL, PARTY_COL, DWNOM_COL]]
house_dwnom['chamber'] = pd.Series('house', index=house_dwnom.index)
house_dwnom.columns = ['name', 'statenm', 'party', 'dwnominate', 'chamber']
house_dwnom.to_csv("../working_data/house_dwnom_clean.csv", header=True)

# -------- #
#  SENATE  #
# -------- #

'''
Scrapes and cleans ThomasLOC senate and then maps to the dwnominate scores
'''

# Find links
links = thomasLOC_utilities.scrape_all_links(START_YEAR, START_MONTH, END_YEAR, END_MONTH, is_senate=True)
pickle.dump(links, open("../working_data/senate_links_dict.p", "wb"))
# Find all text on those links
links = pickle.load(open("../working_data/senate_links_dict.p", "rb"))
text_dict = thomasLOC_utilities.create_text_dict(links)
pickle.dump(text_dict, open("../working_data/senate_text_dict.p", "wb"))
# Clean text dict
text_dict = pickle.load(open("../working_data/senate_text_dict.p", "rb"))
cleaned_text = thomasLOC_utilities.clean_text(text_dict)
pickle.dump(cleaned_text, open("../working_data/senate_cleaned_text_dict.p", "wb"))
# Create speakers dictionary -- splitting by speaker within each day-topic
cleaned_text = pickle.load(open("../working_data/senate_cleaned_text_dict.p", "rb"))
all_names = thomasLOC_utilities.find_all_names_in_text_dict(cleaned_text)
speakers_dict = thomasLOC_utilities.split_all_text_dict(cleaned_text, all_names)
# Add party affiliations and dwnom scores to speakers dict
party_map = thomasLOC_utilities.create_name_to_party_map(all_names, is_senate=True)
party_map = create_name_to_party_map(all_names, is_senate=True)
speakers_dict = thomasLOC_utilities.add_dwnom_and_party(speakers_dict, party_map)
speakers_dict = add_dwnom_and_party(speakers_dict, party_map)
# Save!
pickle.dump(speakers_dict, open("../working_data/senate_speakers_dict.p", "wb"))
