#!/usr/bin/python3
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..datasource import DataSource
from .player import Player
import requests
from urllib.parse import urljoin
import argparse
import time


class GradingListReader(DataSource):

    BASE_URL = "https://www.squash.org.nz/sit/ws/cgl/"

    class RequestError(BaseException):
        pass

    def __init__(self, *, Player_class=None):

        req = requests.get(urljoin(GradingListReader.BASE_URL, "init"))
        self.__config = req.json().get("config")
        if not self.__config:
            raise GradingListReader.RequestError(
                "Failed to read basic grading list data"
            )

        self.genders = self.__config.get("genders")[1:]
        self.gender_choices = sorted(
            self.genders + [f[0].lower() for f in self.genders],
            key=lambda x: x.lower(),
        )
        self.districts = self.__config.get("districts")[1:]
        self.district_choices = [
            d["code"] for d in self.__config.get("districts")[1:]
        ]
        self.clubs = self.__config.get("clubs")[1:]
        self.ages = self.__config.get("ages")[1:]
        self.age_choices = sorted(
            self.ages + [f[0].lower() for f in self.ages],
            key=lambda x: x.lower(),
        )
        self.grades = self.__config.get("grades")[1:]
        self.grade_choices = sorted(
            self.grades + [g.lower() for g in self.grades],
            key=lambda x: x.lower(),
        )

        super().__init__(Player_class=Player_class or Player)

    @classmethod
    def search_grading_list(
        cls,
        *,
        name="",
        gender=None,
        district="All",
        club="All",
        age="Any",
        grade="Any",
    ):

        if not gender:
            gender = "Both"
        else:
            gender = "Male" if gender[0].lower == "m" else "Female"

        if club:
            if district == "All" or district is None:
                district = club[:2]
            else:
                if not club.startswith(district):
                    club = None

        name = name or ""
        club = club or "All"
        district = district or "All"

        if not age:
            age = "Any"  # noqa:E701
        elif age[0].lower() == "j":
            age = "Junior"  # noqa:E701
        elif age[0].lower() == "s":
            age = "Senior"  # noqa:E701
        elif age[0].lower() == "m":
            age = "Masters"  # noqa:E701
        else:
            age = "Any"  # noqa:E701

        if not grade:
            grade = "Any"  # noqa:E701
        elif len(grade) == 1:
            grade = grade.upper()  # noqa:E701

        url = urljoin(cls.BASE_URL, "search")
        sdict = dict(
            name=name,
            gender=gender,
            district=district,
            club=club,
            age=age,
            grade=grade,
        )
        req = requests.post(url, json=sdict)
        return req.json()

    def __get_all_player_dicts(
        self,
        name=None,
        gender=None,
        districts=None,
        clubs=None,
        age=None,
        grade=None,
        points_min=None,
        points_max=None,
        sleep=0,
    ):
        # iSquash limits results to 500, so we iterate by clubs
        first = True
        for club in self.__config["clubs"][1:]:
            c = club["code"]
            d = c[:2]
            if districts and d not in districts:
                continue
            elif clubs and c not in clubs:
                continue

            if first:
                first = False
            else:
                time.sleep(sleep)

            records = GradingListReader.search_grading_list(
                name=name,
                gender=gender,
                district=d,
                club=c,
                age=age,
                grade=grade,
            )

            gd = dict(m=(2,), f=(1,))
            for i in gd.get(gender, range(1, 3)):
                for player in records[f"gradedPlayers{i}"]:

                    if points_min and player["points"] < points_min:
                        continue
                    elif points_max and player["points"] > points_max:
                        continue
                    yield player

    def read_players(
        self,
        *,
        name=None,
        gender=None,
        districts=None,
        clubs=None,
        age=None,
        grade=None,
        points_min=None,
        points_max=None,
        colmap=None,
        sleep=0,
    ):

        colmap = colmap or {}
        colmap["squashcode"] = colmap.get("squashcode", "squash_code")
        colnames = ("id", "name", "gender", "squashCode", "grade", "points")
        records = []
        for player in self.__get_all_player_dicts(
            name=name,
            gender=gender,
            districts=districts,
            clubs=clubs,
            age=age,
            grade=grade,
            points_min=points_min,
            points_max=points_max,
            sleep=sleep,
        ):
            records.append([player[col] for col in colnames])
        records.sort(key=lambda r: r[5], reverse=True)
        super().read_players(colnames, records, colmap=colmap)

    def read_tournament_name(self):
        raise NotImplementedError(
            "The grading list does not provide a tournament name"
        )

    def read_draws(self, *, colmap=None, **kwargs):
        raise NotImplementedError(
            "The grading list does not provide draw data"
        )

    def read_games(self, *, colmap=None, **kwargs):
        raise NotImplementedError(
            "The grading list does not provide game data"
        )

    def read_all(self, *, players_colmap=None):
        self.read_players(colmap=players_colmap)


def make_argument_parser(
    *,
    gender_choices=None,
    district_choices=None,
    club_choices=None,
    age_choices=None,
    grade_choices=None,
    sleep_default=0,
    add_help=False,
    **kwargs,
):

    argparser = argparse.ArgumentParser(add_help=add_help, **kwargs)

    searchg = argparser.add_argument_group(
        title="Searching and limiting",
        description="Specify one or more of these to limit the result set",
    )
    searchg.add_argument(
        "--name", "-n", type=str, help="Search name or parts thereof"
    )
    searchg.add_argument(
        "--gender",
        "-g",
        choices=gender_choices,
        dest="gender",
        help="Limit by district, or districts if specified " "more than once",
    )
    searchg.add_argument(
        "--district",
        "-d",
        action="append",
        choices=district_choices,
        help="Limit by district, or districts if specified " "more than once",
    )
    searchg.add_argument(
        "--club",
        "-c",
        type=str,
        action="append",
        choices=club_choices,
        help="Limit by club, or clubs if specified more than "
        "once (district takes precedence)",
    )
    searchg.add_argument(
        "--age", "-a", choices=age_choices, help="Limit by age group"
    )
    searchg.add_argument(
        "--grade", "-r", choices=grade_choices, help="Limit by age group"
    )
    searchg.add_argument(
        "--minpoints", "-m", type=int, help="Limit by age group"
    )
    searchg.add_argument(
        "--maxpoints", "-x", type=int, help="Limit by age group"
    )
    argparser.add_argument(
        "--sleep",
        "-s",
        type=int,
        default=sleep_default,
        help="Time to wait between API requests",
    )

    return argparser
