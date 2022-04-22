# SquashNZ tournament control with Python

The `pytcnz` library provides abstractions for various data types relevant to Squash New Zealand tournament control. It started out as a subset of [tctools](https://github.com/madduck/tctools), and has been split off in the hope that others might be able to benefit from it.

In addition to abstractions, the library provides access to various data sources, and even a remote controller for iSquash.

Have a look at the [scripts of tctools](https://github.com/madduck/tctools/tree/main/scripts), as well as [tc2web](https://github.com/madduck/tctools/tree/main/tc2web) for inspiration.

## Abstractions

The following abstractions are provided:

* `Phonenumber`, so that invalid phone numbers can be weeded out, and formatting unified;
* `Gender`, because sports are still very gendered, and the gender plays a role in various ways;
* `Scores`, because there are actually quite a bunch of corner cases;
* `Players` and all their data;
* `Draws`, i.e. a collection of players that compete with each other;
* `Games`, i.e. matches between players as part of draws, whether scheduled, or played.

The module also caters to different contexts. Each of the above comes in a very basic form, which is then extended in each of the following contexts:

* `squashnz` — Players get grading list attributes, and an optional age group;
* `dtkapiti` — Players, Draws, and Games specific to DTKapiti's [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) software;
* `tctools` — Players and Draws that are specific to the [DrawMaker](https://github.com/madduck/tctools/tree/main/draw_maker) of [tctools](https://github.com/madduck/tctools).

Here are some simple examples:

```python
# Represent a SquashNZ grade
from pytcnz.squashnz.grading import SquashNZGrading
grading = SquashNZGrading(2870, "M")
print(grading.grade)  # prints 'B2'


# A DrawMaker player
from pytcnz.tctools.player import Player
player = Player(draw="M1", seed=2, name="Martin", gender="M",
                points=2870, dob="1979-02-14", number="0211100938")
print(f'{player.name} plays in {player.draw} as seed {player.seed}')


# A TournamentControl game
from pytcnz.dtkapiti.game import Game
game = Game('M0101', player1='Martin', player2='John', datetime='Thu 8:00pm',
            status=Game.Status.played, comment='11-5 11-6 12-10')
print(f'{game.name} was won by {game.get_winner()} in {game.scores.sets} sets')
```

## Data sources

Instances of the above abstractions can be created using a number of different data sources. Please keep in mind that not every data source provides the same data set. This is largely why there are different types of Players/Draws/Games in different contexts.

The available data sources are all derived from the abstract base class `DataSource`:

* `RegistrationsReader`, which reads `registrations.xls` files, as extractable from iSquash;
* `GradingListReader`, which queries the SquashNZ grading list;
* `TCExportReader`, which parses the Excel file exported by TournamentControl;
* `DrawMakerReader`, which parses all players (registered & waiting list) from a DrawMaker spreadsheet;
* `DrawsReader`, which parses draws as created by the DrawMaker;

Examples:

```python
from pytcnz.dtkapiti.tcexport_reader import TCExportReader
data = TCExportReader('tc-export-fixed.xls')
data.read_all(add_players_to_draws=True)
for draws in data.draws.values():
    print(f'{draw.name} players:')
    for player in draw.players.values():
        print(f'{player.seed:2d}: {player.name}')


from pytcnz.squashnz.gradinglist_reader import GradingListReader
data = GradingListReader()
data.read_players(districts=['WN'], points_min=2700, points_max=3099)
for player in data.players.values():
    print(f'{player.name} from {player.club} has {player.points:,d} points')
```

## iSquash Controller

Finally, pytcnz can make use of [Selenium](https://www.selenium.dev/) to control iSquash, so you don't have to do that manually. In combination with the data sources above, the following functionality is currently possible:

* Make and seed draws as created in the DrawMaker spreadsheet, optionally registering players who aren't yet registered (because they come from the waiting list);
* Bulk-register players matching certain criteria to the waiting list, such that their data becomes available in the DrawMaker;
* Record the scores for played games, and update iSquash diagrams, as well as publish results to the grading list.

# Contributing

Please feel free to contribute and send me your [bug
reports](https://github.com/madduck/pytcnz/issues), or — better yet — [pull
requests](https://github.com/madduck/pytcnz/pulls).

The code is PEP8-compatible (using Flake8), and pretty well test-covered, and I
intend to keep it that way.

# Licence

You are free to use any of the software you find here under the terms of the
MIT License, basically meaning that you can do whatever you want, but you have
to attribute copyright, and include a mention to this licence in whatever you
do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
