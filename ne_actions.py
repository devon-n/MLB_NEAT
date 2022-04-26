import pickle
import neat
import pandas as pd
import os
import numpy as np
import random

# local_dir = os.path.dirname(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config.txt')
data = pd.read_csv(dir_path + '/auto_files/ne_input.csv')


MAX_BET_SIZE = 10
MIN_ODDS_SIZE = 0
MAX_ODDS_SIZE = 1000

bet_sizes = []
bet_direction = []
no_bets_list = []

# Bet dictionary
bet_dict = {
    0: 'True',
    1: 'False',
    2: 'No Bet'
}


def set_vars():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.txt')
    data = pd.read_csv(dir_path + '/auto_files/ne_input.csv')

    MAX_BET_SIZE = 10
    MIN_ODDS_SIZE = 0
    MAX_ODDS_SIZE = 1000

    bet_sizes = []
    bet_direction = []
    no_bets_list = []

    # Bet dictionary
    bet_dict = {
        0: 'True',
        1: 'False',
        2: 'No Bet'
    }

    return dir_path, data, MAX_BET_SIZE, MAX_ODDS_SIZE, MIN_ODDS_SIZE, bet_sizes, bet_direction, no_bets_list, bet_dict, config_path

def get_questions(data):

    questions_df = data[['Home Odds', 'Vis Odds', 'Predictions']]
    questions_df['P2'] = questions_df['Predictions']
    questions_df['P3'] = questions_df['Predictions']
    questions = questions_df.values.tolist()
    return questions, questions_df

def make_bet(genomes, question, bet_sizes, bet_direction):

    guess = genomes.activate(question[-5:])

    bets = guess[:2]
    bet = int(bets.index(max(bets)))
    bet = bet_dict[bet]
    bet_size = round((guess[3] * 10), 2)

    # Check for upper and lower limit of bet sizes
    bet_size = MAX_BET_SIZE if bet_size > MAX_BET_SIZE else 0 if bet_size < 0 else bet_size

        # Quiz logic
    if (bet == 'True') and (question[0] > MIN_ODDS_SIZE) and (question[0] < MAX_ODDS_SIZE):
        bet = 'True'
    elif (bet == 'False') and (question[1] > MIN_ODDS_SIZE) and (question[1] < MAX_ODDS_SIZE):
        bet = 'False'
    else:
        bet = 'No Bet'
    

    bet_direction.append(bet)
    bet_sizes.append(float(bet_size))

def make_bets(genomes, config, questions):
    for i in range(len(questions)):
        make_bet(genomes, questions[i], bet_sizes, bet_direction)

# Print DF
def print_bets(data, bet_sizes, bet_direction):
    data['Bet Direction'] = bet_direction
    data['Bet Sizes'] = bet_sizes
    
    data.to_csv(dir_path + '/auto_files/betting_actions.csv', index=False)

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
    questions, questions_df = get_questions(data)
    make_bets(net, config, questions)
    print_bets(data, bet_sizes, bet_direction)

if __name__=='__main__':
    # Path to config file
    config_path = os.path.join(dir_path, 'config.txt')

    # Run multiple times
    replay_genome(config_path)