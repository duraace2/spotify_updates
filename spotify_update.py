#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 18:18:19 2017

@author: ElMaestro
"""

import pandas as pd 
import configparser
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials 
import spotipy.oauth2 as oauth2
sp = spotipy.Spotify()
from random import randint
import spotify_secrets

def spotify_login():
    cid = spotify_secrets.CID
    secret = spotify_secrets.SECRET
    username = spotify_secrets.USERNAME
    uri = 'http://localhost:8888/callback/'
    scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private'
    #
    auth = oauth2.SpotifyClientCredentials(client_id=cid,client_secret=secret)
    token = util.prompt_for_user_token(username, client_id=cid, \
                                       client_secret=secret, redirect_uri=uri, scope=scope)
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)

    return username, sp

username, sp = spotify_login()

def show_tracks(results):
    for i, item in enumerate(results['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Get playlists and their details
# Currently, this is only done for those playlists included in the "Include Playlists" list below
# and that are owned by Spotify
def get_playlists(username):
    results = sp.user_playlists(username)
    playlists = results['items']    
    while results['next']:
            try:
                results = sp.next(results)
                playlists.extend(results['items'])
            except:
                pass
    
    pl_types = ['THANKSGIVING', 'XMAS', 'CHRISTMAS', 'HOLIDAY',
                'HALLOWEEN']
    not_pls = ['TOP 100 (OR SO...) MOST POPULAR SPOTIFY WEDDING RECEPTION SONGS',
           'CLASSICAL']

    pl_ids = []
    pl_owner=[]
    playlist_names=[]
    
    for playlist in playlists:

        pl_name = playlist['name'].upper()

        for pl_type in pl_types:
            if pl_type in pl_name:
                continue 

        for not_pl in not_pls:
            if pl_name == not_pl:
                continue

        playlist_names.append(pl_name)
        pl_ids.append(playlist['id'])
        pl_owner.append(playlist['owner']['id'])          
    
    playlist_names = list(set(playlist_names))
    pl_ids = list(set(pl_ids))
    pl_owner = list(set(pl_owner))
        
    print('got playlists')
    
    return pl_ids,pl_owner, playlist_names, playlists


# Need both playlist id's and playlist owner to get particular song ids
def get_song_ids(pl_ids,pl_owner):
    song_ids=[]
    for i,j in zip(pl_ids, pl_owner):
        track_deets = get_playlist_tracks(j,i)
        for track_deet in track_deets:
            try:
                song_ids.append(track_deet['track']['id'])
            except:
                pass

    songs_ids = list(set(song_ids))

    print('got song ids')

    return song_ids


## Completely replace songs currently in the "Listen Now" playlist with the songs aggregated here
def add_songs_to_playlist(add_to_playlist_id,song_ids):
    username_pl='duraace2'
    sp.user_playlist_replace_tracks(username_pl, add_to_playlist_id, ['spotify:track:2L335xUQFvgKEp5cGQxpHt'])
    add_songs=set()
    for song_id in song_ids:
        add_songs.add(song_id)
    
    song_count = len(add_songs)
    send_to_spotify = []
    for song in add_songs:  
        send_to_spotify.append(song)
        if len(send_to_spotify) == 20 or song_count < 20:
            try:
                sp.user_playlist_add_tracks(username_pl, add_to_playlist_id, send_to_spotify)
                send_to_spotify = []
                song_count -= 20
            except:
                send_to_spotify = []
                song_count -= 20
            print(song_count)


def main():
    add_to_playlist_id = '1mAQF0qEl6qlETc067kTWJ'
    username_pl=username
    pl_ids,pl_owner, playlist_names, playlists = get_playlists(username)
    song_ids = get_song_ids(pl_ids,pl_owner)
    add_songs_to_playlist(add_to_playlist_id,song_ids)

    return  pl_ids,pl_owner, playlist_names, playlists, song_ids


if __name__ == "__main__":
    pl_ids,pl_owner, playlist_names, playlists, song_ids = main()

            

