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

-- View to create a player standings ordered by wins.
create view playerStandings as
  select p.id,
     p.name,
     coalesce(a.wins, 0) as wins,
     coalesce(a.wins, 0) + coalesce(b.losses, 0) as matchcount
    from
      (select win as id, count(*) as wins from matches group by win) as a
    full join
      (select loss as id, count(*) as losses from matches group by loss) as b
    using (id)
    right join players as p on p.id = a.id or p.id = b.id
  order by wins desc;
