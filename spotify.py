from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import spotipy
import time
import sys
import pandas as pd
import matplotlib
matplotlib.use('Tkagg')
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pyrebase
from passwords import CLIENT_ID, CLIENT_SECRET, CONFIG

def get_tracks(db, album_url, sp):
    """
    Get tracks for a given album

    :param db: Firebase Database
    :param album_url: Album URI or URI
    """

    album = sp.album(album_url)

    album_name = album["name"]
    alb_name = db.child("video_games").child("album_name").set(album_name)
    album_artist = album['artists']
    for artist in album_artist:
        artist_name = artist['name']
        art_name = db.child("video_games").child("album_name").child(album_name).child("album_artist").set(artist_name)


    #alb_name = db.child("video_games").child("album_name").set(album_name)

    album_tracks = album["tracks"]["items"]

    for track in album_tracks:
        track_name = track["name"]
        track_uri = track["uri"]
        print(track_name)
        print(track_uri)
        json_segments = get_features(track_uri, sp)
        art_name = db.child("video_games").child("album_name").child(album_name).child("track_feature").set(json_segments)
        exit(0)
    #    get_sections(track_uri, sp)


def get_features(track_uri, sp):
    """
    Get detailed features for each track_uri

    :param track_uri: URI for the track
    """

    features = sp.audio_features(track_uri)

    analysis = sp._get(features[0]['analysis_url'])
    segments = analysis['segments']

    new_segment = []
    for segment in segments:
        start = segment["start"]
        pitches = segment["pitches"]
        new_segment.append({"start": start, "pitches": pitches})

    json1 = json.dumps(new_segment, indent=4)

    df = pd.read_json(json1, orient='records')
    df1 = pd.DataFrame(df['pitches'].values.tolist(), index=df.index)

    df2 = pd.concat([df, df1], axis=1)
    df2.drop(columns=['pitches'],inplace=True)
    df3 = df2.T
    new_header = df3.iloc[0] #grab the first row for the header
    df3 = df3[1:] #take the data less the header row
    df3.columns = new_header #set the header row as the df header

    json_segments = df3.to_json(orient="split")
    print(df3)
    return(json_segments)


def get_sections(track_uri, sp):
        """
        Get detailed features for each track_uri

        :param track_uri: URI for the track
        """

        features = sp.audio_features(track_uri)

        analysis = sp._get(features[0]['analysis_url'])
        segments = analysis['segments']

        new_segment = []
        for segment in segments:
            start = segment["start"]
            loud_time = segment["loudness_max_time"]
            time = start + loud_time
            pitches = segment["pitches"]
            new_segment.append({"time": time, "pitches": pitches})

        json1 = json.dumps(new_segment, indent=4)

        df = pd.read_json(json1, orient='records')
        df1 = pd.DataFrame(df['pitches'].values.tolist(), index=df.index)

        df2 = pd.concat([df, df1], axis=1)
        df2.drop(columns=['pitches'],inplace=True)
        df3 = df2.T
        new_header = df3.iloc[0] #grab the first row for the header
        df3 = df3[1:] #take the data less the header row
        df3.columns = new_header #set the header row as the df header

        json_segments = df3.to_json(orient="split")
    #    print(df3)
        #visualize(df3)
        #exit(0)

def visualize(df):
    """
    Visualizations for track database

    :param df: pandas dataframe
    """
    ax = plt.axes()
    ax = sns.heatmap(df, ax = ax, linewidths=0.1, cmap="Set3")
    plt.show()

def main():

    client_id= CLIENT_ID
    client_secret= CLIENT_SECRET

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace=False

    config = CONFIG

    firebase = pyrebase.initialize_app(config)

    if len(sys.argv) > 1:
        artist_name = ' '.join(sys.argv[1:])
    else:
        artist_name = 'ramin djawadi'

    results = sp.search(q=artist_name, limit=1)

    db = firebase.database()
    album = 'https://open.spotify.com/album/3jQ7eqotwovipeZ3j3rMqu'
    get_tracks(db, album, sp)

    #visualize()


if (__name__ == "__main__"):
    main()
