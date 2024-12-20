import os

import flask
from flask import jsonify , request

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask_cors import CORS

from urllib.parse import urlparse, parse_qs

from YTMutator import YouTubeMutator

import spotify 

from scraper import get_yt_links, GOOGLE_API_KEY

# import scraper
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets_youtube_playlist_exporter.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works, but if you
# use this code in your application please replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = os.urandom(12)

youtube_manager = None

global playlistsSpotify
playlistsSpotify = ["happy", "zcool playlist", "bears", "Wizard of oz"]
songsForYoutube = []
youtubeIds = []
playlistName = ""
credentials = None

CORS(app, supports_credentials=True)  # Need to add this and CORS import to run flask server along with sveltekit 

@app.route('/', methods=['GET'])
def index():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

# Load the credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    youtube_instance = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    global youtube_manager
    youtube_manager = YouTubeMutator(youtube_instance)

    return channels_list_by_username(youtube_instance,
        part='snippet,contentDetails,statistics',
        forUsername='GoogleDevelopers')


@app.route('/authorize')
def authorize():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # This parameter enables offline access which gives your application
        # both an access and refresh token.
        access_type='offline',
        # This parameter enables incremental auth.
        include_granted_scopes='true')  
    # Store the state in the session so that the callback can verify that
    # the authorization server response.
    flask.session['state'] = state
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    global credentials
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True) 
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response) 
    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    credentials = flow.credentials
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return flask.redirect("/PlaylistExporter")

@app.route("/PlaylistExporter")
def playlistExporter():
    global songsForYoutube
    songsForYoutube = spotify.send_user_playlist(playlist_name=playlistName)
    global youtubeIds
    youtubeIds = get_yt_links(songsForYoutube, GOOGLE_API_KEY)
    global credentials
    # call playlist scraper spotify only function
    if "credentials" not in flask.session:
        return flask.redirect("/authorize")  # Redirect user to authenticate

    # Load the credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])

    youtube_instance = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )

    global youtube_manager
    if not youtube_manager:
        youtube_manager = YouTubeMutator(youtube_instance)

    created_playlist = youtube_manager.createUserPlaylist(playlist_name=playlistName)
    print("created_playlist: ", created_playlist)
    print("youtubeIds: ", youtubeIds)
    youtube_manager.exportLinks(created_playlist, youtubeIds) # error

    # Need to return back to website 
    # return jsonify(response_data) 
    return flask.redirect("http://localhost:5173/success")
    

def channels_list_by_username(client, **kwargs):
    response = client.channels().list(**kwargs).execute()
    return flask.jsonify(**response)

@app.route("/spotifyLogin")
def loginSpotify():
    global playlistsSpotify
    playlistsSpotify = spotify.login_user()
    return flask.redirect("http://localhost:5173/")


@app.route("/getPlaylists", methods=['GET'])
def fetch_spotify_playlist():
    try:
        # Check if playlistsSpotify is empty or not loaded
        if not playlistsSpotify:
            raise ValueError("No playlists available. Please log in to Spotify first.")
        return jsonify({"playlists": list(playlistsSpotify)})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch playlists: {str(e)}"}), 500

    
@app.route("/getSongs", methods=['POST'])
def spotify_playlist():
    data = request.get_json()
    print("data: ", data)
    playlist = data.get('selected')
    print("playlist:", playlist)
    global playlistName
    playlistName = playlist
    #global songsForYoutube
    #songsForYoutube = spotify.send_user_playlist(playlist_name=playlist)
    #global youtubeIds
    #youtubeIds = get_yt_links(songsForYoutube, GOOGLE_API_KEY)
    # Process the playlist URL (you can add your logic here)
    # Example: Extract playlist ID, fetch tracks, etc.
    # response = {
    #     "message": f" Playlist {playlist} received and processed.",
    #     "playlist": playlist,
    #     "songs": songsForYoutube,
    # }

    # Return a response
    return flask.redirect("http://localhost:5173/")


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', port=8090, debug=True)
