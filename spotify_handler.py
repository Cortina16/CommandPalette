from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()



def _authenticate_spotify():
    """
    Authenticate with Spotify and return a Spotify client.
    """
    scope = (
        "user-read-playback-state user-modify-playback-state "
        "user-read-currently-playing user-read-playback-position "
        "user-library-read user-library-modify user-read-email user-read-private"
    )
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:8080",
        scope=scope,
        username=os.getenv("SPOTIFY_USERNAME"),
    )
    return spotipy.Spotify(auth_manager=auth_manager)


_spotify_client = _authenticate_spotify()

def _active_devices_id_spotify(_spotify_client):
    devices = _spotify_client.devices()
    active_device = None
    for device in devices['devices']:
        if device['is_active']:
            active_device = device['id']
            break
    if not active_device and devices['devices']:
        active_device = devices['devices'][0]['id']
        print(f"no active devices found. resorting to fallback device {devices['devices'][0]['name']}")
    return active_device

def main_controller_spotify(action: str, title: str = None, form: str = 'track', artist: str = None, amount: int = 1):
    """
    control spotify playback functions. if no device found, use device issuing commands.
    :param action: what is going to be performed.
    :param title: name of the spotify playback title. Should not be filled out if simply unpausing
    :param form: what playback medium is being listened to
    :return: an action.
    """
    try:
        active_device = _active_devices_id_spotify(_spotify_client)
        # noinspection PyInconsistentReturns
        playback = _spotify_client.current_playback()
        if action == 'toggle_playback':
            if playback and not playback["is_playing"]:
                _spotify_client.start_playback()
            else:
                _spotify_client.pause_playback()
        if action == 'play':
            if title:
                _play_music_spotify(title, form, artist, active_device)
                return f"playing title {title} of type: {form}"
            else:
                _spotify_client.start_playback(active_device)
                return "Music Unpaused"
        elif action == 'get_track_info':
            return _get_track_info()
        elif action == 'pause':
            _spotify_client.pause_playback(active_device)
            return "Music Paused"
        elif action == 'skip_to_next_track':
            for i in range(amount):
                _spotify_client.next_track(active_device)
                sleep(1)
            return f"{amount} Tracks Skipped"
        elif action == 'skip_to_previous_track':
            _spotify_client.previous_track(active_device)
            return "Backed up to last track"
        else:
            return f"Unknown spotify action attempted {action}"
    except spotipy.SpotifyException as e:
        return f"Spotipy Error: {str(e)}"

def _get_track_info():
    global _spotify_client
    try:
        current_track = _spotify_client.current_user_playing_track()['item']
        track_title = current_track['name']
        artist_name = current_track['artists'][0]['name']
        album_name = current_track['album']['name']
        next_song = _spotify_client.queue()['queue'][0]['name']
        return f"Currently playing: {track_title} by {artist_name} from the album {album_name}. The next song is {next_song}"

    except spotipy.SpotifyException as e:
        return f"Error getting current track: {str(e)}"

def _play_music_spotify(title: str, form: str, artist: str, active_device_id: str):
    """
    play a song from spotify
    :param query: the song to search for
    :return: plays the song that is requested
    """
    if form == 'album':
        if artist:
            search = _spotify_client.search(f"album:{title} artist:{artist}", type='album')['albums']['items'][0]['uri']
            _spotify_client.start_playback(active_device_id, search)
            return None
        search = _spotify_client.search(f"album:{title}", type='album')['albums']['items'][0]['uri']
        _spotify_client.start_playback(active_device_id, search)
    elif form == 'track':
        if artist:
            search = [_spotify_client.search(f"track:{title} artist:{artist}")['tracks']['items'][0]['uri']]
            _spotify_client.start_playback(active_device_id, search)
            return None
        search = [_spotify_client.search(f"track:{title}")['tracks']['items'][0]['uri']]
        _spotify_client.start_playback(active_device_id, uris=search)
    elif form == 'playlist':
        search = _spotify_client.search(f"{title}", type='playlist')['playlists']['items'][0]['uri']
        _spotify_client.start_playback(active_device_id, search)
    return None