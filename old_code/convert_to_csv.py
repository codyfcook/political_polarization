import cPickle as pickle 
import csv 


## DEBATES ##
d = pickle.load(open("debates.p", "rb"))
f = csv.writer(open("debates.csv", "wb+"))
f.writerow(["date", "debate", "speaker", "text"])

for date in d.keys(): 
	for speaker in d[date]['speakers']:
		f.writerow([unicode(date.replace(",", "")).encode("utf-8"),
			unicode(d[date]['debate_title'].replace(",", "")).encode("utf-8"),
			unicode(speaker.lower().replace(",", "")).encode("utf-8"),
			d[date]['speakers'][speaker].replace(",", "")
			])

## SPEECHES ##
d = pickle.load(open("speeches.p", "rb"))
f = csv.writer(open("speeches.csv", "wb+"))
f.writerow(["speaker", "type", "date", "text"])

for speaker in d.keys(): 
	for type1 in d[speaker].keys():
		for date in d[speaker][type1].keys(): 
			f.writerow([speaker.replace(",", ""), type1.replace(",", ""), date.replace(",", ""), d[speaker][type1][date].replace(",", "")])


## SPEAKERS DICT ##
d = pickle.load(open("speakers_dict.p", "rb"))
f = csv.writer(open("speakers_dict.csv", "wb+"))
f.writerow(["date", "title", "speaker", "text"])

for date in d.keys(): 
	for title in d[date].keys(): 
		for speaker in d[date][title].keys(): 
			if speaker!="ACTING PRESIDENT" and speaker!="PRESIDING OFFICER":
				text = ' '.join(d[date][title][speaker])
				f.writerow([
					unicode(date.replace(",", "")).encode("utf-8"), 
					unicode(title.replace(",", "")).encode("utf-8"),
					unicode(speaker.replace(",", "")).encode("utf-8"), 
					unicode(text.replace(",", ""))])
