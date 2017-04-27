from bs4 import BeautifulSoup
import requests
import re
import sys
from datetime import datetime
import cPickle as pickle


'''
DESCRIPTION: 
Script to store functions that will be used frequently acrossed multiple files
'''


def make_soup(link):
    '''
    Simple function to make soup from a page for a given link
    '''
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except:
        print "ERROR IN MAKING SOUP: " + str(link)
