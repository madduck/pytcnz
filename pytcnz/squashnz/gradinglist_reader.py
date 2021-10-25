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
import re


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
        self.districts = dict(
            (i["code"], i["desc"]) for i in self.__config.get("districts")[1:]
        )
        self.clubs = dict(
            (i["code"], i["desc"]) for i in self.__config.get("clubs")[1:]
        )
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
        name = name or ""

        if not gender:
            gender = "Both"
        else:
            gender = "Male" if gender[0].lower == "m" else "Female"

        if club and club != "All":
            if district == "All" or district is None:
                district = club[:2]
            else:
                if not club.startswith(district):
                    club = None
        else:
            club = "All"

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

        url = urljoin(GradingListReader.BASE_URL, "search")
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

    def __get_code(self, dict, term):
        if term in dict:
            return term
        for k, v in dict.items():
            if re.search(term, v, re.IGNORECASE):
                return k

    def __get_isquash_records(
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
        if name and not clubs and not districts:
            yield GradingListReader.search_grading_list(
                name=name,
                gender=gender,
                district="All",
                club="All",
                age=age,
                grade=grade,
            )
        else:
            districts = [
                self.__get_code(self.districts, i) for i in districts or []
            ]
            clubs = [
                self.__get_code(self.clubs, i)
                for i in clubs or []
            ]
            # iSquash limits results to 500, so we iterate by clubs
            first = True
            for club in self.clubs:
                district = club[:2]
                if (clubs and club not in clubs) or (
                    districts and district not in districts
                ):
                    continue

                if first:
                    first = False
                else:
                    time.sleep(sleep)

                yield GradingListReader.search_grading_list(
                    name=name,
                    gender=gender,
                    district=district,
                    club=club,
                    age=age,
                    grade=grade,
                )

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
        for records in self.__get_isquash_records(
            name,
            gender,
            districts,
            clubs,
            age,
            grade,
            points_min,
            points_max,
            sleep,
        ):
            gd = dict(m=(2,), f=(1,))
            for i in gd.get(gender, range(1, 3)):
                for player in records[f"gradedPlayers{i}"]:

                    if points_min and player["points"] < points_min:
                        continue
                    elif points_max and player["points"] > points_max:
                        continue
                    player["club"] = self.clubs[player["squashCode"][:4]]
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
        colnames = (
            "id",
            "name",
            "gender",
            "squashCode",
            "grade",
            "points",
            "club",
        )
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
        help="Limit by gender",
    )
    searchg.add_argument(
        "--district",
        "-d",
        action="append",
        help="Limit by district, or districts if specified more than once",
    )
    searchg.add_argument(
        "--club",
        "-c",
        type=str,
        action="append",
        help="Limit by club, or clubs if specified more than "
        "once (district takes precedence)",
    )
    searchg.add_argument(
        "--age", "-a", choices=age_choices, help="Limit by age group"
    )
    searchg.add_argument(
        "--grade", "-r", choices=grade_choices, help="Limit by grade"
    )
    searchg.add_argument(
        "--minpoints",
        "-m",
        type=int,
        help="Only include players above this points limit (inclusive)",
    )
    searchg.add_argument(
        "--maxpoints",
        "-x",
        type=int,
        help="Only include players below this points limit (inclusive)",
    )
    argparser.add_argument(
        "--sleep",
        "-s",
        type=int,
        default=sleep_default,
        help="Time to wait between API requests",
    )

    return argparser
