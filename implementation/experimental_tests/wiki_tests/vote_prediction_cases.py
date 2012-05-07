
import CommunityDetection as CD
import pickle

def run_all_wiki(preknowledge=False):
    """ Produces all of the code necessary to generate more votes for wiki
    """
    if not preknowledge:
        wgraph, e_outcome, user_voting_record, user_nomination = CD.wiki_voting()
    else:
        (wgraph, e_outcome, user_voting_record, user_nomination) = preknowledge
    
    seeds = CD.weighted_seeds(wgraph, .49)
    communities = CD.expand_all(wgraph, seeds, 20, 300)
    community_nodes = [c.nodes.keys() for c in communities[0]]
    
    pf = open('05_communities.pkl', 'wb')
    pickle.dump(['Communities produced by expanding weighted seeds',
                 community_nodes],
                pf)
    pf.close()
    
    # Check that communities are a good representation
    guesses = check_votes_agree(wgraph, community_nodes, user_voting_record)
    print "Output counts on checks, ", guesses[:-2]
    print "Was correct ", guesses[1] / float(sum(guesses[:-2]))
    
    predicted_e_votes, added_edges = generate_votes(wgraph,
                                                    community_nodes,
                                                    user_voting_record,
                                                    e_outcome.keys())
    print "Added ", added_edges, " votes."
    
    # Find how the elections turned out in reality
    true_e_votes = CD.user_votes_to_election_record(user_voting_record)
    numeric_e_outcome = {}
    beur_negate = []
    beur_enforce = []
    for e, votes in true_e_votes.iteritems():
        if votes[1] >= .8 * (votes[1] + votes[-1]):
            numeric_e_outcome[e] = 1
            if e_outcome[e] != 1:
                beur_negate.append(e)
                
        else:
            numeric_e_outcome[e] = 0
            if e_outcome[e] != 0:
                beur_enforce.append(e)
                
    true_info = (true_e_votes, numeric_e_outcome, beur_enforce, beur_negate)
            
    # Predict how the elections turned out if more voted
    predicted_e_outcome = {}
    for e, votes in predicted_e_votes.iteritems():
        if votes[1] >= .8 * (votes[1] + votes[-1]):
            predicted_e_outcome[e] = 1
        else:
            predicted_e_outcome[e] = 0
            
    predicted_info = (predicted_e_votes, predicted_e_outcome)
            
    all_info = (wgraph, true_info, predicted_info, user_voting_record,
                user_nomination, communities)
    
    pf = open('info_dump.pkl', 'wb')
    pickle.dump(all_info, pf)
    pf.close()
    
    return all_info
    


def check_votes_agree(wgraph, communities, user_voting_record):
    """ For every node in a community, if other members of the community voted
    checks whether or not our predictive model would agree with how they voted
    Parameters
    ----------
    wgraph : the wiki graph
    communities : a list of lists
    user_voting_record : a dictionary of user votes
    
    Returns
    -------
    no_say : number of votes that could not be verified
    correct_say : the number of votes that were correctly guessed
    wrong_say : the number of votes that were incorrectly guessed
    """
    no_say = 0
    no_guess = 0
    correct_say = 0
    wrong_say = 0
    wrong_data = []
    
    c_votes = [CD.community_to_elections(c, user_voting_record)
               for c in communities]
    
    for n in wgraph:            
        n_communities = filter(lambda i: n in communities[i],
                               range(len(communities)))
        for e in user_voting_record[n].keys():
            c_guess = []
            for i in n_communities:
                if sum(c_votes[i][e].values()) > 1:
                    c_votes[i][e][user_voting_record[n][e]] -= 1
                    c_guess.append(guess_c_vote(c_votes[i][e]))
                    c_votes[i][e][user_voting_record[n][e]] += 1
                
            if len(c_guess) == 0:
                # there were no comparables to use
                no_guess += 1
            else:
                # had a comparable
                guess = guess_n_vote(c_guess)
                #guess = 1
                if guess == None:
                    no_say += 1
                elif guess == user_voting_record[n][e]:
                    correct_say += 1
                else:
                    wrong_data.append((guess, user_voting_record[n][e], c_guess))
                    wrong_say += 1
                
    return no_say, correct_say, wrong_say, no_guess, wrong_data
            
    
def generate_votes(wgraph, communities, user_voting_record, elections):
    """ Generates Votes that would have happened if everyone in a community vote
    Paramemters
    -----------
    communities : a list of lists
    user_voting_record : a dictionary of user votes
    elections : the ids of elections to generate
    """
    e_voting_record = {}
    c_voting_record = [CD.community_to_elections(c, user_voting_record)
                       for c in communities]
    n_communities = {}
    for n in wgraph.nodes():
        n_communities[n] = filter(lambda i: n in communities[i],
                                  range(len(communities)))
    
    predicted = 0
    count = 0
    for e in elections:
        count += 1
        if count%100 == 0:
            print "Predicted", count, "elections"
            
        e_voting_record[e] = {-1:0, 0:0, 1:0}
        for n in wgraph.nodes():
            if e in user_voting_record[n]:
                e_voting_record[e][user_voting_record[n][e]] += 1
            else:
                n_vote = predict_vote(e, n_communities[n], c_voting_record)
                if n_vote != None:
                    predicted += 1
                    e_voting_record[e][n_vote] += 1
                    
    return e_voting_record, predicted
    

def predict_vote(e, communities, c_voting_record):
    """ Predicts how user n voted in election e
    Parameters
    ----------
    e : the election name
    communities : a list of community indices to consider
    c_voting_record : a list of how communities vote
    
    Returns
    -------
    vote : from the set {-1, 0, 1, None}, indicating how n would have voted
    """
    c_guess = []
    for i in communities:
        if e in c_voting_record[i]:
            c_guess.append(guess_c_vote(c_voting_record[i][e]))
        
    return guess_n_vote(c_guess)
        
        
def guess_c_vote(c_votes):
    """ Returns what the community would have voted
    """
    votes = []
    for k, v in c_votes.iteritems():
        votes.extend([k]*v)
        
    return get_popular_vote(votes)
    
    
def guess_n_vote(c_guess):
    """ Given how the communities n is a member of votes, determines n's vote
    Parameters
    ----------
    c_guess : a list of how communities guessed at -1, 0, 1, None
    """
    return get_popular_vote(c_guess)

    
def get_popular_vote(votes):
    """ Returns the most popular vote
    """
    if len(votes) == 0:
        return None
    
    (a, b, c) = (votes.count(1), votes.count(0), votes.count(-1))
    if a == max([a,b,c]):
        return 1
    
    if b == max([a,b,c]):
        return 0
    
    if c == max([a,b,c]):
        return -1
    