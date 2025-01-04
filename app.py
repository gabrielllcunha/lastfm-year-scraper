import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from months.albums import fetch_albums
from months.artists import fetch_artists
from months.songs import fetch_songs

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Backend Server Running!"

@app.route("/fetch-albums-by-month", methods=["POST"])
def fetch_albums_by_month():
    data = request.get_json()
    try:
        result = asyncio.run(fetch_albums(data))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch-artists-by-month", methods=["POST"])
def fetch_artists_by_month():
    data = request.get_json()
    try:
        result = asyncio.run(fetch_artists(data))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch-songs-by-month", methods=["POST"])
def fetch_songs_by_month():
    data = request.get_json()
    try:
        result = asyncio.run(fetch_songs(data))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
