from flask import Flask, jsonify, request
import requests
import sqlite3
import time

app = Flask(__name__)

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS movies (title TEXT, data TEXT)")
conn.commit()

OMDB_API_KEY = "a57bdb5a"

@app.route("/sync/movie", methods=["POST"])
def get_movie_sync():
    start_time = time.time()
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Please provide a movie title in JSON body"}), 400

    movie_name = data["title"]

    """Check if data exists in the database"""
    cursor.execute("SELECT data FROM movies WHERE title=?", (movie_name,))
    cached_data = cursor.fetchone()
    if cached_data:
        return jsonify({"source": "cache", "data": eval(cached_data[0])})

    """synchronous request to fetch movie details"""
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch movie data"}), 500

    movie_data = response.json()
    cursor.execute("INSERT INTO movies (title, data) VALUES (?, ?)", (movie_name, str(movie_data)))
    conn.commit()

    end_time = time.time()
    return jsonify({"source": "API", "execution_time": end_time - start_time, "data": movie_data})

if __name__ == "__main__":
    app.run(debug=True)
