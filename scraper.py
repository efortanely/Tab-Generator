import sys
import time
import os
import math
import re
import shelve
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from song import Song

#i have not been able to test this past the first page for any artist
#(not for lack of trying, spent an hour trying)
#will make faster, then test to see if it works okay for other pages

browser = webdriver.Firefox()

def main():
    artists = ['Conan Gray', 'Julia Nunes']
    training_data = []
    data_shelf = shelve.open('song_data')
    browser.get('https://www.ultimate-guitar.com/explore')

    #TODO replace with selenium implicit stalling
    for artist in artists:
        #maintain a set of songs for each artist to avoid
        #duplicate song data
        songs = set()
        
        #search tab website for artist
        search = browser.find_element_by_tag_name('input')
        search.clear()
        search.send_keys(artist + Keys.RETURN)
        time.sleep(2)

        #first number in web element is number of tabs
        num_tabs = browser.find_element_by_class_name('_2PyWj')
        num_tabs = int(num_tabs.text.split()[0])

        #iterate through pages of tabs, 50 tabs per page
        last_page = math.ceil(num_tabs/50)+1
        for page in range(1, last_page):
            if page > 1:
                num_tabs -= 50
                #TODO replace with selenium implicit stalling
                next = browser.find_element_by_link_text(str(page))
                next.click()
                time.sleep(2)
            tabs = browser.find_elements_by_class_name('_1iQi2')
            for tab in range(1,len(tabs)):
                #TODO possibly shorten stall time length?
                try:
                    song = first_scrape(songs,artist,tab)
                except:
                    song = recursive_scrape(songs,artist,page,tab)
                if song:
                    training_data.append(song)
    
    data_shelf['training_data'] = training_data
    data_shelf.close()
    browser.close()
    
def first_scrape(songs, artist, tab_index):
    global browser
    tabs = browser.find_elements_by_class_name('_1iQi2')
    tab = tabs[tab_index]
    #remove clutter from title and click on links to
    #ukulele songs that are new
    title = tab.text
    title = remove(title,r'((^(' + artist + r')+(\n)+)|((^(Misc Unsigned Bands)+(\n)+)*(' + artist + r'\s[-]\s)+)|((.*?((ft.|feat.) '+ artist + r')))+(\n)+)')
    title = remove(title,r'(\s*[(\*\n]+[\s\S]*)|(\n+[\s\S]*)')

    if title not in songs and 'Ukulele' in tab.text:
        #TODO replace with selenium implicit stalling
        song_link = tab.find_element_by_partial_link_text(title)
        song_link.click()
        time.sleep(2)
        lyrics = browser.find_element_by_class_name('_1YgOS')
        time.sleep(2)
        lyrics = lyrics.text
        song = Song(title,lyrics)
        #TODO replace with selenium implicit stalling
        browser.back()
        time.sleep(2)
    else:
        song = None

    return song

def recursive_scrape(songs, artist, page, tab_index):
    global browser
    browser.close()
    browser = webdriver.Firefox()
    browser.get('https://www.ultimate-guitar.com/explore')
    search = browser.find_element_by_tag_name('input')
    search.clear()
    #TODO
    search.send_keys(artist + Keys.RETURN)
    time.sleep(2)
    #TODO
    if page > 1:
        next = browser.find_element_by_link_text(str(page))
        next.click()
        time.sleep(2)
    #TODO possibly shorten stall time length?
    try:
        song = first_scrape(songs,artist,tab_index)
    except:
        song = recursive_scrape(songs,artist,page,tab_index)
    
    return song

def remove(song, filler):
    remove = re.compile(filler)
    remove_matches = remove.search(song)
    if remove_matches is not None:
        song = song.replace(remove_matches.group(),'')
    return song

if __name__ == '__main__':
    main()
