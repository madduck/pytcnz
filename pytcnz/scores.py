# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .exceptions import BaseException
import re
import enum


class Scores:
    class Player(enum.IntEnum):
        A = 0
        B = 1

    class BaseException(BaseException):
        pass

    class IncompleteError(BaseException):
        pass

    @classmethod
    def __parse_string(cls, string):
        SET_DELIMS = r" ,"
        GAME_DELIMS = r"-/:"  # '-' must be first
        string = re.sub(rf"\s*([{GAME_DELIMS}])\s*", r"\1", string)
        sets = [
            s.strip(SET_DELIMS) for s in re.split(rf"[{SET_DELIMS}]+", string)
        ]
        ret = []
        unp = []
        for s in sets:
            # as soon as we fail to parse scores, append the remainder to the
            # unparsed string, which we return as well as the scores
            if unp:
                unp.append(s)
                continue
            try:
                ret.append(
                    tuple(map(int, re.split(rf"[{GAME_DELIMS}]+", s, 1)))
                )
            except ValueError:
                unp.append(s)

        if ret:
            return ret, SET_DELIMS[0].join(unp)
        else:
            return None, string

    @classmethod
    def from_string(cls, string, *, bestof=5, par=(11, 15)):
        scores, remainder = cls.__parse_string(string)
        if scores:
            return cls(scores, bestof=bestof, par=par), remainder
        else:
            return None, remainder

    def __init__(self, sets=None, *, bestof=5, par=(11, 15)):
        try:
            bestof + 1
            bestof = (bestof,)  # noqa:E701,E702
        except TypeError:
            bestof = bestof or (5,)  # noqa:E701
        try:
            par + 1
            par = (par,)  # noqa:E701,E702
        except TypeError:
            par = par or (11, 15)  # noqa:E701

        self._sets = sets or []
        self._bestof = bestof
        self._par = par
        self._winner = None

        self.__verify_scores()

    def __verify_scores(self):
        min_games = [int(cnt / 2 + 1) for cnt in self.bestof]
        max_games = self.bestof

        if len(self._sets) < min(min_games):
            raise Scores.IncompleteError(
                f"At least {min(min_games)} sets must be played"
            )
        elif len(self._sets) > max(max_games):
            raise Scores.IncompleteError(
                f"At most {max(max_games)} sets can be played"
            )

        cntA, cntB = 0, 0
        maxpar = 0
        for i, (a, b) in enumerate(self._sets, 1):
            if (
                (a - b > 2 and a not in self._par)
                or (a - b == 2 and a < min(self._par))
                or (a - b == 1)
                or (b - a == 1)
                or (b - a > 2 and b not in self._par)
                or (b - a == 2 and b < min(self._par))
            ):
                raise Scores.IncompleteError(
                    f"{a}-{b} did not reach any PAR in {self.par} in set {i}"
                )

            cntA += 1 if a > b else 0
            cntB += 1 if b > a else 0

            if a - b > 2:
                maxpar = a  # noqa:E271,E701
            elif b - a > 2:
                maxpar = b  # noqa:E271,E701

        if cntA == cntB:
            raise Scores.IncompleteError(f"No winner at {cntA}-{cntB}")

        if cntA == 0 and cntB not in min_games:
            raise Scores.IncompleteError(
                f"Cannot lose 0-{cntB} in best-of {self.bestof}"
            )
        elif cntB == 0 and cntA not in min_games:
            raise Scores.IncompleteError(
                f"Cannot win {cntA}-0 in best-of {self.bestof}"
            )

        for i, (a, b) in enumerate(self._sets, 1):
            if (a > b and a < maxpar) or (b > a and b < maxpar):
                raise Scores.IncompleteError(
                    f"{a}-{b} did not reach PAR {maxpar} in set {i}"
                )

        self._winner = Scores.Player.A if cntA > cntB else Scores.Player.B
        self._games_score = (cntA, cntB)

    winner = property(lambda s: s._winner)
    bestof = property(lambda s: s._bestof)
    par = property(lambda s: s._par)

    def get_scores(self):
        if self._sets:
            return " ".join(f"{a}-{b}" for a, b in self._sets)
        else:
            return None

    def get_games_score(self):
        return "-".join(map(str, self._games_score))

    def flip_scores(self):
        if self._winner == Scores.Player.A:
            self._winner = Scores.Player.B
        elif self._winner == Scores.Player.B:
            self._winner = Scores.Player.A
        self._sets = [(b, a) for (a, b) in self._sets]
        self._games_score = self._games_score[::-1]

    def __str__(self):
        return self.get_scores()

    def __repr__(self):
        s = (
            f"<{self.__class__.__name__}({self!s}, "
            f'best-of={",".join(map(str,self.bestof))}, '
            f'par={",".join(map(str,self.par))}'
        )
        if self.winner:
            s = f"{s}: {self.winner.name} won {self.get_games_score()}"
        return f"{s})>"

    def __eq__(self, other):
        return self._sets == other._sets

    def __len__(self):
        return len(self._sets)

    def __iter__(self):
        return iter(self._sets)

    def __getitem__(self, nset):
        return self._sets[nset]


if __name__ == "__main__":
    print(repr(Scores.from_string("11-6 6-11 11-8 8-11 10-12")))
