#!/usr/bin/env python
#
# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.

from tournament import *
import itertools

def testFirstRound():
    '''
    Fill DB with players and first round to efficiently test pairings queries
    and functions.
    '''
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    Tid = createTournament()[0][0]
    applyPlayer("Twilight Sparkle", Tid)
    applyPlayer("Fluttershy", Tid)
    applyPlayer("Applejack", Tid)
    applyPlayer("Pinkie Pie", Tid)
    applyPlayer("Rarity", Tid)
    applyPlayer("Rainbow Dash", Tid)
    applyPlayer("Princess Celestia", Tid)
    applyPlayer("Princess Luna", Tid)
    standings = playerStandings(Tid)
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(Tid, id1, id2, id1)
    reportMatch(Tid, id3, id4, id3)
    reportMatch(Tid, id5, id6, id5)
    reportMatch(Tid, id7, id8, id7)
    return Tid

def testFirstRoundUneven():
    '''
    Fill DB with players and first round to efficiently test pairings queries and functions.
    '''
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    Tid = createTournament()[0][0]

    applyPlayer("Twilight Sparkle", Tid)
    applyPlayer("Fluttershy", Tid)
    applyPlayer("Applejack", Tid)
    applyPlayer("Pinkie Pie", Tid)
    applyPlayer("Rarity", Tid)
    applyPlayer("Rainbow Dash", Tid)
    applyPlayer("Princess Celestia", Tid)
    applyPlayer("Princess Luna", Tid)
    applyPlayer("Brad Split", Tid)
    standings = playerStandings(Tid)
    [id1, id2, id3, id4, id5, id6, id7, id8, id9] = [row[0] for row in standings]
    reportMatch(id1, id2, id1)
    reportMatch(id3, id4, id3)
    reportMatch(id5, id6, id5)
    reportMatch(id7, id8, id7)
    reportBye(id9)


def testCount():
    """
    Test for initial player count,
             player count after 1 and 2 players registered,
             player count after players deleted.
    """
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deletion, countPlayers should return zero.")
    print "1. countPlayers() returns 0 after initial deletePlayers() execution."
    addPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1. Got {c}".format(c=c))
    print "2. countPlayers() returns 1 after one player is registered."
    addPlayer("Jace Beleren")
    c = countPlayers()
    if c != 2:
        raise ValueError(
            "After two players register, countPlayers() should be 2. Got {c}".format(c=c))
    print "3. countPlayers() returns 2 after two players are registered."
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError(
            "After deletion, countPlayers should return zero.")
    print "4. countPlayers() returns zero after registered players are deleted.\n5. Player records successfully deleted."

def testStandingsBeforeMatches():
    """
    Test to ensure players are properly represented in standings prior
    to any matches being reported.
    """
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    Tid = createTournament()[0][0]
    applyPlayer("Melpomene Murray", Tid)
    applyPlayer("Randy Schwartz", Tid)
    standings = playerStandings(Tid)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 7:
        raise ValueError("Each playerStandings row should have seven columns.")
    [(id1, name1, wins1, losses1, draws1, matches1, OMW1), (id2, name2, wins2, losses2, draws2, matches2, OMW2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."

def testReportMatches():
    """
    Test that matches are reported properly.
    Test to confirm matches are deleted properly.
    """
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    Tid = createTournament()[0][0]
    applyPlayer("Bruno Walton", Tid)
    applyPlayer("Boots O'Neal", Tid)
    applyPlayer("Cathy Burton", Tid)
    applyPlayer("Diane Grant", Tid)
    standings = playerStandings(Tid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(Tid, id1, id2, id1)
    reportMatch(Tid, id3, id4, id3)
    standings = playerStandings(Tid)
    for (i, n, w, l, d, m, o) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3):
            if w != 1:
                raise ValueError("Each match winner should have one win recorded.")
            elif o != 0:
                raise ValueError("A match winner should have 0 OMW after one match.")
        elif i in (id2, id4):
            if w != 0:
                raise ValueError("Each match loser should have zero wins recorded.")
            elif o != 1:
                raise ValueError("A match loser should have 1 OMW after one match")
    print "7. After a match, players have updated standings."
    deleteMatches()
    standings = playerStandings(Tid)
    if len(standings) != 4:
        raise ValueError("Match deletion should not change number of players in standings.")
    for (i, n, w, l, d, m, o) in standings:
        if m != 0:
            raise ValueError("After deleting matches, players should have zero matches recorded.")
        if w != 0:
            raise ValueError("After deleting matches, players should have zero wins recorded.")
    print "8. After match deletion, player standings are properly reset.\n9. Matches are properly deleted."

def testPairings():
    """
    Test that pairings are generated properly both before and after match reporting.
    """
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    Tid = createTournament()[0][0]

    applyPlayer("Twilight Sparkle", Tid)
    applyPlayer("Fluttershy", Tid)
    applyPlayer("Applejack", Tid)
    applyPlayer("Pinkie Pie", Tid)
    applyPlayer("Rarity", Tid)
    applyPlayer("Rainbow Dash", Tid)
    applyPlayer("Princess Celestia", Tid)
    applyPlayer("Princess Luna", Tid)
    applyPlayer("Brad Split", Tid)
    standings = playerStandings(Tid)
    pairings = swissPairings(Tid)
    byes = assignedByes(Tid)
    byeidr1 = byes[0][1]
    [(id1, name1, id2, name2), (id3, name3, id4, name4), (id5, name5, id6, name6), (id7, name7, id8, name8)] = pairings
    #[id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    if len(byes) != 1:
        raise ValueError(
            "No bye assigned for first round, got {byecount}".format(byecount=len(byes)))
    if len(pairings) != 4:
        raise ValueError(
            "For nine players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))
    reportMatch(Tid, id1, id2, id1)
    reportMatch(Tid, id3, id4, id3)
    reportMatch(Tid, id5, id6, id5)
    reportMatch(Tid, id7, id8, id7)

    # checking for right pairings, need to be more strict than for 8 players
    standings = playerStandings(Tid)
    win_set = set([row[0] for row in standings if row[2] == 1])
    loss_set = set([row[0] for row in standings if row[2] == 0])
    win_comb = itertools.combinations(win_set, 2)
    win_comb = set([frozenset(row) for row in win_comb])
    loss_comb = itertools.combinations(loss_set, 2)
    loss_comb = set([frozenset(row) for row in loss_comb])
    prod_comb = itertools.product(win_set, loss_set)
    prod_comb = set([frozenset(row) for row in prod_comb])

    pairings = swissPairings(Tid)
    byes = assignedByes(Tid)
    if len(byes) != 2:
        raise ValueError(
            "No bye assigned for second round, got {byecount}".format(byecount=len(byes)))
    if len(pairings) != 4:
        raise ValueError(
            "For nine players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))

    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings

    # old method for 8 players
    # possible_pairs = set([frozenset([id1, id3]), frozenset([id1, id5]),
    #                       frozenset([id1, id7]), frozenset([id3, id5]),
    #                       frozenset([id3, id7]), frozenset([id5, id7]),
    #                       frozenset([id2, id4]), frozenset([id2, id6]),
    #                       frozenset([id2, id8]), frozenset([id4, id6]),
    #                       frozenset([id4, id8]), frozenset([id6, id8])
    #                       ])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), frozenset([pid5, pid6]),frozenset([pid7, pid8])])

    win_sets = list(actual_pairs.intersection(win_comb))
    print 'Matches of last round winners:', win_sets
    if len(win_sets) != 2:
        raise ValueError(
            """For 9 players after first round at least 2 matches should be
            between last rounds winners, got {}""".format(len(win_sets)))

    loss_sets = list(actual_pairs.intersection(loss_comb))
    print 'Matches of last round losers',loss_sets
    if len(loss_sets) != 1:
        raise ValueError(
            """For 9 players after first round at least 1 match should be
            between last rounds losers, got {}""".format(len(loss_sets)))

    prod_sets = list(actual_pairs.intersection(prod_comb))
    print 'Matches between a winner and loser:', prod_sets
    if len(prod_sets) != 1:
        raise ValueError(
            """For 9 players after first round at 1 match should be
            between a winner and loser, got {}""".format(len(prod_sets)))
    # for pair in actual_pairs:
    #     if pair not in possible_pairs:
    #         raise ValueError(
    #             "After one match, players with one win should be paired.")
    print "10. After one match, players are properly paired."


if __name__ == '__main__':
    testCount()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"
