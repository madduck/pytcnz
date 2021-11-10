# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..game import Game as BaseGame
from ..squashnz.game_names import get_game_name
from ..datarecord import Placeholder
from ..exceptions import BaseException
from ..scores import Scores
from ..warnings import Warnings
import re
import enum
import dateutil.parser


class Game(BaseGame):
    class InvalidStatusError(BaseException):
        pass

    class InconsistentResultError(BaseException):
        pass

    class ReadError(BaseException):
        pass

    class Status(enum.IntEnum):
        notplayed = -2
        played = -1
        justfinished = 0
        on = 1
        next = 2
        soon = 3
        scheduled = 99
        unknown = 100
        invalid = 101

        @classmethod
        def from_int(cls, _int):
            try:
                return cls(_int)
            except ValueError:
                pass
            if _int > cls.soon and _int < cls.scheduled:
                return cls.soon
            raise Game.InvalidStatusError(f"{_int} is not a valid game status")

        def __str__(self):
            return self.name

    class Reference:
        def __init__(self, from_game):
            self.__winnerloser, self.__from_game = from_game.split()

        def __str__(self):
            return (
                "Winner" if self.__winnerloser == "W" else "Loser"
            ) + f" of {self.__from_game}"

        def __eq__(self, other):
            return (
                self.__from_game == other.__from_game
                and self.__winner == other.__winner
            )

        def __lt__(self, other):
            if self.__from_game == other.__from_game:
                return self.__winner.__lt__(other.__winner)
            else:
                return self.__from_game.__lt__(other.__from_game)

        def __bool__(self):
            return False

        def __hash__(self):
            return str(self).__hash__()

    def __init__(
        self,
        name,
        player1,
        from1,
        score1,
        player2,
        from2,
        score2,
        status,
        *,
        autoflip_scores=False,
        drawnamepat=r"\w\d{1}",
        **kwargs,
    ):
        draw_name = None
        if name is not None and len(name):
            pat = re.compile(rf"(?P<draw>{drawnamepat})")
            md = re.match(pat, name).groupdict()
            draw_name = md.get("draw")
        data = kwargs | dict(draw=Placeholder(name=draw_name))

        player1 = player1 or Game.Reference(from1)
        player2 = player2 or Game.Reference(from2)

        status = Game.Status.from_int(int(status))

        scores = None
        if status <= Game.Status.justfinished:
            if isinstance(player1, Game.Reference) or isinstance(
                player2, Game.Reference
            ):
                raise Game.InvalidStatusError(
                    f"Game {name} is missing a player"
                )

            if not (score1 ^ score2):
                try:
                    if (
                        str(player1).lower() == "bye"
                        or player1.has_defaulted()
                    ):
                        score2 = 1
                        status = Game.Status.notplayed
                except AttributeError:
                    pass

                try:
                    if (
                        str(player2).lower() == "bye"
                        or player2.has_defaulted()
                    ):
                        score1 = 1
                        status = Game.Status.notplayed
                except AttributeError:
                    pass

                if status != Game.Status.notplayed:
                    raise Game.InconsistentResultError(
                        f"Game {name} needs exactly one winner"
                    )

            try:
                scores, unparsed = Scores.from_string(data["comment"])
                if scores:
                    data["comment"] = unparsed

                    if (scores.winner == Scores.Player.A and score2) or (
                        scores.winner == Scores.Player.B and score1
                    ):
                        if autoflip_scores:
                            Warnings.add(
                                f"Scores recorded in wrong order: {scores}",
                                context=f"Reading game {name}",
                            )
                            scores.flip_scores()
                        else:
                            r = "-".join(map(str, (score1, score2)))
                            raise Game.InconsistentResultError(
                                f"Scores don't match result {r}: {scores}"
                            )

            except Scores.BaseException as e:
                raise Game.ReadError(
                    f"While reading scores for game {name}: {e}"
                )

        data |= dict(
            scores=scores,
            score1=score1,
            score2=score2,
            status=status,
            datetime=None,
        )

        datetime = data.get("daytime")
        if datetime:
            try:
                datetime.strftime("")
            except AttributeError:
                # parse into a date starting from next Monday. This is to
                # ensure that when a string like "Thu 7:30pm" is passed to the
                # code run on a Thursday and on a Friday, the result is the
                # same on both.
                data["datetime"] = dateutil.parser.parse(
                    datetime,
                    default=data.get(
                        "tournament_start_date", dateutil.parser.parse("Mon")
                    ),
                )
            del data["daytime"]

        super().__init__(name=name, player1=player1, player2=player2, **data)

    def __repr__(self):
        s = f"<{self.__class__.__name__}({self.name}"
        if self.is_scheduled():
            s = f'{s} on {self.datetime.strftime("%a %H:%M")}'
        s = f'{s}, {self.status}: {" & ".join(map(str, self.players))}'
        if self.is_played():
            s = f"{s}: {self.scores}"
        return f"{s})>"

    def __lt__(self, other):

        s, o = self.get("datetime"), other.get("datetime")

        if s is None and o is None:
            # Sort as if we didn't have datetime
            return super().__lt__(other)
        elif s is None:
            # Unscheduled games always sort after scheduled games:
            return False
        elif o is None:
            # Scheduled games always sort before unscheduled games:
            return True
        elif s != o:
            # Earlier games sort before later games
            return self.datetime.__lt__(other.datetime)

        # Now we're in the situation where two games are scheduled at the
        # same time, which is special, because now we actually want to
        # reverse the sort order so that the "better" games with the lower
        # number show up later, e.g. W0301 is the final, W0304 the consolation
        # plate…
        return BaseGame.__lt__(other, self)

    def get_fancy_name(self, *, drawsize=None, short=False):
        try:
            return get_game_name(
                drawsize=drawsize or self.draw.get_size(),
                gamecode=self.name.replace(self.draw.name, ""),
                short=short,
            )

        except AttributeError:
            return self.name

    def is_scheduled(self):
        return self.get("datetime") is not None and not self.is_finished()

    def is_played(self):
        return self.get_scores() is not None and self.status in (
            Game.Status.played,
            Game.Status.justfinished,
        )

    def is_finished(self):
        return self.status <= Game.Status.justfinished

    def get_winner(self):
        if self.is_played():
            return self.players[self.scores.winner]
        elif self.is_finished():
            return (
                self.players[0]
                if self.score1 > self.score2
                else self.players[1]
            )
        else:
            return None

    def get_scores(self):
        return self.get("scores")


if __name__ == "__main__":
    gd = dict(
        name="W0201",
        player1="",
        player2="Kate",
        from1="W W0101",
        from2="",
        score1=1,
        score2=0,
        status=Game.Status.scheduled,
    )
    g1 = Game(**gd)
    print(vars(g1))
    print(repr(g1))
    print()
    gd.update(datetime=dateutil.parser.parse("Thu 7:30pm"))
    g2 = Game(**gd)
    print(vars(g2))
    print(repr(g2))
    print()
    gd.update(
        name="W0301",
        comment="11-0 11-4 11-3",
        status=Game.Status.played,
        player1="Jane",
    )
    g3 = Game(**gd)
    print(vars(g3))
    print(repr(g3))
    print(g3.get_fancy_name(drawsize=8))
    try:
        import ipdb

        ipdb.set_trace()
    except ImportError:
        pass
