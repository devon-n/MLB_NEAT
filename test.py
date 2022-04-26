# # Put default columns on 10_games_collected_at_14.csv
# # Save as all_games

# # Predictions,Bet Direction,Bet Sizes,Home Score,Vis Score,Home Win,Prediction Result,Outcome

import pandas as pd
from scrape_games import get_yesterdays_results

# get_yesterdays_results()


bet_actions = pd.read_csv('./auto_files/yesterdays_results.csv', parse_dates=['Date'])


# drop cols from bet actions
bet_actions.drop(['Home Score', 'Vis Score', 'Home Win'], axis=1, inplace=True)

# Add cols from get_today_games
bet_actions['Home Odds'] = 1.9
bet_actions['Vis Odds'] = 1.9

# add in new cols
bet_actions['Predictions'] = 0.55
bet_actions['Bet Direction'] = True
bet_actions['Bet Sizes'] = 10.0

# Merge
# all_games = pd.merge(bet_actions, yes_results, on=['Time', 'Date', 'Home', 'Visitor'], how='outer', sort=False)
# all_games['Date'] = all_games['Date'].dt.floor(freq='D')


bet_actions.to_csv('./auto_files/betting_actions.csv', index=False)


# Run after all games are completed for the day
