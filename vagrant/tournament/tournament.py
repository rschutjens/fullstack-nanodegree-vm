#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def createTournament():
    """Add a new tournament to the database.

        Returns: inserted tournament id
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into tournaments (Tid) values (default) returning Tid;")
    db.commit()
    Tid = c.fetchall()
    db.close()
    return Tid

def deleteTournaments():
    """Removes ALL the tournaments from the database. Including matches,
    byes, and registered_players!"""
    db = connect()
    c = db.cursor()
    c.execute("delete from tournaments;")
    db.commit()
    db.close()

def deleteTournament(Tid):
    """Removes the tournament with Tid from DB, including matches, byes, and
    registed_players
    """
    db = connect()
    c = db.cursor()
    c.execute("delete from tournaments where Tid = %s", (Tid,))
    db.commit()
    db.close()

def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from matches;")
    c.execute("delete from byes;")
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from registered_players;")
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

def validMatchups(Tid, playerid, wins):
    """Returns valid matchups from player standings and played matchups."""
    db = connect()
    c = db.cursor()
    query = '''select a.id from
                (select id from playerStandings where wins = %s and id != %s and Tid = %s) as a
               where a.id not in
                (select opponent from playedMatchups where id = %s and Tid = %s);
            '''
    c.execute(query, (wins, playerid, Tid, playerid, Tid))
    matchups = c.fetchall()
    db.close()
    return matchups

def addPlayer(name):
    """Add player to player database.

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

def applyPlayer(name, Tid):
    """Add player to DB and register for tournament

    Args:
        name: player name.
        Tid: tournament the player will play in.
    """

    db = connect()
    c = db.cursor()
    c.execute("insert into players (name) values (%s) returning id", (name,))
    db.commit()
    pid = c.fetchall()[0][0]
    c.execute("insert into registered_players (Tid, id) values (%s, %s)", (Tid, pid))
    db.commit()
    db.close()

def registerPlayer(Tid, pid):
    """Register a player to the tournament with Tid database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      Tid: the id for the tournament.
      pid: the id of the player participating in tournament Tid.
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into registered_players (Tid, id) values (%s, %s)", (Tid, pid))
    db.commit()
    db.close()

def playerStandings(Tid):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie. After wins the players are
    sorted on OMW, the amount of matches won by their opponents, lastly on
    matches played. For players with the same wins, the one that
    has played stronger opponents will be placed higher, and for player that
    have received a bye to be placed lower if they have the same wins and OMW.

    Args:
        Tid: the id of the tournament you want the player standings of
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        OMW: the number of matches won by opponents of the player
    """
    db = connect()
    c = db.cursor()
    c.execute('select id, name, wins, losses, draws, matchcount, OMW from playerStandings where Tid = %s;', (Tid,)) # see view in tournament.sql
    standings = c.fetchall()
    db.close()
    return standings

def reportMatch(Tid, player1, player2, win = None):
    """Records the outcome of a single match between two players.

    Args:
      Tid: the id of the tournament the match is played in
      player1:  the id number of the first player
      player2:  the id number of the second player
      win: id of player who won, None for draw (default to None if no winner
        is provided)

    """
    db = connect()
    c = db.cursor()
    c.execute("insert into matches (Tid, p1, p2, win) values (%s, %s, %s, %s);", (Tid, player1, player2, win))
    db.commit()
    db.close()

def reportBye(Tid, playerid):
    """Recors a bye for a player in matches.

    Args:
        Tid: the id of tournament the player received the bye
        playerid: the id number of the player receiving the bye
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into byes (Tid, id) values (%s, %s);", (Tid, playerid))
    db.commit()
    db.close()

def playedMatchups(Tid):
    """ All played matchups up to that point in the competition.

    Args:
        Tid: id of tournament you want the playedMatchups of.
    """
    db = connect()
    c = db.cursor()
    c.execute("select * from playedMatchups where Tid = %s;", (Tid,))
    matchups = c.fetchall()
    db.close()
    return matchups

def assignedByes(Tid):
    """ Return all players that have received a bye for tournament Tid.

    Args:
        Tid: tournament you want the byes of.
    """
    db = connect()
    c = db.cursor()
    c.execute("select * from byes where Tid = %s;", (Tid,))
    byes = c.fetchall()
    return byes

def swissPairings(Tid):
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
    opponent before.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(Tid)
    playedmatchups = playedMatchups(Tid)
    byes = [row[1] for row in assignedByes(Tid)]

    # handle byes
    if len(standings) % 2 != 0: # uneven players
        # if first round assign bye at random
        if standings[0][5] == 0:
            bye = random.choice(standings)
        else:
        # assign bye to lowest standing player who has not received one before.
            rev_stands = list(reversed(standings))
            bye = next(row for row in rev_stands if row[0] not in byes)

        # give bye and remove player from standing so he won't get paired
        reportBye(Tid, bye[0])
        index_bye = [row[0] for row in standings].index(bye[0])
        del(standings[index_bye])

    # handle matchups
    matchups = []
    while len(standings) > 1:
        # pop player from standings, don't consider him for later pairings
        player = standings.pop(-1)
        playerID = player[0]
        playerWins = player[2]

        # player already played against, opponents that match wins of players,
        # and check if player played opponent
        played = [row[1] for row in playedmatchups if row[0] == playerID]
        opponents = [row[0] for row in standings if row[2] == playerWins]
        possibilities = [opp for opp in opponents if opp not in played]

        # if no opponents with same wins, check players with 1 more win
        if len(opponents) == 0:
            opponents = [row[0] for row in standings if row[2] == (playerWins + 1)]
            possibilities = [opp for opp in opponents if opp not in played]

        opponent = random.choice(possibilities)

        # find opponent's standings, add match to matchups
        index_opp = [row[0] for row in standings].index(opponent)
        match = (playerID, player[1], opponent, standings[index_opp][1])
        matchups.append(match)

        # remove opponent from standings table so they won't be paired again.
        del(standings[index_opp])
    return matchups
