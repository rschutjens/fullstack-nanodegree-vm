-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

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
