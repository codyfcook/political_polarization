import csv
import numpy as np
import difflib

def create_name_to_party_map(all_names, is_senate): 
	'''
	Creates a dictionary of name (in all names) to 'party', 'dwnom1', 'dwnom2', 'chamber'  
	'''
	if is_senate: 
		filenm = '../DWNOM/senate_dwnom_clean.csv'
	else: 
		filenm = '../DWNOM/house_dwnom_clean.csv'
	with open(filenm) as f: 
		dwnom = list(csv.DictReader(f))

	# Make state and legislator names all lowercase 
	for dict1 in dwnom: 
		dict1['name'] = dict1['name'].lower()
		dict1['statenm'] = dict1['statenm'].lower()

	# standardize name so that if there is a "[name] of [state]", we split those into two keys 
	all_names_map = {}
	for name in all_names: 
		if " of " in name: 
			state = name[name.find("of")+3:].replace(".", "")
			name_final = name[:name.find("of")-1].replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").strip()
			all_names_map[name] = {} 
			all_names_map[name]['name'] = name_final.lower()
			all_names_map[name]['state'] =  state.lower()
		else: 
			name_final = name.replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").strip()
			name_final = name_final.replace(".", "")
			all_names_map[name] = {}
			all_names_map[name]['name'] = name_final.lower()

	# add dwnom scores and party to all_names map, if there is a match
	for key in all_names_map: 
		if len(all_names_map[key].keys())==1: 
			for dict1 in dwnom: 
				if dict1['name']==all_names_map[key]['name']: 
					all_names_map[key]['dwnom1'] = dict1['dwnom1']
					all_names_map[key]['dwnom2'] = dict1['dwnom2']
					all_names_map[key]['party'] = dict1['party']
					all_names_map[key]['state'] = dict1['statenm']
		else: # must be split as [name] of [state], so match both 
			for dict1 in dwnom: 
				if (dict1['name']==all_names_map[key]['name']) and (dict1['statenm'].strip()[:7]==all_names_map[key]['state'].strip()[:7]):
					all_names_map[key]['dwnom1'] = dict1['dwnom1']
					all_names_map[key]['dwnom2'] = dict1['dwnom2']
					all_names_map[key]['party'] = dict1['party']
					all_names_map[key]['state'] = dict1['statenm']

	return all_names_map 

def add_dwnom_and_party(speakers_dict, party_map): 
	for date in speakers_dict: 
		for title in speakers_dict[date]: 
			for speaker in speakers_dict[date][title]: 
				if speaker in party_map:
					if "party"  in party_map[speaker]:
						speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0], "party":party_map[speaker]['party'], "dwnom1":party_map[speaker]['dwnom1'], "dwnom2":party_map[speaker]['dwnom2']}
					else: 
						#print "semi fuck " + speaker
						speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0]}
				else: 
					speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0]}
					print "fuck " + str(speaker) 
				#close_matches = difflib.get_close_matches(speaker, party_map.keys())
				#closest = close_matches[0]

	return speakers_dict 












