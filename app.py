from flask import Flask, render_template, request, jsonify
import lyricsgenius as lg
import csv
import base64

access_token = "LC2defTjjGgEM09GFXIhStvjR9d_YnZ3WArkc_yoW3aA1ewUgCbJGVk8k2BYuveo"
app = Flask(__name__, template_folder='templates')

# Define routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lyrics", methods=["POST"])
def process_form():
    songArtist = request.form.get("searchInput")
    songartistSeparated = songArtist.split(" - ")
    songName = songartistSeparated[0].title()
    artistName = songartistSeparated[1].title()

    with open('Artists.csv') as csvfile:
        artistsCSV = csv.reader(csvfile, delimiter='\n')
        artistsDatabase = []
        for row in artistsCSV:
            artistsDatabase.append(row)
        
        if any(artistName in sublist for sublist in artistsDatabase):
            genius = lg.Genius(access_token)
            artist = genius.search_artist(artistName, max_songs=1, sort="title")
            song = artist.song(songName)
        else:
            return render_template("404.html")
    
    encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
    return render_template("lyrics.html", content=encoded_lyrics, song=songName+ " - " + artistName)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    global song_and_artist
    data = request.get_json()
    print("Received data from JavaScript:", data)

    song_and_artist = data.get('songAndArtist')
    if song_and_artist:
        song_name, artist_name = map(str.strip, song_and_artist.split('-', 1))

        genius = lg.Genius("LC2defTjjGgEM09GFXIhStvjR9d_YnZ3WArkc_yoW3aA1ewUgCbJGVk8k2BYuveo")
        if artist_name:
            artist = genius.search_artist(artist_name, max_songs=1, sort="title")
            if artist:
                song = artist.song(song_name)
                if song:
                    encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
                    return jsonify({'lyrics': encoded_lyrics})

        else:
            song = genius.search_song(song_name)
            if song:
                encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
                return jsonify({'lyrics': encoded_lyrics})

    return jsonify({'error': 'Failed to retrieve lyrics'})

@app.route("/lyrics")
def lyrics():
    lyrics_data = request.args.get('lyrics')
    decoded_lyrics = base64.b64decode(lyrics_data).decode() if lyrics_data else "Lyrics not available"
    return render_template("lyrics.html", content=decoded_lyrics, song=song_and_artist)

@app.route("/loading")
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True, port=8002)
