"""
Database configuration:
This module defines a function and a class for creating and populating a PostgreSQL database.

Author: Tamara Weilharter
Version: 2024/05
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
import psycopg2
from modules.config import config


# --------------------------------------------------------------------
# Function and class definition
# --------------------------------------------------------------------
def create_database():
    """
    Creates a PostgreSQL database named 'concerts' based on the parameters provided in the 'database.ini' file.
    If a database with the same name already exists, it is dropped before creating a new one.

    Note: Ensure that the 'database.ini' file is correctly configured with the required parameters.
    """
    # defines parameters
    params = config()

    # connects to database
    conn = psycopg2.connect(
        database=params['database'],
        user=params['username'],
        password=params['password'],
        host=os.getenv('DB_HOST'),
        port=params['port'],
    )

    # ensures that each SQL statement executed by the cursor will be automatically committed
    conn.autocommit = True

    # creates a cursor object
    cursor = conn.cursor()

    # query to delete database if exists
    cursor.execute('DROP DATABASE IF EXISTS concerts;')
    # query to create database
    cursor.execute('CREATE database concerts;')


class ManageDatabase:
    """
    Provides methods for creating and populating tables in a PostgreSQL database.
    """
    def __init__(self):
        """
        Establishes a connection to the PostgreSQL database using the parameters specified in the 'database.ini' file.
        It then creates a cursor object that allows executing SQL commands within the established connection.

        Note: Ensure that the 'database.ini' file is correctly configured with the required parameters.
        """
        params = config()

        self.conn = psycopg2.connect(
            database='concerts',
            user=params['username'],
            password=params['password'],
            host=os.getenv('DB_HOST'),
            port=params['port']
        )

        self.cursor = self.conn.cursor()

    def create_tables(self):
        """
        Creates the schema and the necessary tables in the database for storing concert-related data.
        """
        # query to delete schema if exists
        self.cursor.execute('DROP SCHEMA IF EXISTS concerts_vienna;')
        # query to create schema
        self.cursor.execute('CREATE SCHEMA concerts_vienna;')

        statements = [
            ('CREATE TABLE concerts_vienna.locations(location_id SERIAL PRIMARY KEY, location_name VARCHAR(255) UNIQUE)'),
            ('CREATE TABLE concerts_vienna.areas(area_id SERIAL PRIMARY KEY, area_name VARCHAR(255) UNIQUE)'),
            ('CREATE TABLE concerts_vienna.artists(artist_id SERIAL PRIMARY KEY, area_id INTEGER, artist_name VARCHAR(255) NOT NULL,'
             'mb_id VARCHAR(255) CHECK (mb_id ~* \'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$\'),'
             'FOREIGN KEY (area_id) REFERENCES concerts_vienna.areas(area_id))'),
            ('CREATE TABLE concerts_vienna.concerts_data(concert_id SERIAL PRIMARY KEY, location_id INTEGER,'
             'artist_id INTEGER, date DATE NOT NULL, FOREIGN KEY (location_id) REFERENCES concerts_vienna.locations(location_id),'
             'FOREIGN KEY (artist_id) REFERENCES concerts_vienna.artists(artist_id))'),
            ('CREATE TABLE concerts_vienna.albums(album_id SERIAL PRIMARY KEY, artist_id INTEGER, album_name VARCHAR(255),'
             'FOREIGN KEY (artist_id) REFERENCES concerts_vienna.artists(artist_id))')
        ]

        for statement in statements:
            self.cursor.execute(statement)

        self.conn.commit()

    def fill_locations_table(self, lst):
        """
        Fills the locations table in the database with the provided list of location names.

        :param lst: A list of location names.
        """
        # iterates through list and inserts each element in table
        for item in lst:
            self.cursor.execute('INSERT INTO concerts_vienna.locations (location_name) VALUES (%s)', (item,))

        self.conn.commit()

    def fill_areas_table(self, lst):
        """
        Fills the areas table in the database with the provided list of area names.

        :param lst: A list of area names.
        """
        # iterates through list and inserts each element in table
        for item in lst:
            self.cursor.execute('INSERT INTO concerts_vienna.areas (area_name) VALUES (%s)', (item,))

        self.conn.commit()

    def fill_artists_table(self, dicti):
        """
        Fills the artists table in the database with the provided dictionary of the artists' data.

        :param dicti: A dictionary containing the artist name, area and MusicBrainzID.
        artists_data = {'artist': (area, mb_id)}
        """
        # selects area_id from areas table and inserts it in artists table
        for artist, area_mbid in dicti.items():
            self.cursor.execute('SELECT area_id FROM concerts_vienna.areas WHERE area_name = %s', (area_mbid[0],))
            area_id = self.cursor.fetchone()

            # inserts data in table
            self.cursor.execute('INSERT INTO concerts_vienna.artists (area_id, artist_name, mb_id) VALUES (%s, %s, %s)',
                                (area_id, artist, area_mbid[1]))

        self.conn.commit()

    def fill_albums_table(self, dicti):
        """
        Fills the albums table in the database with the provided dictionary of the album names for each artist.

        :param dicti: A dictionary containing the artist name and a list of album names.
        albums_data = {'artist': [album_name1, album_name2]}
        """
        # selects artist_id from artists table and inserts it in albums table
        for artist, albums in dicti.items():
            self.cursor.execute('SELECT artist_id FROM concerts_vienna.artists WHERE artist_name = %s', (artist,))
            artist_id = self.cursor.fetchone()

            # checks if artist has albums and inserts data in table
            if albums:
                for album in albums:
                    self.cursor.execute('INSERT INTO concerts_vienna.albums (artist_id, album_name) VALUES (%s, %s)',
                                        (artist_id, album))

        self.conn.commit()

    def fill_concerts_table(self, df):
        """
        Fills the concerts_data table in the database with the provided concert data.

        :param df: A DataFrame containing date, artist name and location for each concert.
        """
        # iterates through each row in DataFrame and selects location_id from locations table
        for index, row in df.iterrows():
            self.cursor.execute('SELECT location_id FROM concerts_vienna.locations WHERE location_name = %s',
                                (row['Location'],))
            location_id = self.cursor.fetchone()

            # selects artist_id from artists table
            self.cursor.execute('SELECT artist_id FROM concerts_vienna.artists WHERE artist_name = %s', (row['Artist'],))
            artist_id = self.cursor.fetchone()

            # inserts data in table
            self.cursor.execute('INSERT INTO concerts_vienna.concerts_data (location_id, artist_id, date) VALUES (%s, %s, %s)',
                                (location_id, artist_id, row['Date']))

        self.conn.commit()
