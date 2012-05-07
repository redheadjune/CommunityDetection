

def community_to_elections(c, user_voting_record):
    """ returns a dictionary of how users in c voted
    Parameters
    ----------
    c : a set of nodes
    user_voting_record : a dictionary keyed on users and valued on their votes
    """
    e_record = {}
    for n in c:
        for e, vote in user_voting_record[n].iteritems():
            if e not in e_record:
                e_record[e] = {-1:0, 0:0, 1:0}
                
            e_record[e][vote] += 1
            
    return e_record

    
def user_votes_to_election_record(user_voting_record):
    """ Turns user_votes into an election voting record
    """
    return community_to_elections(user_voting_record.keys(), user_voting_record)
    