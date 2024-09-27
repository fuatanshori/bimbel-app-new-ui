import requests
import asyncio
def internetConnection():
    try:
        requests.get("https://www.google.com",timeout=5)
        return True
    except requests.ConnectionError:
        return False
