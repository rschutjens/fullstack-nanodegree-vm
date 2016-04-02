-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;
\c tournament;

-- Contains all tournaments:
create table tournaments (
  Tid serial primary key
);

-- Contains all players and gives them an ID.
create table players (
  id serial primary key,
  name text
);

-- Contains all players registered for a tournament, players can play in
-- multiple tournaments, but register for 1 only once.
create table registered_players (
  id integer references players(id),
  Tid integer references tournaments(Tid),
  primary key (id, Tid)
);

-- Table containing all matches, match ID as players can face off in different
-- matches against eachother, players need to be in players table.
-- win is player id if someone won, or null for draw.
create table matches (
  Tid integer references tournaments(Tid),
  p1 integer references players(id),
  p2 integer references players(id),
  win integer references players(id),
  check ( (win = p1) or (win = p2) or (win is null) ),
  check (p1 <> p2),
  primary key (Tid, p1, p2)
);

-- make sure no duplicated matches are added:
create unique index matchup on matches
  (Tid, greatest(p1, p2), least(p1, p2));

-- a bye is given to one person each round if there is an uneven number of
-- players. This counts as a won match for the player against no opponent.
-- id as primary key ensures on DB level that no player receives 2 byes per
-- tournament.
create table byes (
  Tid integer references tournaments(Tid),
  id integer references players(id),
  primary key (Tid, id)
);

-- view to get all wins and losses of a player, this is used as subset for
-- playerstandings stats and OMW and draws.
create view playersMatchstats as
  select id,
    coalesce(winl, 0) + coalesce(winr, 0) as wins,
    coalesce(lossl, 0) + coalesce(lossr, 0) as losses,
    coalesce(drawl, 0) + coalesce(drawr, 0) as draws
   from
    (select p1 as id,
      sum(case when p1 = win then 1 else 0 end) as winl,
      sum(case when p2 = win then 1 else 0 end) as lossl,
      sum(case when win is null then 1 else 0 end) as drawl
      from matches group by p1) a
    full join
    (select p2 as id,
      sum(case when p2 = win then 1 else 0 end) as winr,
      sum(case when p1 = win then 1 else 0 end) as lossr,
      sum(case when win is null then 1 else 0 end) as drawr
      from matches group by p2) b
    using (id);


-- view to show all played matchups in the tournament per player.
-- as byes count as a match, but there was no matchup, ignore byes.
create view playedMatchups as
  select * from
    (select p1 as id,
      p2 as opponent,
      case when win is null then 1 end as draw
    from matches) as a
  full join
    (select p2 as id,
      p1 as opponent,
      case when win is null then 1 end as draw
    from matches) as b
  using (id, opponent, draw)
  order by id;

-- Opponents Win Matches (OMW) calculation, using playerMatchStats and
-- playedMatchups. Only dependent on matches, should not take into account byes.
create view OMW as
  select player as id,
    sum(wins) as OMW
   from
   (select id as player,
     opponent as id
  from playedMatchups where draw is null) as a
  left join
   (select id,
     wins
  from playersMatchstats) as b
  using (id)
  group by player;

  -- View to create a player standings ordered by wins, matchcount (for byes).
  -- Uses matches table and byes table to determine standings
  create view playerStandings as
  select p.id,
     p.name,
     coalesce(wins, 0) + coalesce(byes, 0) as wins,
     coalesce(losses, 0) as losses,
     coalesce(draws, 0) as draws,
     coalesce(wins, 0) + coalesce(losses, 0) + coalesce (draws, 0 ) as matchcount,
     coalesce(OMW, 0) as OMW
    from
      ((playersMatchstats as a
    full join
      (select id,
        count(id) as byes
      from byes
      group by id) as b
    using(id)) as ab
    full join
      OMW as c
    using (id)) as abc
    right join
    players as p
    using (id)
  order by wins desc, OMW desc, matchcount desc;

-- contains all valid matchups for that point of the tournament: players with
-- equal wins are paired, but not matchups that have already been played.
create view validmatchupsequalwin as
  select a.id as p1,
    b.id as p2
  from
    playerStandings as a
   full join
    playerStandings as b
   on a.wins = b.wins
  where a.id <> b.id
   and (a.id, b.id) not in (select id, opponent from playedMatchups)
  order by p1;

-- contains all valid matchups for that part of the tournament: players with
-- one win or loss difference are paired, already played matchups are filtered
-- out.
create view validmatchupsonediffwin as
  select a.id as p1,
    b.id as p2
  from
    playerStandings as a
   full join
    playerStandings as b
   on (a.wins = b.wins + 1) or (a.wins = b.wins - 1)
  where a.id <> b.id
   and (a.id, b.id) not in (select id, opponent from playedMatchups)
  order by p1;
