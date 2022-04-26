# Import libraries
import os
from pathlib import Path
from selenium import webdriver 
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# Driver path and options
chrome_options = Options()
# chrome_options.headless = True
# Absolute path always
dir_path = os.path.dirname(os.path.realpath(__file__))
PATH = dir_path + '/chromedriver'
driver = webdriver.Chrome(executable_path=PATH, options=chrome_options)

# Import files
from scrape_games import get_yesterdays_results, get_todays_games, merge_predictions_with_results
from keras_preds import clean_games, transform, fit_transform, transform_all_data, predict_and_save
from ne_actions import set_vars, get_questions, make_bet, make_bets, print_bets, replay_genome
from report import get_data, calc_outcome, yesterdays_pnl, combine_games, find_dates, print_charts, create_pdf
from send_email import send_email_func


# Scrape yesterdays results and todays games
get_todays_games()
print('Completed todays games')
past_games_df = get_yesterdays_results()
print('Completed past game results')
merge_predictions_with_results(past_games_df)
print('Completed merge')


# Make predictions with keras
x, games = clean_games()
x = transform_all_data(x)
predict_and_save(x, games)
print('Completed Keras predictions')

# Make betting strategies with NEAT
dir_path, data, MAX_BET_SIZE, MAX_ODDS_SIZE, MIN_ODDS_SIZE, bet_sizes, bet_direction, no_bets_list, bet_dict, config_path = set_vars()
questions, questions_df = get_questions(data)
replay_genome(config_path)
print('Completed Neuroevolution bets')

# Report outcomes and bets in PDF
yes_results, all_games = get_data()
calc_outcome(yes_results)
outcome, correct_games, all_games_len = yesterdays_pnl(yes_results)
all_games = combine_games(all_games, yes_results)
dates = find_dates(all_games)
acc0, acc1, acc2, acc3 = print_charts(all_games, dates)
create_pdf(outcome, correct_games, all_games_len, acc3)
print('Completed PDF generation')

# Send PDF to me
send_email_func()
print('Sent report')
driver.quit()