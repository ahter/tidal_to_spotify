#!/usr/bin/env python3

import argparse
import sys

import yaml

from auth import start_spotify_session, start_tidal_session


def get_playlists_from_spotify(spotify_session, user_id, config=None):
    """
    Get all the playlists from the Spotify account
    """
    spotify_playlists = []
    exclude_list = []
    spotify_results = spotify_session.user_playlists(user_id)

    if config:
        exclude_list = set(
            [x.split(":")[-1] for x in config.get("excluded_playlists", [])]
        )

    while True:
        for spotify_playlist in spotify_results["items"]:
            if (
                spotify_playlist["owner"]["id"] == user_id
                and not spotify_playlist["id"] in exclude_list
            ):
                spotify_playlists.append(spotify_playlist)

        # Move to the next page of results if there are
        # still playlists remaining.
        if spotify_results["next"]:
            spotify_results = spotify_session.next(spotify_results)
        else:
            break

    return spotify_playlists


def move_tidal_playlists_to_spotify(
    tidal_session, spotify_session, exclude_imported: bool = True
):
    """
    Move all the playlists from TIDAL to Spotify.
    """
    current_user = spotify_session.current_user()

    # Get all the TIDAL playlists.
    tidal_playlists = tidal_session.user.playlists()

    # Exclude the imported playlists.
    if exclude_imported:
        tidal_playlists = _exclude_imported_playlists(
            tidal_playlists=tidal_playlists,
            spotify_session=spotify_session,
            user_id=current_user["id"],
        )

    # Create TIDAL playlist(s) on Spotify and add the tracks.
    for tidal_playlist in tidal_playlists:
        # Create the playlist on Spotify.
        spotify_playlist = spotify_session.user_playlist_create(
            user=current_user["id"],
            public=False,
            name=tidal_playlist.name,
            description=tidal_playlist.description,
        )

        # Get the tracks from TIDAL.
        tidal_tracks = tidal_playlist.tracks

        # Search and get the Spotify URIs for the tracks.
        spotify_uris = []
        for tidal_track in tidal_tracks():
            # Search for the track on Spotify.
            spotify_tracks = spotify_session.search(
                q=f"artist:{tidal_track.artist.name} track:{tidal_track.name}",
                type="track",
            )

            # If the track is found, add it to the list.
            if len(spotify_tracks["tracks"]["items"]) > 0:
                spotify_uris.append(spotify_tracks["tracks"]["items"][0]["uri"])

        # Finally, add the tracks to the Spotify playlist.
        spotify_session.playlist_add_items(
            playlist_id=spotify_playlist["id"], items=spotify_uris
        )


def _exclude_imported_playlists(tidal_playlists, spotify_session, user_id):
    """
    Exclude the imported playlists from the list of TIDAL playlists.

    Currently, this is done by comparing the names of the playlists.

    TODO: This should also compare the tracks in the playlists.
    """
    list_of_playlist_names = []
    tidal_playlist_to_import = []

    # Get the list of Spotify playlists.
    # Some of them might already be imported.
    spotify_playlists = get_playlists_from_spotify(
        spotify_session=spotify_session, user_id=user_id
    )

    # Extract the names of the Spotify playlists.
    for playlist in spotify_playlists:
        list_of_playlist_names.append(playlist["name"])

    # Exclude the imported playlists.
    for tidal_playlist in tidal_playlists:
        if tidal_playlist.name not in list_of_playlist_names:
            tidal_playlist_to_import.append(tidal_playlist)

    return tidal_playlist_to_import


if __name__ == "__main__":
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="config.yml", help="location of the config file"
    )

    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # First, start the sessions.
    spotify_session = start_spotify_session(config["spotify"])
    tidal_session = start_tidal_session()
    if not tidal_session.check_login():
        sys.exit("Could not connect to TIDAL!")

    # Then, move TIDAL playlists to Spotify.
    move_tidal_playlists_to_spotify(tidal_session, spotify_session)

    sys.exit("Finished execution.")
