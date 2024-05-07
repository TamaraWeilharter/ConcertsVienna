"""
Web Scraping:
This module defines a class designed to extract structured data from a specified website.
It utilizes web scraping methods to analyze the HTML structure of the website.

Author: Tamara Weilharter
Version: 2024/05
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import requests
import pandas as pd
from bs4 import BeautifulSoup


# --------------------------------------------------------------------
# Class definition
# --------------------------------------------------------------------
class ConcertsData:
    """
    Extracts and organizes information about current concerts from a designated website into a structured DataFrame.
    """
    def __init__(self, url):
        # initializes url of the website
        self.url = url

    def collect_data(self):
        """
        Scrapes the specified website to gather details about concerts, including their dates, artists, and locations.

        :param self: Instance of the ConcertsData class containing the initialized website URL.
        :return: Pandas DataFrame containing the extracted concert data.
        """
        # makes a HTTP-request
        try:
            scraper_response = requests.get(self.url)
        except requests.exceptions.RequestException:
            print('Connection to website failed.')

        # converts raw content to HTML format
        concerts = BeautifulSoup(scraper_response.content, 'html.parser')

        # examines the structure of the websites data, extracts relevant information and stores it in lists
        website = concerts.find(class_='grid-box grid-box-first grid-box-last grid-box-concerts-list')
        months = website.find_all(class_='ph-concerts-list is-3col')

        dates, artists, locations = [], [], []
        for month in months:
            all_dates = month.find_all(class_='ph-concerts-list-col ph-concerts-list-date')
            for date in all_dates:
                dates.append(date.text.split(' ')[1])

            all_artists = month.find_all(class_='ph-concerts-list-col ph-concerts-list-artist')
            for artist in all_artists:
                artists.append(artist.text.split(' live')[0])

            all_locations = month.find_all(class_='ph-concerts-list-col ph-concerts-list-location')
            for location in all_locations:
                locations.append(location.text.split(',')[0])

        # converts lists in a DataFrame
        all_concerts_df = pd.DataFrame({'Date': dates, 'Artist': artists, 'Location': locations})

        # converts date to date format
        all_concerts_df['Date'] = pd.to_datetime(all_concerts_df['Date'], format='%d.%m.%Y')

        return all_concerts_df


# for testing and building this module
if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    data = ConcertsData('https://www.metal-hammer.de/alle-konzerte-in/wien/')
    concerts_data_df = data.collect_data()
    print(concerts_data_df.to_string())
