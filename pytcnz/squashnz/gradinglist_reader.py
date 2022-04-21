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
        elif term.upper() in dict:
            return term.upper()

        for k, v in dict.items():
            if re.search(term, v, re.IGNORECASE):
                return k

    def __iterate_grades_ages(
        self,
        *,
        name=None,
        district=None,
        club=None,
        ages=None,
        grades=None,
        sleep=0,
        first=True,
    ):
        male, female = [], []
        for grade in grades or ["Any"]:
            for age in ages or ["Any"]:
                if first:
                    first = False
                else:
                    time.sleep(sleep)

                ret = GradingListReader.search_grading_list(
                    name=name,
                    district=district,
                    club=club,
                    age=age,
                    grade=grade,
                )
                female.extend(ret['gradedPlayers1'])
                male.extend(ret['gradedPlayers2'])

        return female, male


    def __get_isquash_records(
        self,
        *,
        name=None,
        districts=None,
        clubs=None,
        ages=None,
        grades=None,
        sleep=0,
    ):
        if name and not clubs and not districts:
            return self.__iterate_grades_ages(
                name=name,
                ages=ages,
                grades=grades,
                sleep=sleep,
            )

        else:
            districts = [
                self.__get_code(self.districts, i) for i in districts or []
            ]
            clubs = [self.__get_code(self.clubs, i) for i in clubs or []]
            # iSquash limits results to 500, so we iterate by clubs
            first = True
            male, female = [], []
            for club in self.clubs:
                district = club[:2]
                if False and district == 'WN':
                    import ipdb; ipdb.set_trace()  # noqa:E402,E702
                if (clubs and (club not in clubs)) or (
                    districts and (district not in districts)
                ):
                    continue

                ret = self.__iterate_grades_ages(
                    name=name,
                    district=district,
                    club=club,
                    ages=ages,
                    grades=grades,
                    sleep=sleep,
                    first=first,
                )
                female.extend(ret[0])
                male.extend(ret[1])

            return female, male

    def __get_all_player_dicts(
        self,
        name=None,
        genders=None,
        districts=None,
        clubs=None,
        ages=None,
        grades=None,
        points_min=None,
        points_max=None,
        sleep=0,
    ):
        female, male = self.__get_isquash_records(
            name=name,
            districts=districts,
            clubs=clubs,
            ages=ages,
            grades=grades,
            sleep=sleep,
        )

        for gender, players in (("f", female), ("m", male)):
            if genders and (gender not in genders):
                continue

            for player in players:
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
        genders=None,
        districts=None,
        clubs=None,
        ages=None,
        grades=None,
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
            genders=genders,
            districts=districts,
            clubs=clubs,
            ages=ages,
            grades=grades,
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
        type=str,
        action="append",
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
        "--age",
        "-a",
        choices=age_choices,
        type=str,
        action="append",
        help="Limit by age group (can be given more than once)",
    )
    searchg.add_argument(
        "--grade",
        "-r",
        choices=grade_choices,
        type=str,
        action="append",
        help="Limit by grade (can be given more than once)",
    )
    searchg.add_argument(
        "--minpoints",
        type=int,
        help="Only include players above this points limit (inclusive)",
    )
    searchg.add_argument(
        "--maxpoints",
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
