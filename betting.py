import pickle
import neat
import pandas as pd
import os
import numpy as np
import random

local_dir = os.path.dirname(__file__)

data = pd.read_csv('NE_input_df.csv')
# data = pd.read_csv('Current Stats and Games.csv')

MAX_BET_SIZE = 10
MIN_ODDS_SIZE = 1.6
MAX_ODDS_SIZE = 2
N_TIMES = 50
QUIZ_LENGTH = 50
# QUIZ_START = random.randint(1, len(data) - QUIZ_LENGTH)

bet_sizes = []
bet_direction = []
no_bets_list = []
outcomes = []
cumsums = []


# Bet dictionary
bet_dict = {
    0: 'True',
    1: 'False',
    2: 'No Bet'
}


def get_questions(data):

    QUIZ_START = random.randint(1, len(data) - QUIZ_LENGTH)
    questions_df = data[['Home Odds', 'Vis Odds', 'Current Preds', 'Prev Preds', 'Ensemble', 'Home Win']]
    questions_df = questions_df.iloc[QUIZ_START:(QUIZ_START + QUIZ_LENGTH)]

    output_df = questions_df.copy()
    questions = questions_df.values.tolist()
    return questions, questions_df


def make_bet(genomes, question, bet_sizes, bet_direction):

    outcome = 0
    answer = question[-1]
    guess = genomes.activate(question[:5])
    # guess is an array of 4
    # [0] = Home bet, [1] = Away bet, [2] =  No bet, [3] = bet size

    # Find H, A or NB
    bets = guess[:2]
    bet = int(bets.index(max(bets)))
    bet = bet_dict[bet]
    bet_size = round((guess[3] * 10), 2)

    # Check for upper and lower limit of bet sizes
    bet_size = MAX_BET_SIZE if bet_size > MAX_BET_SIZE else 0 if bet_size < 0 else bet_size

    # Quiz logic
    if (bet == 'True') and (str(answer) == 'True') and (question[0] > MIN_ODDS_SIZE) and (question[0] < MAX_ODDS_SIZE):
        outcome += (question[0] * bet_size) - bet_size
    elif (bet == 'False') and (str(answer) == 'False') and (question[1] > MIN_ODDS_SIZE) and (question[1] < MAX_ODDS_SIZE):
        outcome += (question[1] * bet_size) - bet_size
    elif (bet == 'No Bet') or (bet == 'True' and question[0] <= MIN_ODDS_SIZE) or (bet == 'False' and question[1] <= MIN_ODDS_SIZE) \
        or (bet == 'True' and question[0] >= MAX_ODDS_SIZE) or (bet == 'False' and question[1] >= MAX_ODDS_SIZE):
        outcome = 0
        no_bets_list.append(bet)
    else:
        outcome -= bet_size

    bet_direction.append(bet)
    bet_sizes.append(float(bet_size))
    outcomes.append(outcome)


def make_bets(genomes, config, questions):
    for i in range(len(questions)):
        make_bet(genomes, questions[i], bet_sizes, bet_direction)


def print_df(questions, bet_direction, bet_sizes, outcomes):

    # Copy DF
    outcome_df = pd.DataFrame()
    outcome_df[['Home Odds', 'Vis Odds', 'Home Win']] = questions[['Home Odds', 'Vis Odds', 'Home Win']]

    # Add necessary columns
    outcome_df['Bet Direction'] = bet_direction
    outcome_df['Bet Sizes'] = bet_sizes
    outcome_df['Outcome'] = outcomes
    outcome_df['Bankroll'] = outcome_df['Outcome'].cumsum()

    # Print and save ending balance
    ending_balance = outcome_df['Bankroll'].values[-1]
    print('Ending Balance: ', ending_balance)
    cumsums.append(ending_balance)

    # Print out csv
    outcome_df.to_csv('Future Bets to Make.csv', index=False)

    # Clear Columns/Arrays
    outcome_df.drop(['Bet Direction', 'Bet Sizes', 'Outcome', 'Bankroll'], axis=1, inplace=True)
    
    bet_sizes.clear()
    bet_direction.clear()
    no_bets_list.clear()
    outcomes.clear()




# Make bets
def replay_genome(config_path, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]
    net = neat.nn.FeedForwardNetwork.create(genome, config)


    # Call game with only the loaded genome
    for _ in range(N_TIMES):
        questions, questions_df = get_questions(data)
        make_bets(net, config, questions)
        print_df(questions_df, bet_direction, bet_sizes, outcomes)




if __name__=='__main__':
    # Path to config file
    config_path = os.path.join(local_dir, 'config.txt')

    # Run multiple times
    replay_genome(config_path)
    cumsums_mean = str(np.mean(cumsums))
    str_n_times = str(N_TIMES)
    print("Mean bankroll after " + str_n_times + " times : " + cumsums_mean)
    