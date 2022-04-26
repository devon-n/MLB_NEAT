# CHANGE ALL PATHS TO ABSOLUTE PATHS USING LOCAL_DIR

# Scrape odds from odds portal
import time
import os
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
chrome_options.headless = True

# Absolute path always
dir_path = os.path.dirname(os.path.realpath(__file__))
PATH = dir_path + '/chromedriver'
driver = webdriver.Chrome(executable_path=PATH, options=chrome_options)

# Floor today and yesterday
today = datetime.now()
today = pd.to_datetime(today).floor(freq='D')
today_str = datetime.strftime(today, '%d-%B-%Y')
tomorrow = today + timedelta(days = 1)
tomorrow = pd.to_datetime(tomorrow).floor(freq='D')
tomorrow_str = datetime.strftime(tomorrow, '%d-%B-%Y')
year = today.year
month = today.month



def get_todays_games():

    # Change timezone to EST
    # Change in account settings on pinnacle
    all_games = []

    # Get the team names
    driver.get('https://www.pinnacle.com/en/baseball/mlb/matchups')

    # Each day - get 2nd day
    blocks = WebDriverWait(driver, 999).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.style_vertical__3xnFk"))
    )
    
    # Get last block of games (todays games)
    block = blocks[-1]
    games = block.find_elements_by_css_selector('div.style_row__3_aBC')

    # For each game listed
    for game in games:
        teams = game.find_element_by_css_selector('div.style_participants__FetcR')
        team1, team2 = teams.text.split('\n')
        team1 = team1.strip()
        team2 = team2.strip()
        
        # Check if summary of game
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
            'Date': tomorrow,
            'Home': team1,
            'Visitor': team2,
            'Home Odds': odd1,
            'Vis Odds': odd2
        }
        all_games.append(game_dict)

    # Save to csv
    future_games_df = pd.DataFrame(all_games)
    future_games_df.to_csv('auto_files/future_games.csv', index=False)


def get_yesterdays_results():

    driver.get('https://www.oddsportal.com/baseball/usa/mlb/results/#/page/1/')

    # Change timezone to Eastern USA
    time.sleep(3)
    timezone = driver.find_element_by_id('user-header-timezone-expander')
    timezone.click()
    time.sleep(3)
    # driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[7]/div/a[40]').click() # US Eastern time
    
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[7]/div/a[69]').click() # Syd time
    

    odds_list = []

    table = driver.find_element_by_tag_name('tbody')

    rows = table.find_elements_by_tag_name('tr')

    for row in rows:
        try:
            date = row.find_element_by_css_selector('th.first2.tl').text
        except:
            cols = row.find_elements_by_tag_name('td')

            if len(cols) > 5:
                match_time = cols[0].text
                teams = cols[1].text
                teams = teams.replace('\n', '')
                if ' - ' in teams:
                    home_team = teams.split(' - ')[1].strip()
                    vis_team = teams.split(' - ')[0].strip()
                    home_team = 'St. Louis Cardinals' if 'St.L' in home_team else home_team
                    vis_team = 'St. Louis Cardinals' if 'St.L' in vis_team else vis_team
                score = cols[2].text
                if ':' in score:
                    home_score = int(score.split(':')[0])
                    vis_score = int(score.split(':')[1])
                    outcome = True if home_score > vis_score else False
                
                    if 'Today' in date:
                        odds_dict = {
                            'Time': match_time,
                            'Date': today,
                            'Home': home_team,
                            'Visitor': vis_team,
                            'Home Score': home_score,
                            'Vis Score': vis_score,
                            'Home Win': outcome                   
                        }

                        odds_list.append(odds_dict)
    
    # Save to csv
    past_games_df = pd.DataFrame(odds_list)
    past_games_df.to_csv('auto_files/yesterdays_results.csv', index=False)
    return past_games_df


def merge_predictions_with_results(df):
    
    # Load all games
    yesterdays_bets = pd.read_csv('./auto_files/betting_actions.csv', parse_dates=['Date'])

    # Floor dates in both dfs
    yesterdays_bets['Date'] = yesterdays_bets['Date'].dt.floor(freq='D')
    df['Date'] = df['Date'].dt.floor(freq='D')

    # Merge into new df
    merged = pd.merge(yesterdays_bets, df, on=['Time', 'Date', 'Home', 'Visitor'], how='outer', sort=False)

    # Save
    merged.to_csv('./auto_files/yesterdays_bets_and_results.csv', index=False)






get_todays_games()
past_games_df = get_yesterdays_results()
merge_predictions_with_results(past_games_df)