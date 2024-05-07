"""
API:
This module defines a class designed to retrieve data from the MusicBrainz API.
It provides methods to fetch information such as artist ID, artist area and album names.

Author: Tamara Weilharter
Version: 2024/05
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import requests
import base64
import json
from requests import post, get


# --------------------------------------------------------------------
# Class definition
# --------------------------------------------------------------------
class ArtistInfos:
    """
    This class provides methods to access information from the MusicBrainz API.
    """
    # defines header for query's with user-agent-string: 'user/version ( email@provider.com )'
    header = {
        'User-Agent': 'username/1.2.0 ( email@provider.com )'
    }

    def api_request(self, url):
        """
        Sends a GET request to the specified URL and returns the JSON response.

        :param url: The URL to send the request to.
        :return: JSON data returned by the API.
        """
        try:
            response = requests.get(url, headers=self.header)
            return response.json()
        except requests.exceptions.RequestException:
            print('Connection to API failed.')

    def get_artist_id(self, name):
        """
        Searches for the artist's name and retrieves the ID of the first matching result.

        :param name: The name of the artist.
        :return: The ID of the artist if found in the API, otherwise returns None.
        """
        # defines query url and gets JSON response
        request_url = f'https://musicbrainz.org/ws/2/artist?query={name}&fmt=json'
        query_data = self.api_request(request_url)

        # checks if the relevant key exists
        if 'artists' in query_data:
            query_results = query_data['artists']
            # checks if there are any results for this artist name and selects the first result
            if query_results:
                return query_results[0]['id']
            else:
                return None

    def get_artist_area(self, mb_id):
        """
        Retrieves information about the artist using their MusicBrainz ID.

        :param mb_id: The MusicBrainz ID of the artist.
        :return: The area associated with the artist if available, otherwise returns None.
        """
        # defines search url and gets JSON response
        request_url = f'https://musicbrainz.org/ws/2/artist/{mb_id}?inc=aliases&fmt=json'
        artist_data = self.api_request(request_url)

        # checks if the relevant key exists and if the value is not None
        if 'area' in artist_data and artist_data['area'] is not None:
            return artist_data['area']['name']
        else:
            return None

    def get_album_names(self, name):
        """
        Searches for albums related to the specified artist name or similar artist name matches.

        :param name: The name of the artist.
        :return: A list of album names related to this specific artist.
        """
        # defines query url and gets JSON response
        request_url = f'https://musicbrainz.org/ws/2/release-group?query={name}&fmt=json'
        album_data = self.api_request(request_url)

        # creates empty list to store album names, which will be filled later
        albums = []
        # checks if the relevant key exists
        if 'release-groups' in album_data:
            release_groups = album_data['release-groups']
            # goes through all results
            for release_group in release_groups:
                # checks if the album belongs to this specific artist name
                if release_group['artist-credit'][0]['name'] == name:
                    albums.append(release_group['title'])

        return albums


class SpotifyAPI:
    """
    This class provides methods to access information from the Spotify API.
    """
    client_id = # insert your client_id
    client_secret = # insert your client_secret

    def __init__(self):
        """
        Creates a token and a header to be able to connect with the Spotify API.
        """
        auth_string = self.client_id + ':' + self.client_secret
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + auth_base64,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {'grant_type': 'client_credentials'}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)

        token = json_result['access_token']
        self.header = {'Authorization': 'Bearer ' + token}

    def search_artist(self, artist_name):
        """
        Searches for the artist's name and retrieves the ID of the first matching result.

        :param artist_name: The name of the artist.
        :return: The ID of the artist if found in the API, otherwise returns None.
        """
        url = 'https://api.spotify.com/v1/search'
        query = f'?q={artist_name}&type=artist&limit=1'

        query_url = url + query
        result = get(query_url, headers=self.header)
        json_result = json.loads(result.content)['artists']['items']
        if len(json_result) == 0:
            return None
        else:
            return json_result[0]['id']

    def get_songs(self, artist_id):
        """
        Retrieves the top tracks of this specific artist.

        :param artist_id: The Spotify ID of this specific artist.
        :return: A json object with all information of the tracks.
        """
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
        result = get(url, headers=self.header)
        json_result = json.loads(result.content)['tracks']
        return json_result


# for testing and building this module
if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    artist = 'Powerwolf'
    infos = ArtistInfos()
    id = infos.get_artist_id(artist)
    print(id)
    print(infos.get_artist_area(id))
    print(infos.get_album_names(artist))

    spotify = SpotifyAPI()
    spotify_id = spotify.search_artist(artist)
    songs = spotify.get_songs(spotify_id)

    print(f'Top songs of {artist}:')
    for idx, song in enumerate(songs):
        print(f"{idx + 1}. {song['name']}")
