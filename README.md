# Overview
Code to scrape political speech data, run MINRs, and output graphs for the 2016 election.

# Code
Run code in the following order:
* scrape_debates
* scrape_other_election_documents
* scrape_house_and_senate
* convert_all_to_csv

This gets all the initial scraping done. The rest of the code is largely spread among Spark and R.

After the data has been scraped, run:
* Spark/parse_and_create_bigrams.ipynb
* 
