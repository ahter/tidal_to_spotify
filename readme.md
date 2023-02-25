A command-line tool for importing your TIDAL playlists into Spotify.
(Check out the original project for the reverse.)

## Installation

Clone this git repository and then run:

```bash
python3 -m pip install -r requirements.txt
```

## Setup

0. Rename the file example_config.yml to config.yml
1. Go [here](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/) and register a new app on developer.spotify.com.
2. Copy and paste your client ID and client secret to the Spotify part of the config file.
3. Copy and paste the value in 'redirect_uri' of the config file to Redirect URIs at developer.spotify.com and press ADD.
4. Enter your Spotify username into the config file.

## Usage

To synchronize all of your Tidal playlists with your Spotify account, run the following:

```bash
python3 sync.py
```

This will take a long time because the Tidal API is really slow.
