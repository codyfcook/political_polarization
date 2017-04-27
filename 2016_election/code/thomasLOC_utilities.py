from bs4 import BeautifulSoup
import requests
import re
import sys
import cPickle as pickle
import custom_utilities
sys.setrecursionlimit(4800)

# ------------------ #
#  ThomasLOC LINKS   #
# ------------------ #

def collect_suitable_links_for_day(link):
    '''
    Given a link to a day when there were senate proceedings, returns all links that should
    be followed and scraped
    '''
    links = {}
    soup = custom_utilities.make_soup(link)
    main_table = soup.findAll("table", {"class":"item_table"})
    if len(main_table)==0: # this happens when no senate activity on date or invalid date
        return []
    # Find all columns in the table
    tds = main_table[0].findAll("td")
    # For each column, grab the link
    for td in tds:
        a = td.findAll("a")
        if should_follow_link(a[0].text):
            links[a[0].text] = {}
            links[a[0].text]['link'] = a[0]['href']
    return links


def should_follow_link(text):
    '''
    Takes in text description of a link to some senate proceedings document. Returns true or
    false based on whether it is a link that you should follow. Would not want to follow
    procedural links, recognition stuff, etc.
    '''
    text = text.lower()
    things_not_to_follow = ["conclusion of", "extension of", "recognizing", "measures", "measure", "recess", "notices of", "quorum",
        "reauthorizing", "order of", "appointment", "memorial", "honoring", "senate concurrent resolution", "recognition",
        "text of", "welcoming", "prayer", "recognition of", "reservation of", "morning business", "remembering ", "committees",
        "introduction of", "submission of", "additional cosponsors", "additional sponsors", "submitted", "senate resolution", "notice of", "authority for",
        "reports of", "report of", "nomination", "orders for", "adjournment", "nominations", "schedule", "executive session",
        "legislative session", "motion to", "tribute to", "rules of the", "reports on", "report on", "executive and other communications",
        "executive messages", "messages from", "pledge of", "privileges of", "message from", "joint meeting", "res.", "unanimous", "award winners",
        "authorization to", "authorization of",  "appoint", "executive calendar", "congratulat", "celebrating", "as modified", "amendment no.",
        "enrolled bill presented", "upcoming business", "expression to", "anniversary of", "issuance of", "authorization", "exhibition of", "commemorating",
         "thanking", "condemning the", "committee", "resilience of", "h.r.", "the journal", "permission to" , "general leave", "leave of absence",
         "senate", "bills and resolutions", "authority statement", "congressional earmarks", "house of representatives", "morning-hour debate", "announcement by",
          "removal of", "memory", "adjournment", "executive communications", "deletion of",  "memorial",  "communication from", "designat", "amendments",
          "hour of", "special orders", "welcome home"]
    if re.search("s[0-9]", text) is not None: # For links like S9192
        return False
    elif re.search("h[0-9]", text) is not None: # For links like h9192
        return False
    elif (("national" in text) or ("history" in text)) and (("day" in text) or ("week" in text) or ("month" in text)):
        return False
    elif text == "senate" or text == "program" or text == "confirmations" or text == "confirmation":
        return False
    else:
        # Check if any of the above is contained in the title
        for thing in things_not_to_follow:
            if thing in text:
                return False
        return True


def scrape_all_links(start_year, start_month, end_year, end_month, is_senate):
    '''
    Start year + month will be first month of links scraped. End year + month will be last
    month of links scraped. Returns all suitable links in a dictionary {date: links}.
    '''
    if is_senate:
        chamber = "/senate-section"
    else:
        chamber = "/house-section"
    rv = {}
    for year in range(start_year, end_year+1):
        for month in range(1,13):
            if year == start_year and month < start_month:
                continue
            if year == end_year and month > end_month:
                continue
            print "Scraping " + str(month) + "/" + str(year) + "..."

            for day in range(1, 32):
                date = str(year) + "/" + str(month) + "/" + str(day)
                #print "Scraping " + date
                link = "https://www.congress.gov/congressional-record/" + date + chamber
                l = collect_suitable_links_for_day(link)
                if len(l) != 0 and l is not None:
                    rv[date] = l
    return rv



# -------------------- #
#  ThomasLOC SCRAPING  #
# -------------------- #


def get_page_text(link):
    '''
    Given a link to a senate doc, returns relevant text on that get_page_text
    '''
    soup = custom_utilities.make_soup(link)
    text = soup.find("pre", {"class":"styled"}).text
    text = re.sub('<[^>]+>', ' ', text)
    text = re.sub("[\[].*?[\]]", " ", text)
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
                link = "https://www.congress.gov" + links_dict[key][key2]['link']
                rv[key][key2]['raw_text'] = get_page_text(link)
            except:
                print "Error scraping: " + links_dict[key][key2]['link']
                rv[key][key2]['raw_text'] = ""
    return rv


def is_starting_speaker(word):
    '''
    Returns true if the word is the starting speaker
    '''
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


# ---------------- #
#  TEXT CLEANING   #
# ---------------- #

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


# ---------------- #
#  PARTY MAPPING   #
# ---------------- #
def create_name_to_party_map(all_names, is_senate):
    '''
    Creates a dictionary of name (in all names) to 'party', 'dwnom1', 'dwnom2', 'chamber'
    '''
    if is_senate:
        filenm = '../working_data/senate_dwnom_clean.csv'
    else:
        filenm = '../working_data/house_dwnom_clean.csv'
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
                    all_names_map[key]['dwnom'] = dict1['dwnominate']
                    all_names_map[key]['party'] = dict1['party']
                    all_names_map[key]['state'] = dict1['statenm']
        else: # must be split as [name] of [state], so match both
            for dict1 in dwnom:
                if (dict1['name']==all_names_map[key]['name']) and (dict1['statenm'].strip()[:7]==all_names_map[key]['state'].strip()[:7]):
                    all_names_map[key]['dwnom'] = dict1['dwnominate']
                    all_names_map[key]['party'] = dict1['party']
                    all_names_map[key]['state'] = dict1['statenm']

    return all_names_map

def add_dwnom_and_party(speakers_dict, party_map):
    for date in speakers_dict:
        for title in speakers_dict[date]:
            for speaker in speakers_dict[date][title]:
                if speaker in party_map:
                    if "party"  in party_map[speaker]:
                        speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0], "party":party_map[speaker]['party'], "dwnom":party_map[speaker]['dwnom']}
                    else:
                        speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0]}
                else:
                    speakers_dict[date][title][speaker] = {"text":speakers_dict[date][title][speaker][0]}
    return speakers_dict
