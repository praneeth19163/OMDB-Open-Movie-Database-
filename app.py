
import requests
import asyncio
import httpx
import time

MOVIE_TITLES = ["Inception", "Interstellar", "The Dark Knight", "Dunkirk"]

SYNC_URL = "http://127.0.0.1:5000/sync/movie"
ASYNC_URL = "http://127.0.0.1:8000/async/movie"

def test_sync():
    print("\n Testing Synchronous API...")
    total_start_time = time.time()
    for title in MOVIE_TITLES:
        start_time = time.time()
        requests.post(SYNC_URL, json={"title": title})
        end_time = time.time()
        print(f"Sync - {title}: {end_time - start_time:.2f} seconds")
    total_end_time = time.time()
    print(f"\nTotal execution time for Synchronous API: {total_end_time - total_start_time:.2f} seconds")

async def fetch_movie(client, title):
    start_time = time.time()
    await client.post(ASYNC_URL, json={"title": title})
    end_time = time.time()
    print(f"Async - {title}: {end_time - start_time:.2f} seconds")

async def test_async():
    print("\n Testing Asynchronous API...")
    total_start_time = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [fetch_movie(client, title) for title in MOVIE_TITLES]
        await asyncio.gather(*tasks)
    total_end_time = time.time()
    print(f"\nTotal execution time for Asynchronous API: {total_end_time - total_start_time:.2f} seconds")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
