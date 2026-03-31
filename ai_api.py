import json
from datetime import datetime
from time import sleep

import websockets
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import subprocess
import webbrowser
import keyboard
import ddgs
import python_weather
import asyncio
import os
from spotify_handler import main_controller_spotify, _spotify_client
load_dotenv()

# ------INITIALIZATION-------#
BROWSER_PATHS = {
    # if you want jarvis to be able to use other browsers,\
    # add a line with what you want the browser to be titled on the left
    # then add it's directory to the right
    # then find the prompt for brwosers and add the instruction that {browser title} is how jarvis hsould refer to whatever browser you added.
    # "firefox incognito": "C:\\Program Files\\Mozilla Firefox\\private_browsing.exe",
    # "firefox regular": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
}

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
entity_id_list = {}

for name, path in BROWSER_PATHS.items():
    webbrowser.register(name, None, webbrowser.BackgroundBrowser(path))


# allows jarvis to steal users keyboard and start typing
def key_control(action: str, text: str = None):
    if action == 'write' and text:
        keyboard.write(text, delay=0.1)
        return f'successfully typed {text}'
    elif action == 'press_and_release' and text:
        keyboard.press_and_release(text)
        return f'successfully pressed {text}'
    else:
        return f"unsupported action {action}"

# gets time on user's computer
def get_time():
    """
    returns the current time and date
    """
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")


# searches google for whatever
def web_search(query: str):
    """
    performs a web search and returns the result
    :param query: the web search query
    :return: the search result
    """
    try:
        results = ddgs.DDGS().text(query=query, max_results=3)
        results_array = [{'title': r['title'], 'description': r['body'], 'url': r['href']} for r in results]
        if results_array:
            return "\n".join([f"Title: {r['title']}\nDescription: {r['description']}" for r in results_array])
    except Exception as e:
        print(f'error in web search: {query}, error: {e}')
    return f'No results found for {query}'


# grabs weather
async def weather_grabber(location):
    """
    returns the current weather and date
    :param location: the location of the weather
    :return: returns the weather for the given location
    """
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(location)

    return f"The temperature is {weather.temperature} and is {weather.kind} with a description of {weather.description} and a windspeed of {weather.wind_speed} mph and coordinates of {weather.coordinates}"


# self explanatory
def get_weather(location):
    return asyncio.run(weather_grabber(location))




# allows jarvis to rummage through user's pc
def search_files(query, result_amount: int = 5, otherFunction: bool = False):
    command = ["es.exe", "-s", "-n", str(result_amount), query]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().split("\n")
        if otherFunction:
            return result
        return "\n".join(f"- {path}" for path in result)
    except Exception as e:
        print(f'error in search_files: {query}, error: {e}')
        return f'error in search_files: {query}, error: {e}'


# allows jarvis to run executables on user's pc
def run_program(query):
    if query.endswith(".exe"):
        result = search_files(query, otherFunction=True)
    else:
        result = search_files(f"{query}.exe", otherFunction=True)
    try:
        for path in result:
            if path.find('.exe') != -1:
                subprocess.run([path])
                return 'process ran successfully'
        return 'process could not be ran, or possibly not found.'
    except Exception as e:
        print(f'error in program: {query}, error: {e}')
        return 'program could not be ran'


# allows Jarvis to open browser tabs
def open_tabs(url: str, browser: str = 'firefox regular'):
    try:
        for name, v in BROWSER_PATHS.items():
            if name == browser:
                webbrowser.get(name).open_new_tab(url)
                return 'tab opened successfully'
        webbrowser.get('chrome').open_new_tab(url)
        return 'defaulted to google because whatever you put in did not work'
    except webbrowser.Error as e:
        return f"error could not find or open the requested browser: {browser}, with error message: {e}"
    except Exception as e:
        return f"error {e}"