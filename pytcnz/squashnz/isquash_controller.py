#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..exceptions import BaseException
from ..gender import Gender
from ..warnings import Warnings
from ..util import get_timestamp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin
import enum
import bs4
import sys
import re
import bdb
import argparse
import requests
import configparser
import os.path

DRAW_TYPES = {
    "8": "Draw8",
    "16": "Draw16",
    "16no34": "Draw16Sans34",
    "32": "Draw32",
    "4rr": "RoundRobin4",
    "5rr": "RoundRobin5",
    "6rr": "RoundRobin6",
    "6b": "Draw6TypeB",
    "6c": "Draw6TypeC",
    "16swiss": "SwissDraw16",
}


class iSquashController:
    class State(enum.IntEnum):
        init = -1
        ready = 0
        logged_in = 1
        pre_tournament = 2
        registering = 5
        tseeding = 6
        managing = 10
        add_draw = 15
        dseeding = 16
        matches = 17
        results = 90

    class LoginError(BaseException):
        pass

    class NotFoundError(BaseException):
        pass

    class OutOfSequenceError(BaseException):
        def __init__(self, ctrl, state, text=None):
            t = f"{ctrl} not in state {state.name}"
            if text:
                t = f"{t}: {text}"
            BaseException.__init__(self, t)

    class PlayerNameMismatchError(BaseException):
        pass

    class CannotOverwriteError(BaseException):
        pass

    class MissingSelectorError(BaseException):
        pass

    @classmethod
    def __get_firefox_driver(cls, *, headless=False, service_log_path=None):
        profile = webdriver.FirefoxProfile()
        options = webdriver.FirefoxOptions()
        options.headless = headless
        return webdriver.Firefox(
            firefox_profile=profile,
            options=options,
            service_log_path=service_log_path or os.path.devnull,
        )

    def __init__(
        self, *, headless=False, service_log_path=None, pagewait=5, debug=False
    ):
        self.state = self.State.init
        self.driver = iSquashController.__get_firefox_driver(
            headless=headless, service_log_path=service_log_path
        )
        self.state = self.State.ready
        self.driver.implicitly_wait(pagewait)
        self.soup = None
        self.username = None
        self.__debug = debug

    def __repr__(self):
        mxlen = max(len(k) for k in iSquashController.State.__members__.keys())
        r = f"<{self.__class__.__name__}(state={self.state.name:{mxlen+1}s}"

        if self.state >= self.State.logged_in:
            r = f"{r}user={self.username} "

        if self.state >= self.State.pre_tournament:
            r = f"{r}tcode={self.tcode} "

        return f"{r.strip()})>"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.__debug and exc_type not in (KeyboardInterrupt, bdb.BdbQuit):
            try:
                import ipdb

                ipdb.set_trace()
            except ImportError:
                pass
        if self.state >= self.State.logged_in:
            self.go_logout()
        if self.state >= self.State.ready:
            self.driver.quit()

    def get_soup(self):
        return bs4.BeautifulSoup(self.driver.page_source, "html.parser")

    def find_row_by_col_content(tbody, text, *, col=0):
        if not tbody:
            return None, None
        rows = tbody.find_all("tr")
        values = []
        for i, row in enumerate(rows):
            t = row.find_all("td")
            if not t:
                continue
            t = t[col].text.strip()
            try:
                if text.search(t):
                    return i + 1, row
            except AttributeError:
                if text == t:
                    return i + 1, row

            values.append(t)

        return None, values

    def get_row_for_draw(self, draw):
        soup = self.get_soup()
        tbody = soup.find("table", class_="stats_table").find("tbody")

        return iSquashController.find_row_by_col_content(tbody, draw.name)

    def get_row_for_player(self, player):
        soup = self.get_soup()
        tbody = soup.find("table", class_="stats_table").find("tbody")

        pat = iSquashController.make_re_pattern_for_player_name(player.name)
        return iSquashController.find_row_by_col_content(tbody, pat, col=1)

    def select_option(self, id, *, value=None, text=None):
        if value is None and text is None:
            raise iSquashController.MissingSelectorError(
                "Need either a value or an option text."
            )
        elif value is not None and text is not None:
            raise iSquashController.MissingSelectorError(
                "Need either a value or an option text not both."
            )

        # should use selenium.webdriver.support.select.Select!
        soup = self.get_soup()
        select = soup.find(id=id)
        if text:
            option = select.find("option", text=text)
            if not option:
                raise iSquashController.NotFoundError(
                    f"No option found with text {text} in {id}"
                )
            value = option["value"]

        elif value:
            option = select.find("option", value=value)
            if not option:
                raise iSquashController.NotFoundError(
                    f"No option found with value {value} in {id}"
                )

        dropdown = self.driver.find_element(By.ID, id)
        option = dropdown.find_element(By.XPATH, f"./option[@value='{value}']")
        text = option.text
        option.click()

        return value, text

    @classmethod
    def make_re_pattern_for_player_name(cls, name):
        pat = r".*\s+.*".join(name.split())
        return re.compile(pat)

    def go_login(self, username, password):
        if self.state >= self.State.logged_in:
            raise iSquashController.OutOfSequenceError(
                self, self.State.logged_in
            )
        self.driver.get("https://www.squash.org.nz/sit/homepage")
        self.driver.find_element(By.ID, "j_username").send_keys(username)
        self.driver.find_element(By.ID, "j_password").send_keys(password)
        self.driver.find_element(By.ID, "signin_submit").click()

        if "Your login attempt was not successful" in self.driver.page_source:
            raise iSquashController.LoginError(
                f"Invalid credentials for user {username}"
            )

        self.username = username
        self.state = self.State.logged_in

    def go_logout(self):
        if self.state < self.State.logged_in:
            raise iSquashController.OutOfSequenceError(
                self, self.State.logged_in
            )
        url = "https://www.squash.org.nz/sit/j_spring_security_logout"
        self.driver.get(url)
        self.state = self.State.ready
        self.username = None

    def go_manage_tournament(self, tournament_code):
        if self.state < self.State.logged_in:
            raise iSquashController.OutOfSequenceError(
                self, self.State.logged_in
            )

        self.driver.get("https://www.squash.org.nz/sit/tournament/home")

        soup = self.get_soup()
        tbody = soup.find(id="listTournamentEventsForm:tournaments_data")

        rowx, row = iSquashController.find_row_by_col_content(
            tbody, tournament_code
        )

        if rowx is None:
            raise iSquashController.NotFoundError(
                f"No {tournament_code} in {row}"
            )

        url = row.find("a", text="View").get("href")
        url = urljoin(self.driver.current_url, url)
        self.driver.get(url)

        self.tcode = tournament_code
        self.state = self.State.pre_tournament

    def go_pre_tournament(self):
        if self.state < self.State.logged_in:
            raise iSquashController.OutOfSequenceError(
                self, self.State.pre_tournament
            )

        elif self.state == self.State.pre_tournament:
            return

        self.driver.find_element(
            By.XPATH, "//input[@value='Pre Tournament']"
        ).click()

        self.state = self.State.pre_tournament

    def go_clear_registrations(self, player_cb=None):
        self.go_pre_tournament()

        self.driver.find_element(
            By.XPATH, "//input[@value='List Registrations']"
        ).click()

        try:
            i = 2
            while True:
                row = self.driver.find_element(
                    By.XPATH,
                    f"//*[@id='listRegistrantsForm']/table/tbody/tr[{i}]",
                )

                player = row.find_element(By.XPATH, ".//td[2]").text
                button = row.find_element(
                    By.XPATH, ".//input[@value='Delete']"
                )
                if button.get_property("disabled"):
                    if player_cb:
                        player_cb(
                            player,
                            removed=False,
                            msg="Player is assigned to a draw",
                        )
                    i += 1
                    continue

                button.click()
                wait = WebDriverWait(self.driver, 10)
                wait.until(expected_conditions.alert_is_present())
                self.driver.switch_to.alert.accept()
                WebDriverWait(self.driver, 60).until(
                    expected_conditions.invisibility_of_element(button)
                )
                if player_cb:
                    player_cb(player)

        except NoSuchElementException:
            pass

    def go_fill_registrations(self, players, *, update=False, player_cb=None):
        self.go_pre_tournament()

        self.driver.find_element(
            By.XPATH, "//input[@value='List Registrations']"
        ).click()

        to_register = []
        for player in players:
            rowx, row = self.get_row_for_player(player)
            if rowx is None:
                to_register.append(player)
                continue
            elif update:
                self.driver.find_element(
                    By.XPATH,
                    "//*[@id='listRegistrantsForm']"
                    f"/table/tbody/tr[{rowx}]/td[7]"
                    "/input[@value='Edit']",
                ).click()
                try:
                    comments = player.comments
                except AttributeError:
                    pass
                else:
                    el = self.driver.find_element(
                        By.ID, "makeTournamentRegistration:" "comment"
                    )
                    el.clear()
                    el.send_keys(comments)

                self.driver.find_element(
                    By.ID, "makeTournamentRegistration:" "enterTournament"
                ).click()

            if player_cb:
                player_cb(player, False)

        for player in to_register:
            self.go_register_player(
                player,
                player_cb=player_cb,
                default_comment=f"Bulk-registered by {self.username} "
                f"on {get_timestamp()}",
            )

    def go_register_player(
        self, player, *, player_cb=None, default_comment=None
    ):
        if (
            self.state < self.State.pre_tournament
            or self.state > self.State.registering
        ):
            raise iSquashController.OutOfSequenceError(
                self, self.State.registering
            )

        elif self.state != self.State.registering:
            self.driver.find_element(
                By.XPATH, "//input[@value='Register Player']"
            ).click()
            self.state = self.State.registering

        wait = WebDriverWait(self.driver, 10)

        inp = self.driver.find_element(
            By.ID, "makeTournamentRegistration:" "playingPartner_input"
        )
        inp.clear()
        inp.send_keys(player.squash_code)
        try:
            wait.until(
                expected_conditions.visibility_of_element_located(
                    (By.ID, "makeTournamentRegistration:playingPartner_panel")
                )
            )
            choices = self.driver.find_elements(
                By.XPATH,
                "//*[@id='makeTournamentRegistration:"
                "playingPartner_panel']//li",
            )
            pat = iSquashController.make_re_pattern_for_player_name(
                player.name
            )
            for choice in choices:
                isqname = choice.get_attribute("data-item-label")
                if pat.search(isqname):
                    choice.click()
                    break
        except TimeoutException:
            msg = (
                "iSquash does not know a player with code "
                f"{player.squash_code}"
            )
            Warnings.add(msg, context="Registering players")
            if player_cb:
                player_cb(player, added=False, error=True, msg=msg)
            return

        def check_for_player_id_input(driver):
            el = driver.find_element(
                By.XPATH,
                "//*[@id='makeTournamentRegistration:"
                "playingPartner_hinput']",
            )
            return len(el.get_attribute("value"))

        wait.until(check_for_player_id_input)

        self.driver.find_element(
            By.ID, "makeTournamentRegistration:" "addPlayer"
        ).click()

        email = player.get("email")
        if email:
            el = self.driver.find_element(
                By.ID, "makeTournamentRegistration:email"
            )
            el.clear()
            el.send_keys(email)

        comments = player.get("comments", default_comment)
        if comments:
            el = self.driver.find_element(
                By.ID, "makeTournamentRegistration:comment"
            )
            el.clear()
            el.send_keys(comments)

        self.driver.find_element(
            By.ID, "makeTournamentRegistration:enterTournament"
        ).click()

        add_btn = self.driver.find_element(
            By.ID, "makeTournamentRegistration:addPlayer"
        )
        if add_btn.get_property("disabled"):
            msg = self.driver.find_element(
                By.XPATH, '//*[@id="j_idt156"]/div/ul/li/span'
            )
            if player_cb:
                player_cb(player, added=False, error=True, msg=msg.text)
            self.driver.find_element(
                By.XPATH, "//input[@value='Register Player']"
            ).click()

        else:
            if player_cb:
                player_cb(player, added=True, msg=isqname)

    def go_design_tournament(self):
        if self.state < self.State.pre_tournament:
            raise iSquashController.OutOfSequenceError(
                self, self.State.pre_tournament
            )

        elif self.state == self.State.managing:
            self.driver.refresh()
            return

        self.driver.find_element(
            By.XPATH, "//input[@value='Design/Manage Tournament']"
        ).click()

        self.state = self.State.managing

    def go_seed_tournament(self):
        self.go_pre_tournament()

        self.driver.find_element(
            By.XPATH, "//input[@value='Seed Tournament']"
        ).click()
        self.state = self.State.tseeding

        self.driver.find_element(
            By.XPATH,
            "//*[@id='seedTournamentForm']//input[@value='Seed Tournament']",
        ).click()

        wait = WebDriverWait(self.driver, 10)
        wait.until(expected_conditions.alert_is_present())
        self.driver.switch_to.alert.accept()

    def _go_extract_spreadsheet(self, filename, btndict):
        self.go_design_tournament()

        form = self.driver.find_element(By.ID, "toolbarForm")

        viewstate = self.driver.find_element(
            By.ID, "j_id1:javax.faces.ViewState:0"
        )
        jsessionid = self.driver.get_cookie("JSESSIONID")
        response = requests.post(
            urljoin(self.driver.current_url, form.get_attribute("action")),
            data=btndict
            | {
                "toolbarForm": "toolbarForm",
                "javax.faces.ViewState": viewstate.get_attribute("value"),
            },
            headers={"Referer": self.driver.current_url},
            cookies={"JSESSIONID": jsessionid["value"]},
        )
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def go_extract_registrations(self, filename):
        self._go_extract_spreadsheet(
            filename, {"toolbarForm:j_idt145": "Extract Registrations"}
        )

    def go_extract_draws(self, filename):
        self._go_extract_spreadsheet(
            filename, {"toolbarForm:j_idt147": "Extract Draws"}
        )

    def go_delete_draws(self, draws=None, *, draw_cb=None):
        self.go_design_tournament()

        try:
            i = 1
            while True:
                row = self.driver.find_element(
                    By.XPATH, f"//*[@id='drawForm']/table/tbody/tr[{i}]"
                )

                draw = row.find_element(By.XPATH, ".//td[1]").text
                if draws and draw not in draws:
                    i += 1
                    continue
                button = row.find_element(
                    By.XPATH, ".//input[@value='Delete']"
                )
                button.click()
                wait = WebDriverWait(self.driver, 10)
                wait.until(expected_conditions.alert_is_present())
                self.driver.switch_to.alert.accept()
                WebDriverWait(self.driver, 60).until(
                    expected_conditions.invisibility_of_element(button)
                )
                if draw_cb:
                    draw_cb(draw)

        except NoSuchElementException:
            pass

    def go_add_draw(self, draw, drawtype, *, drawdesc=None):
        self.go_design_tournament()

        rowx, row = self.get_row_for_draw(draw)
        if rowx is None:
            self.driver.find_element(
                By.XPATH, "//input[@value='Add Draw']"
            ).click()
            self.state = self.State.add_draw

            option = DRAW_TYPES[drawtype]
            self.select_option("AddDrawForm:typeOfDraw", value=option)

            if draw.gendered == Gender.W:
                option = "Womens"
            elif draw.gendered == Gender.M:
                option = "Mens"
            else:
                option = "Mixed"
            self.select_option("AddDrawForm:MenWomen", value=option)

            self.driver.find_element(By.ID, "AddDrawForm:drawName").send_keys(
                draw.name
            )
            self.driver.find_element(
                By.ID, "AddDrawForm:drawDescription"
            ).send_keys(drawdesc or draw.description)
            self.driver.find_element(By.ID, "AddDrawForm:addDraw").click()
            self.state = self.State.managing

    def go_seed_draw(self, draw, *, player_cb=None):
        self.go_design_tournament()

        rowx, row = self.get_row_for_draw(draw)
        if rowx is None:
            if row:
                raise iSquashController.NotFoundError(
                    f"Draw {draw.name} not in {row}"
                )
            else:
                raise iSquashController.NotFoundError(
                    f"Draw {draw.name} does not exist"
                )

        self.driver.find_element(
            By.XPATH,
            f"//*[@id='drawForm']/table/tbody/tr[{rowx}]"
            "/td[4]/input[@value='Seed Draw']",
        ).click()
        self.state = self.State.dseeding

        self.driver.execute_script(
            """
            els = document.getElementsByTagName('select');
            for (let i = 0; i < els.length; ++i) {
                els[i].setAttribute('onchange', '');
            }
            """
        )

        for i, player in enumerate(draw.players):
            pat = iSquashController.make_re_pattern_for_player_name(
                player.name
            )
            try:
                val, isqname = self.select_option(
                    f"AddDrawForm:Items:{i}:players", text=pat
                )
                isqname = isqname.split("(")[0].strip()
                if player_cb:
                    player_cb(i, player, isqname)
            except iSquashController.NotFoundError:
                Warnings.add(
                    f"No iSquash player found for {player}",
                    context=f"Populating draw {draw}, position {i+1}",
                )
                if player_cb:
                    player_cb(i, player, "NO REGISTERED PLAYER")

        self.driver.find_element(
            By.XPATH, '//*[@id="AddDrawForm"]/input[@value="Save"]'
        ).click()
        self.state = self.State.managing

    def go_make_matches_for_draw(self, draw):
        self.go_design_tournament()

        rowx, row = self.get_row_for_draw(draw)
        if rowx is None:
            raise iSquashController.NotFoundError(
                f"Draw {draw.name} not in {row}"
            )

        self.driver.find_element(
            By.XPATH,
            f"//*[@id='drawForm']/table/tbody/tr[{rowx}]"
            "/td[4]/input[@value='Matches']",
        ).click()
        self.state = self.State.matches

        self.driver.find_element(
            By.XPATH,
            '//*[@id="addDrawForm"]/' 'input[@value="Initialise Matches"]',
        ).click()
        self.state = self.State.managing

    def go_update_web_diagram(self):
        self.go_design_tournament()

        self.driver.find_element(
            By.XPATH,
            '//*[@id="toolbarForm"]/div/div[2]/'
            'input[@value="Update Web Diagram"]',
        ).click()

    def go_enter_results_for_draw(self, draw, *, done=None, reset=False):
        self.go_design_tournament()

        rowx, row = self.get_row_for_draw(draw)
        if rowx is None:
            raise iSquashController.NotFoundError(
                f"Draw {draw.name} not in {row}"
            )

        self.driver.find_element(
            By.XPATH,
            f"//*[@id='drawForm']/table/tbody/tr[{rowx}]"
            "/td[4]/input[@value='Results']",
        ).click()
        self.state = self.State.results

        soup = self.get_soup()
        tbody = soup.find("table", class_="stats_table").find("tbody")

        done = done or []
        entered = []
        for game in draw.get_games():
            if game in done:
                print(f"    skip: {game!r}", file=sys.stderr)
                continue

            rowx, row = iSquashController.find_row_by_col_content(
                tbody, game.name, col=1
            )

            if rowx is None:
                raise iSquashController.NotFoundError(
                    f"Game {game.name} not in {row}"
                )

            tr_xpath = f"//*[@id='myForm']/table/tbody/tr[{rowx}]"

            scorecell1 = self.driver.find_element(
                By.XPATH, f"{tr_xpath}/td[5]/input"
            )
            if scorecell1.get_attribute("disabled"):
                # iSquash is not ready to receive our scores yet, whether we
                # have them or not.
                print(f"    skip: {game!r}", file=sys.stderr)
                continue

            if reset:
                print(f"    rset: {game!r}", file=sys.stderr)
            else:
                print(f"          {game!r}", file=sys.stderr)

            scores = list(game.get_scores()) if not reset else list()
            for i in range(len(scores), 5):
                scores.append((0, 0))

            for player in (0, 1):
                isqname = row.find_all("td")[2 + player].text
                pname = game.players[player]
                for name in pname.split():
                    if name.lower() not in isqname.lower():
                        raise iSquashController.PlayerNameMismatchError(
                            f"While entering results for {game}: "
                            f"{pname} is not {isqname}"
                        )

            for gamenr, score in enumerate(scores):
                for player in (0, 1):
                    cell = self.driver.find_element(
                        By.XPATH,
                        f"{tr_xpath}/td[5+{gamenr*2}+{player}]" "/input",
                    )
                    cell.clear()
                    cell.send_keys(str(score[player]))

            entered.append(game)

        self.driver.find_element(
            By.XPATH, '//*[@id="myForm"]/input[@value="Save"]'
        ).click()
        self.state = self.State.managing

        return entered

    def go_send_to_gradinglist(self):
        self.go_design_tournament()

        btn = self.driver.find_element(
            By.XPATH,
            '//*[@id="toolbarForm"]/div/div[2]'
            '/input[@value="Publish to Grading"]',
        )
        btn.click()

        wait = WebDriverWait(self.driver, 10)
        wait.until(expected_conditions.alert_is_present())
        self.driver.switch_to.alert.accept()

        msg = self.driver.find_element(
            By.XPATH, '//*[@id="j_idt157"]/div/ul/li/span'
        )
        print(msg.text, file=sys.stderr)


def make_argument_parser(add_help=False, *, configfile=None, **kwargs):

    argparser = argparse.ArgumentParser(add_help=add_help, **kwargs)
    defaults = {}
    if configfile:
        config = configparser.ConfigParser()
        config.read(configfile)
        if config.has_section("iSquash"):
            defaults = dict(config["iSquash"])
            argparser.set_defaults(**defaults)

    isqgroup = argparser.add_argument_group(
        title="iSquash interaction",
        description="Data required to interact with iSquash",
    )
    isqgroup.add_argument(
        "--username",
        "-u",
        metavar="USERNAME",
        required="username" not in defaults,
        help="iSquash user name for login",
    )
    isqgroup.add_argument(
        "--password",
        "-p",
        metavar="PASSWORD",
        required="password" not in defaults,
        help="iSquash password for login",
    )
    isqgroup.add_argument(
        "--tournament",
        "-t",
        metavar="TOURNAMENT_CODE",
        required="tournament" not in defaults,
        help="iSquash tournament code",
    )

    runtimeg = argparser.add_argument_group(title="Runtime control")
    runtimeg.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        help="Drop into debugger on error",
    )
    runtimeg.add_argument(
        "--headless",
        action="store_true",
        dest="headless",
        help="Operate without a browser window (invisible)",
    )

    return argparser
