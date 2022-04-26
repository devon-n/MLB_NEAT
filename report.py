import pandas as pd
import os
import jinja2
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime
import pytz
from dateutil import tz
from fpdf import FPDF
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import warnings
warnings.filterwarnings("ignore")

dir_path = os.path.dirname(os.path.realpath(__file__))


# yes_results = pd.read_csv('./auto_files/yesterdays_bets_and_results.csv', parse_dates=['Date'])
# all_games = pd.read_csv('./auto_files/all_games_final.csv', parse_dates=['Date'])


# all_games['Date'].dt.tz_localize('US/Eastern')
# all_games['Date'] = all_games['Date'].dt.normalize()

def get_data():
    ''' Gets the data to run a report on'''
    yes_results = pd.read_csv(dir_path + '/auto_files/yesterdays_bets_and_results.csv', parse_dates=['Date'])
    all_games = pd.read_csv(dir_path + '/auto_files/all_games_final.csv', parse_dates=['Date'])

    # Fixed dates in scraping file so I shouldn't need this
    # all_games['Date'].dt.tz_localize('US/Eastern')
    # all_games['Date'] = all_games['Date'].dt.normalize()
    return yes_results, all_games

# Calc Bankroll For yesterday
def calc_outcome(df):

    df['Prediction Result'] = np.where(df['Bet Direction'] == df['Home Win'], True, False)
    
    conditions = [
        ((df['Prediction Result'] == True) & (df['Home Win'] == True)),
       ((df['Prediction Result'] == True) & (df['Home Win'] == False)),
        (df['Bet Direction'] == 'No Bet'),
        (True)
    ]

    values = [
        (df['Home Odds'] * df['Bet Sizes'] - df['Bet Sizes']),
        (df['Vis Odds'] * df['Bet Sizes'] - df['Bet Sizes']),
        0,
        -df['Bet Sizes']
    ]


    df['Outcome'] = np.select(conditions, values)

    # Save
    return df 
    # CONCAT WITH ALL GAMES AND SAVE
    # df.to_csv('all_games_final.csv', index=False)


# Calucate winning games, losing games and cumsum for yesterday
def yesterdays_pnl(df):

    df_short = df[['Home', 'Visitor', 'Home Odds', 'Vis Odds', 'Home Win', 'Bet Direction', 'Bet Sizes', 'Outcome']]
    df_short['Home'] = df_short['Home'].str.slice(start=0, stop=5)
    df_short['Visitor'] = df_short['Visitor'].str.slice(start=0, stop=5)
    df_short['Outcome'] = df_short['Outcome'].round(2)
    df_short['Bankroll'] = df_short['Outcome'].cumsum()
    df_short['Bankroll'] = df_short['Bankroll'].round(2)
    df_short.drop(['Outcome'], axis=1, inplace=True)

    # Accuracy
    outcome = df_short['Bankroll'][len(df_short)-1]
    correct_games = len(df_short[df_short['Bet Direction'] == df_short['Home Win']])
    all_games_len = len(df_short)

    # Plot chart
    fig, ax = plt.subplots()
    plt.style.use('seaborn')
    ax.axis=('off')
    plt.box(False)
    table = ax.table(cellText=df_short.values, colLabels=df_short.columns, loc='center')
    plt.xticks([])
    plt.yticks([])
    plt.title('Yesterdays Games', pad='0.0')
    plt.savefig(dir_path + '/tmp/table.png', bbox_inches='tight', pad_inches=0, format='png')

    return outcome, correct_games, all_games_len
    

def combine_games(all_games, yes_results):

    combined_games = pd.concat([all_games, yes_results], axis=0, ignore_index=True, sort=False)
    combined_games['Date'] = pd.to_datetime(combined_games['Date'], utc=True)
    return combined_games


def find_dates(combined_games):

    today = pd.to_datetime(combined_games['Date'][len(combined_games) - 1])
    one_week_ago = today - relativedelta(days=7)
    three_mon_ago = today - relativedelta(months=3)
    this_month = today.replace(day=1)
    season_start = combined_games['Date'][0]

    return [one_week_ago, three_mon_ago, this_month, season_start]


def print_charts(df, dates):
    
    # Calc bankroll
    df['Bankroll'] = df['Outcome'].cumsum()

    # End date will always be today
    df0 = df[(df['Date'] >= dates[0])]
    df1 = df[(df['Date'] >= dates[1])]
    df2 = df[(df['Date'] >= dates[2])]
    df3 = df[(df['Date'] >= dates[3])]

    # Calc Accuracy
    acc0 = df0['Prediction Result'].sum() / len(df0) * 100
    acc1 = df1['Prediction Result'].sum() / len(df1) * 100
    acc2 = df2['Prediction Result'].sum() / len(df2) * 100
    acc3 = df3['Prediction Result'].sum() / len(df3) * 100
    
    # Graph bankroll
    fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))
    plt.style.use('seaborn')
    plt.rc('axes', labelsize=40) 
    ax0.set_title('Weekly', fontsize=40)
    ax0.plot(df0['Date'], df0['Bankroll'])

    ax1.set_title('Monthly', fontsize=40)
    ax1.plot(df1['Date'], df1['Bankroll'])

    ax2.set_title('3 Months', fontsize=40)
    ax2.plot(df2['Date'], df2['Bankroll'])

    ax3.set_title('Whole season', fontsize=40)
    ax3.plot(df3['Date'], df3['Bankroll'])

    plt.savefig(dir_path + '/tmp/charts.png', format='png')
    return acc0, acc1, acc2, acc3


def create_pdf(outcome, correct_games, all_games_len, acc3, strategy='HANE'):

    # Create pdf
    WIDTH = 210
    HEIGHT = 297
    pdf = FPDF()
    pdf.add_page()
    pdf.set_text_color(155, 155, 255)
    pdf.set_font('Arial', 'B', 30)

    # Title + charts
    pdf.image(dir_path + '/auto_files/letterhead.png', 0, 0, WIDTH)
    pdf.ln(25)
    pdf.cell(80, 40, ('%s Report' % (strategy))) #HOW TO MOVE TITLE DOWN
    pdf.image(dir_path + '/tmp/charts.png', x=0, y=HEIGHT/2, w=WIDTH, h=HEIGHT/2)

    # Add yesterdays stats
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(155, 155, 255)
    pdf.ln(75)
    pdf.write(5, 'YESTERDAYS STATS')
    pdf.ln(10)
    pdf.write(5, 'Bankroll: '+str(outcome))
    pdf.ln(10)
    pdf.write(5, 'Correct Games: '+str(correct_games)+'/'+str(all_games_len))
    pdf.ln(10)
    pdf.write(5, 'Season Accuracy: '+str(round(acc3, 2))+'%')

    # Add games table in
    pdf.add_page(orientation='L')
    pdf.image(dir_path + '/tmp/table.png', x=0, y=0, w=HEIGHT, h=WIDTH)
    pdf.output(dir_path + '/tmp/report.pdf', 'F')
    

yes_results, all_games = get_data()
yes_results = calc_outcome(yes_results)
outcome, correct_games, all_games_len = yesterdays_pnl(yes_results)
all_games = combine_games(all_games, yes_results)
dates = find_dates(all_games)
acc0, acc1, acc2, acc3 = print_charts(all_games, dates)
create_pdf(outcome, correct_games, all_games_len, acc3)