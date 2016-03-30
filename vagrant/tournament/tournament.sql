-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;
\c tournament;

-- Contains all players and gives them an ID.
create table players (
  id serial primary key,
  name text
);

-- Table containing all matches, match ID as players can face off in different
-- matches against eachother, players need to be in players table.

create table matches (
  id serial primary key,
  win integer references players(id),
  loss integer references players(id)
);

-- a bye is given to one person each round if there is an uneven number of
-- players. This counts as a won match for the player against no opponent.
-- id as primary key ensures on DB level that no player receives 2 byes.
create table byes (
  id integer references players(id),
  primary key (id)
);

-- View to create a player standings ordered by wins, matchcount (for byes).
-- Uses matches table and byes table to determine standings
create view playerStandings as
  select p.id,
     p.name,
     abc.wins + coalesce(byes, 0) as wins,
     abc.wins + abc.losses as matchcount,
     coalesce(abc.OMW, 0) as OMW
    from
      ((playersMatchstats as a
    full join
      (select id, count(id) as byes from byes group by id) as b
    using(id)) as ab
    full join
      OMW as c
    using (id)) as abc
    right join players as p on p.id = abc.id
  order by wins desc, OMW desc, matchcount desc;

-- view to get all wins and losses of a player, this is used as subset for
-- playerstandings stats and OMW
create view playersMatchstats as
  select ab.id,
    coalesce(ab.wins, 0) as wins,
    coalesce(ab.losses, 0) as losses
   from
    ((select win as id, count(*) as wins from matches group by win) as a
  full join
    (select loss as id, count(*) as losses from matches group by loss) as b
  using (id)) as ab;


-- view to show all played matchups in the tournament per player.
-- as byes count as a match, but there was no matchup, ignore byes.
create view playedMatchups as
  select * from
    (select win as id, loss as opponent from matches) as a
  full join
    (select loss as id, win as opponent from matches) as b
  using (id, opponent)
  order by id;

-- Opponents Win Matches (OMW) calculation, using playerMatchStats and
-- playedMatchups. Only dependent on matches, should not take into account byes.
create view OMW as
  select ab.player as id,
    sum(ab.wins) as OMW
   from
   ((select id as player, opponent as id from playedMatchups) as a
  full join
   (select id, wins from playersMatchstats) as b
  using (id)) as ab
  group by ab.player
