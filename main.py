"""
Script:
This is the program code where all modules are executed.

Author: Tamara Weilharter
Version: 2024/05
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from modules.web_logger import ConcertsData
from modules.api_logger import ArtistInfos, SpotifyAPI
from modules.safe_data import create_database, ManageDatabase
from tqdm import tqdm
from colorama import Fore, Style
from difflib import get_close_matches


# --------------------------------------------------------------------
# Program code
# --------------------------------------------------------------------

######################
# TOP TRACKS SPOTIFY #
######################

# collects data from a website with web scraping
concerts = ConcertsData('https://www.metal-hammer.de/alle-konzerte-in/wien/')
concerts_data_df = concerts.collect_data()

# collects all infos from API with the artist names of the DataFrame above
artists_names = concerts_data_df['Artist'].unique().tolist()

# asks the user for an artist name as input
input_artist = input(Fore.BLUE + 'Choose an artist to get their top tracks and check if they have a concert in '
                                 'Vienna: ' + Style.RESET_ALL)

# connects to Spotify API to get top tracks
spotify = SpotifyAPI()
spotify_id = spotify.search_artist(input_artist)
songs = spotify.get_songs(spotify_id)

print(Fore.BLUE + f'\nHere are the top tracks of {input_artist}:' + Style.RESET_ALL)
for idx, song in enumerate(songs):
    print(f"{idx + 1}. {song['name']}")

# looks for close matches in the concerts DataFrame and checks if artist has a concert in Vienna
matches = get_close_matches(input_artist, concerts_data_df['Artist'], cutoff=0.8)
if matches:
    artist_match = matches[0]
    print(Fore.GREEN + f'\n{input_artist} has a concert in Vienna:' + Style.RESET_ALL)
    concert_data = concerts_data_df[concerts_data_df['Artist'] == artist_match].to_string(index=False, header=False)
    print(concert_data)
else:
    print(Fore.RED + f'\n{input_artist} has no concert in Vienna.' + Style.RESET_ALL)


################
# COLLECT DATA #
################

print(Fore.BLUE + '\nNow all data for all concerts in Vienna will be collected:')

infos = ArtistInfos()
# saves area and MusicBrainzID in dictionary -> artists_data = {'artist': (area, mb_id)}
artists_data_dicti = {}
for artist in tqdm(artists_names, desc='Collecting ID and area from API'):
    mb_id = infos.get_artist_id(artist)
    time.sleep(0.6)
    area = infos.get_artist_area(mb_id)
    time.sleep(0.6)
    artists_data_dicti[artist] = (area, mb_id)


# saves all album names in dictionary -> albums_data = {'artist': [album_name1, album_name2]}
albums_data_dicti = {}
for artist in tqdm(artists_names, desc='Collecting albums from API'):
    albums = infos.get_album_names(artist)
    time.sleep(0.6)
    albums_data_dicti[artist] = albums


############
# DATABASE #
############

create_database()
database = ManageDatabase()
database.create_tables()

# TABLE -> LOCATIONS
locations_lst = concerts_data_df['Location'].unique().tolist()
database.fill_locations_table(locations_lst)

# TABLE -> AREAS
artists_data_df = pd.DataFrame.from_dict(artists_data_dicti, orient='index', columns=['Area', 'MB_ID'])
areas_lst = artists_data_df['Area'].dropna().unique().tolist()
database.fill_areas_table(areas_lst)

# TABLE -> ARTISTS
database.fill_artists_table(artists_data_dicti)

# TABLE -> ALBUMS
database.fill_albums_table(albums_data_dicti)

# TABLE -> CONCERTS_DATA
database.fill_concerts_table(concerts_data_df)

print('\nDatabase created:\nConnect to your PostgreSQL server to see the database.')
time.sleep(1)


######################
# DATA VISUALIZATION #
######################

# creates folder for plots
work_dir = os.getcwd()
path = work_dir + '/data_visualization'

if not os.path.exists(path):
    os.mkdir(path)

os.chdir(path)

# BAR CHART vertical: number of concerts per month
# grouping by month and counting number of concerts per month
concerts_per_month = concerts_data_df.groupby(concerts_data_df['Date'].dt.strftime('%Y-%m'))['Date'].count()

num_concerts = concerts_per_month.plot.bar(color='#8b0000')

plt.xlabel('month')
plt.ylabel('number of concerts')
plt.title('Number of Concerts per Month')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig(fname='concerts_per_month.png')

# creates empty figure for next plotting image
plt.figure()

# BAR CHART horizontal: number of concerts per location
# counting occurrence of location
concerts_per_location = concerts_data_df['Location'].value_counts()

# selecting top 15 locations
top_locations = concerts_per_location.head(15)

occ_location = top_locations.plot.barh(color='#00008B')

plt.xlabel('number of concerts')
plt.ylabel('location')
plt.title('Number of Concerts per Location (TOP 15)')

plt.tight_layout()
plt.savefig(fname='concerts_per_location.png')


print('\nPlotting completed:\nGo to folder "data_visualization" to see the results.' + Style.RESET_ALL)
time.sleep(1)
