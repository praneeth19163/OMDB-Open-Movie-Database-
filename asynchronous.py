# # from flask import Flask, request, jsonify
# # import httpx
# # import sqlite3
# # import time
# # import json
# # import asyncio

# # app = Flask(__name__)

# # # Database setup
# # conn = sqlite3.connect("movies1.db", check_same_thread=False)
# # cursor = conn.cursor()
# # cursor.execute("CREATE TABLE IF NOT EXISTS movies (title TEXT, data TEXT)")
# # conn.commit()

# # OMDB_API_KEY = "a57bdb5a"

# # async def fetch_movie(movie_name):
# #     async with httpx.AsyncClient() as client:
# #         url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
# #         response = await client.get(url)
# #         return response.json()

# # @app.route("/async/movie", methods=["POST"])
# # async def get_movie():
# #     data = request.get_json()
# #     if not data or "title" not in data:
# #         return jsonify({"error": "Title parameter is required in JSON body"}), 400

# #     title = data["title"]
# #     start_time = time.time()
    
# #     cursor.execute("SELECT data FROM movies WHERE title=?", (title,))
# #     cached_data = cursor.fetchone()
    
# #     if cached_data:
# #         return jsonify({"source": "cache", "data": json.loads(cached_data[0])})

# #     # ✅ FIX: Use await instead of asyncio.run()
# #     movie_data = await fetch_movie(title)

# #     cursor.execute("INSERT INTO movies (title, data) VALUES (?, ?)", (title, json.dumps(movie_data)))
# #     conn.commit()

# #     end_time = time.time()
# #     return jsonify({"source": "API", "execution_time": end_time - start_time, "data": movie_data})

# # if __name__ == "__main__":
# #     app.run(host="127.0.0.1", port=8000, debug=True)
# from flask import Flask, request, jsonify
# import httpx
# import sqlite3
# import time
# import json
# import asyncio

# app = Flask(__name__)

# OMDB_API_KEY = "a57bdb5a"

# async def fetch_movie(movie_name):
#     async with httpx.AsyncClient() as client:
#         url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
#         response = await client.get(url)
#         return response.json()

# @app.route("/async/movie", methods=["POST"])
# async def get_movie():
#     data = request.get_json()
#     if not data or "title" not in data:
#         return jsonify({"error": "Title parameter is required in JSON body"}), 400

#     title = data["title"]
#     start_time = time.time()

#     # 🚀 Create a new connection for each request
#     conn = sqlite3.connect("movies1.db")
#     cursor = conn.cursor()

#     # Check if the movie is in the cache
#     cursor.execute("SELECT data FROM movies WHERE title=?", (title,))
#     cached_data = cursor.fetchone()
    
#     if cached_data:
#         conn.close()  # Close connection after query
#         return jsonify({"source": "cache", "data": json.loads(cached_data[0])})

#     # Fetch movie data from API
#     movie_data = await fetch_movie(title)

#     # Store the result in the database
#     cursor.execute("INSERT INTO movies (title, data) VALUES (?, ?)", (title, json.dumps(movie_data)))
#     conn.commit()
#     conn.close()  # Close connection after writing

#     end_time = time.time()
#     return jsonify({"source": "API", "execution_time": end_time - start_time, "data": movie_data})

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8000, debug=True)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import sqlite3
import time

app = FastAPI()

conn = sqlite3.connect("movies1.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS movies (title TEXT, data TEXT)")
conn.commit()

OMDB_API_KEY = "a57bdb5a"


class MovieRequest(BaseModel):
    title: str

async def fetch_movie(movie_name):
    async with httpx.AsyncClient() as client:
        url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
        response = await client.get(url)
        return response.json()

@app.post("/async/movie")
async def get_movie_async(movie: MovieRequest):
    start_time = time.time()
    title = movie.title.strip()

    cursor.execute("SELECT data FROM movies WHERE title=?", (title,))
    cached_data = cursor.fetchone()
    if cached_data:
        return {"source": "cache", "data": eval(cached_data[0])}

    movie_data = await fetch_movie(title)

    if "Error" in movie_data:
        raise HTTPException(status_code=404, detail="Movie not found")

    cursor.execute("INSERT INTO movies (title, data) VALUES (?, ?)", (title, str(movie_data)))
    conn.commit()

    end_time = time.time()
    return {"source": "API", "execution_time": end_time - start_time, "data": movie_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
