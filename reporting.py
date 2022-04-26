import pandas as pd
import matplotlib.pyplot as plt
import csv
import datetime

# Get dates
today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1)
today = today.strftime('%d/%m/%Y')
yesterday = yesterday.strftime('%d/%m/%Y')

results = pd.read_csv('yesterdays_results.csv')
bets = pd.read_csv('todays_bets.csv')


# Load file
data = pd.read_csv('bet_tracking.csv')


# Drop yesterday and todays rows as we will be putting them in next
data.drop(today, axis=0, inplace=True)
data.drop(yesterday, axis=0, inplace=True)


# Write in yesterdays results
for row in results:
    # Input bets and bet amounts
    with open('bet_tracking.csv') as f:
        writer = csv.writer(f)
        writer.writerow(row)

# Input todays bets
for row in bets:
    with open('bet_tracking.csv') as f:
        writer = csv.writer(f)
        writer.writerow(row)

# Line graph of week, month, quarter, half, full season
def make_graph(date_period, data):
    # Data
    # X axis
    # y axis
    # Title
    # colors?

# Compare full season with past season/ averages of past seasons

# Save to PDF file