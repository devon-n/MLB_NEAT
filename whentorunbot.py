# Scrape odds from odds portal

# BEST TIME TO RUN SO FAR IS MIDNIGHT 00:00S
import os
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

dir_path = os.path.dirname(os.path.realpath(__file__))
PATH = dir_path + '/chromedriver'
driver = webdriver.Chrome(executable_path=PATH, options=chrome_options)


time.sleep(3)

# tz = pytz.timezone('America/New_York')
today = datetime.now()
today_str = datetime.strftime(today, '%d-%B-%Y')
yesterday = today - timedelta(days = 1)
yesterday_str = datetime.strftime(yesterday, '%d-%B-%Y')
year = today.year
month = today.month
hour = today.hour
minute = today.minute


def get_todays_games():


    all_games = []
    driver.get('https://www.pinnacle.com/en/baseball/mlb/matchups')

    # Get all blocks of games
    blocks = WebDriverWait(driver, 999).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.style_vertical__3xnFk"))
    )
    
    # Get last block = todays games 
    block = blocks[-1]

    games = block.find_elements_by_css_selector('div.style_row__3_aBC')

    # For each game listed
    for game in games:
        teams = game.find_element_by_css_selector('div.style_participants__FetcR')
        team1, team2 = teams.text.split('\n')
        if ('Away' in team1) or ('Home' in team2):
            continue

        # Get odds
        odds = game.find_elements_by_tag_name('span.price')
        try:
            odd1, odd2 = float(odds[0].text), float(odds[1].text)
        except:
            odd1, odd2 = 1, 1
        
        match_time = game.find_element_by_tag_name('span.style_time__1_zpO.ellipsis').text


        # Save each game as dict
        game_dict = {
            'Time': match_time,
            'Date': today_str,
            'Home': team1,
            'Visitor': team2,
            'Home Odds': odd1,
            'Vis Odds': odd2
        }
        all_games.append(game_dict)

    # Save to csv
    future_games_df = pd.DataFrame(all_games)
    num_of_games = len(future_games_df)
    future_games_df.to_csv(f'/home/dev/Desktop/Projects/AI/MLB/quiz_ga/auto_files/{num_of_games}_games_collected_at_{hour}.csv', index=False)
    driver.quit()
    


get_todays_games()