#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from matches;")
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from players;")
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("select count(*) from players;")
    result = c.fetchone()
    db.close()
    return result[0]

def validMatchups(playerid, wins):
    """Returns valid matchups from player standings and played matchups."""
    db = connect()
    c = db.cursor()
    query = '''select a.id from
                (select id from playerStandings where wins = %s and id != %s) as a
               where a.id not in
                (select opponent from playedMatchups where id = %s);
            '''
    c.execute(query, (wins, playerid, playerid))
    matchups = c.fetchall()
    db.close()
    return matchups

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into players (name) values (%s)", (name,))
    db.commit()
    db.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    c.execute('select * from playerStandings;') # see view in tournament.sql
    standings = c.fetchall()
    db.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into matches (win, loss) values (%s, %s);", (winner, loser))
    db.commit()
    db.close()

def reportBye(playerid):
    """Recors a bye for a player in matches.

    Args:
        playerid: the id number of the player receiving the bye
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into matches (win, bye) values (%s, %s);", (playerid, True))
    db.commit()
    db.close()

def playedMatchups():
    """ All played matchups up to that point in the competition.
    """
    db = connect()
    c = db.cursor()
    c.execute("select * from playedMatchups;")
    matchups = c.fetchall()
    db.close()
    return matchups

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Use player standings to find possible pairings, use already played matchups
    to find ellibible setups (i.e. nobody is paired against the same opponent
    twice.)

    The opponent of a player is picked *randomly* from all elligible opponents:
        - first from players with the same amount of wins
        - second from players with one more win
    Both are conditional on the fact that they have not played against the
    oppnent before.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    playedmatchups = playedMatchups()

    matchups = []
    while len(standings) > 1:
        # pop player from standings, don't consider him for later pairings
        player = standings.pop(-1)
        playerID = player[0]
        playerWins = player[2]

        # player already played against:
        played = [row[1] for row in playedmatchups if row[0] == playerID]

        # opponents that match wins of player
        # check if opponents contains already played people & pick oppenent
        opponents = [row[0] for row in standings if row[2] == playerWins]
        possibilities = [opp for opp in opponents if opp not in played]

        if len(opponents) == 0: # if no opponents with same wins
            # opponents that have 1 more win than player
            opponents = [row[0] for row in standings if row[2] == (playerWins + 1)]
            possibilities = [opp for opp in opponents if opp not in played]

        opponent = random.choice(possibilities)

        # find opponent's standings, add match to matchups
        index_opp = [row[0] for row in standings].index(opponent)
        #index_opp = [i for row, i in enumerate(standings) if row[0] == opponent]
        match = (playerID, player[1], opponent, standings[index_opp][1])
        matchups.append(match)

        # remove opponent from standings table so they won't be paired again.
        del(standings[index_opp])
    return matchups
