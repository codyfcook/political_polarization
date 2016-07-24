import cPickle as pickle
import csv
from datetime import datetime

## ALL ELECTION DOCUMENTS ##
# ------------------------ #
# Write debates, speeches, press releases, etc. to the same file

# DEBATES #
d = pickle.load(open("../raw_data/debate_text.p", "rb"))
f = csv.writer(open("../final_data/all_election_documents.csv", "wb"))
f.writerow(["date", "speaker", "text", "type"])
for date in d.keys():
    for speaker in d[date].keys():
        f.writerow([
            date,
            unicode(speaker.lower().replace(",", "")).encode("utf-8"),
            d[date][speaker].replace(",", ""),
            "debate"
            ])

# SPEECHES, ETC. #
d = pickle.load(open("../raw_data/other_election_documents_text.p", "rb"))
for speaker in d.keys():
    for type1 in d[speaker].keys():
        for date in d[speaker][type1].keys():
            date_f = datetime.strptime(date, "%B %d, %Y")
            f.writerow([
            date_f,
            unicode(speaker.replace(",", "")).encode("utf-8"),
            unicode(d[speaker][type1][date].replace(",", "")).encode("utf-8"),
            unicode(type1.replace(",", "")).encode("utf-8")
            ])



## ThomasLOC -- HOUSE ##
d = pickle.load(open("../working_data/house_speakers_dict.p", "rb"))
f = csv.writer(open("../final_data/house_thomasloc_text.csv", "wb+"))
f.writerow(["date", "title", "speaker", "text", "party", "dwnom"])

for date in d.keys():
    for title in d[date].keys():
        for speaker in d[date][title].keys():
            if speaker!="ACTING PRESIDENT" and speaker!="PRESIDING OFFICER":
                if 'party' in d[date][title][speaker].keys():
                    text = d[date][title][speaker]['text']
                    party = d[date][title][speaker]['party']
                    dwnom = d[date][title][speaker]['dwnom']
                    f.writerow([
                        unicode(date.replace(",", "")).encode("utf-8"),
                        unicode(title.replace(",", "")).encode("utf-8"),
                        unicode(speaker.replace(",", "")).encode("utf-8"),
                        unicode(text.replace(",", "")).encode("utf-8"),
                        unicode(party.replace(",", "")).encode("utf-8"),
                        unicode(dwnom.replace(",", "")).encode("utf-8")
                        ])

## ThomasLOC -- SENATE ##
d = pickle.load(open("../working_data/senate_speakers_dict.p", "rb"))
f = csv.writer(open("../final_data/senate_thomasloc_text.csv", "wb+"))
f.writerow(["date", "title", "speaker", "text", "party", "dwnom"])

for date in d.keys():
    for title in d[date].keys():
        for speaker in d[date][title].keys():
            if speaker!="ACTING PRESIDENT" and speaker!="PRESIDING OFFICER":
                if 'party' in d[date][title][speaker].keys():
                    text = d[date][title][speaker]['text']
                    party = d[date][title][speaker]['party']
                    dwnom = d[date][title][speaker]['dwnom']
                    f.writerow([
                        unicode(date.replace(",", "")).encode("utf-8"),
                        unicode(title.replace(",", "")).encode("utf-8"),
                        unicode(speaker.replace(",", "")).encode("utf-8"),
                        unicode(text.replace(",", "")).encode("utf-8"),
                        unicode(party.replace(",", "")).encode("utf-8"),
                        unicode(dwnom.replace(",", "")).encode("utf-8")
                        ])
