"""
Factory for generating sample data for the mock FOGIS API server.

This module provides a factory class that can generate various types of sample data
that mimic the responses from the FOGIS API, with proper structure but anonymized content.
"""

import json
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class MockDataFactory:
    """Factory for generating sample data for the mock FOGIS API server."""

    @staticmethod
    def generate_id() -> int:
        """Generate a random ID."""
        return random.randint(1000000, 9999999)

    @staticmethod
    def generate_match_number() -> str:
        """Generate a random match number."""
        return f"{random.randint(0, 999999):06d}"

    @staticmethod
    def generate_name(first_name: bool = True) -> str:
        """Generate a random name."""
        if first_name:
            names = [
                "John",
                "Jane",
                "Alex",
                "Sam",
                "Chris",
                "Pat",
                "Taylor",
                "Morgan",
                "Jordan",
                "Casey",
            ]
            return random.choice(names)
        else:
            surnames = [
                "Smith",
                "Johnson",
                "Williams",
                "Brown",
                "Jones",
                "Miller",
                "Davis",
                "Garcia",
                "Rodriguez",
                "Wilson",
            ]
            return random.choice(surnames)

    @staticmethod
    def generate_full_name() -> str:
        """Generate a random full name."""
        return f"{MockDataFactory.generate_name(True)} {MockDataFactory.generate_name(False)}"

    @staticmethod
    def generate_team_name() -> str:
        """Generate a random team name."""
        prefixes = [
            "FC",
            "United",
            "City",
            "Athletic",
            "Sporting",
            "Real",
            "Inter",
            "Dynamo",
        ]
        locations = [
            "North",
            "South",
            "East",
            "West",
            "Central",
            "Metro",
            "Royal",
            "Olympic",
        ]
        return f"{random.choice(locations)} {random.choice(prefixes)}"

    @staticmethod
    def generate_phone() -> str:
        """Generate a random phone number."""
        return f"07{random.randint(0, 9)}{random.randint(0, 9)}-{random.randint(100000, 999999)}"

    @staticmethod
    def generate_email(name: Optional[str] = None) -> str:
        """Generate a random email address."""
        if name is None:
            name = MockDataFactory.generate_full_name().lower().replace(" ", ".")
        domains = ["example.com", "test.org", "sample.net", "mock.io", "demo.se"]
        return f"{name}@{random.choice(domains)}"

    @staticmethod
    def generate_address() -> str:
        """Generate a random address."""
        streets = ["Main St", "Park Ave", "Oak Rd", "Maple Ln", "Cedar Blvd"]
        return f"{random.randint(1, 999)} {random.choice(streets)}"

    @staticmethod
    def generate_postal_code() -> str:
        """Generate a random postal code."""
        return f"{random.randint(10000, 99999)}"

    @staticmethod
    def generate_city() -> str:
        """Generate a random city name."""
        cities = [
            "Springfield",
            "Rivertown",
            "Lakeside",
            "Mountainview",
            "Valleyfield",
            "Brookhaven",
        ]
        return random.choice(cities)

    @staticmethod
    def generate_date(future: bool = True, days_offset: Optional[int] = None) -> str:
        """Generate a random date in YYYY-MM-DD format."""
        if days_offset is None:
            days_offset = random.randint(1, 180) if future else -random.randint(1, 180)

        date = datetime.now() + timedelta(days=days_offset)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def generate_time() -> str:
        """Generate a random time in HH:MM format."""
        hours = random.randint(10, 20)
        minutes = random.choice([0, 15, 30, 45])
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def generate_timestamp(future: bool = True, days_offset: Optional[int] = None) -> int:
        """Generate a random timestamp in milliseconds."""
        if days_offset is None:
            days_offset = random.randint(1, 180) if future else -random.randint(1, 180)

        date = datetime.now() + timedelta(days=days_offset)
        return int(date.timestamp() * 1000)

    @staticmethod
    def generate_formatted_timestamp(future: bool = True, days_offset: Optional[int] = None) -> str:
        """Generate a random timestamp in FOGIS format."""
        timestamp = MockDataFactory.generate_timestamp(future, days_offset)
        return f"\\/Date({timestamp})\\/"

    @staticmethod
    def generate_match_list(count: int = 5) -> Dict[str, Any]:
        """Generate a sample match list response."""
        matches = []

        for _ in range(count):
            match_id = MockDataFactory.generate_id()
            match_number = MockDataFactory.generate_match_number()
            home_team = MockDataFactory.generate_team_name()
            away_team = MockDataFactory.generate_team_name()
            competition = f"Division {random.randint(1, 5)}"
            match_date = MockDataFactory.generate_date(True)
            match_time = MockDataFactory.generate_time()

            # Generate referee information
            referees = []
            for role_id, role_name, role_short in [
                (1, "Huvuddomare", "Dom"),
                (2, "Assisterande 1", "AD1"),
                (3, "Assisterande 2", "AD2"),
            ]:
                referee_name = MockDataFactory.generate_full_name()
                referees.append(
                    {
                        "domaruppdragid": MockDataFactory.generate_id(),
                        "matchid": match_id,
                        "matchnr": match_number,
                        "domarrollid": role_id,
                        "domarrollnamn": role_name,
                        "domarrollkortnamn": role_short,
                        "domareid": MockDataFactory.generate_id(),
                        "domarnr": str(random.randint(10000, 99999)),
                        "personid": MockDataFactory.generate_id(),
                        "domaruppdragstatusid": 5,
                        "domaruppdragstatusnamn": "Tilldelat",
                        "personnamn": referee_name,
                        "telefon": "",
                        "mobiltelefon": MockDataFactory.generate_phone(),
                        "telefonarbete": "",
                        "adress": MockDataFactory.generate_address(),
                        "coadress": "",
                        "epostadress": MockDataFactory.generate_email(
                            referee_name.lower().replace(" ", ".")
                        ),
                        "land": "Sverige",
                        "namn": referee_name,
                        "postnr": MockDataFactory.generate_postal_code(),
                        "postort": MockDataFactory.generate_city(),
                    }
                )

            # Generate contact persons
            contacts = []
            for team_name in [home_team, away_team]:
                for is_reserve in [False, True]:
                    contact_name = MockDataFactory.generate_full_name()
                    contacts.append(
                        {
                            "lagid": MockDataFactory.generate_id(),
                            "lagnamn": f"{team_name}",
                            "personid": MockDataFactory.generate_id(),
                            "personnamn": contact_name,
                            "telefon": "",
                            "mobiltelefon": MockDataFactory.generate_phone(),
                            "telefonarbete": "",
                            "adress": MockDataFactory.generate_address(),
                            "coadress": "",
                            "epostadress": MockDataFactory.generate_email(
                                contact_name.lower().replace(" ", ".")
                            ),
                            "land": "Sverige",
                            "postnr": MockDataFactory.generate_postal_code(),
                            "postort": MockDataFactory.generate_city(),
                            "reserv": is_reserve,
                            "foreningId": MockDataFactory.generate_id(),
                        }
                    )

            # Create the match object
            match = {
                "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchJSON",
                "value": match_number,
                "label": (
                    f"{match_number}: {home_team} - {away_team} ({competition}), "
                    f"{match_date} {match_time}"
                ),
                "matchid": match_id,
                "matchnr": match_number,
                "fotbollstypid": 1,
                "matchlag1id": MockDataFactory.generate_id(),
                "lag1lagengagemangid": MockDataFactory.generate_id(),
                "lag1lagid": MockDataFactory.generate_id(),
                "lag1foreningid": MockDataFactory.generate_id(),
                "lag1forbundid": 0,
                "lag1namn": home_team,
                "lag1spelsystem": "4-4-2",
                "matchlag2id": MockDataFactory.generate_id(),
                "lag2lagengagemangid": MockDataFactory.generate_id(),
                "lag2lagid": MockDataFactory.generate_id(),
                "lag2foreningid": MockDataFactory.generate_id(),
                "lag2forbundid": 0,
                "lag2namn": away_team,
                "lag2spelsystem": "4-3-3",
                "anlaggningid": MockDataFactory.generate_id(),
                "anlaggningnamn": (
                    f"{random.choice(['Arena', 'Stadium', 'Park'])} " f"{random.randint(1, 5)}"
                ),
                "anlaggningLatitud": round(57.0 + random.random(), 6),
                "anlaggningLongitud": round(12.0 + random.random(), 6),
                "tid": MockDataFactory.generate_formatted_timestamp(True),
                "speldatum": match_date,
                "avsparkstid": match_time,
                "tidsangivelse": f"{match_date}, {match_time}",
                "tavlingid": MockDataFactory.generate_id(),
                "tavlingnr": match_number[:6],
                "tavlingnamn": competition,
                "tavlingskategoriid": MockDataFactory.generate_id(),
                "tavlingskategorinamn": f"Division {random.randint(1, 5)}",
                "tavlingagsavforbundid": 1,
                "matchlag1mal": random.randint(0, 5),
                "matchlag2mal": random.randint(0, 5),
                "arslutresultat": random.choice([True, False]),
                "wo": False,
                "ow": False,
                "ww": False,
                "antalaskadare": random.randint(0, 2000),
                "uppskjuten": False,
                "avbruten": False,
                "installd": False,
                "matchrapportgodkandavdomare": random.choice([True, False]),
                "matchrapportgodkandavdomaredatum": (
                    MockDataFactory.generate_formatted_timestamp(False)
                    if random.choice([True, False])
                    else "\\/Date(-62135596800000)\\/"
                ),
                "matchrapportgodkandavdomaredatumformaterad": "",
                "tavlinganvanderhogupplosttid": False,
                "tavlingantalstartadespelareigodkanddomarrapport": 11,
                "tavlingmaxantalspelareimatchtruppigodkanddomarrapport": 18,
                "tavlingantalledareimatchtrupp": 7,
                "tavlingantalspelareimatchtrupp": 18,
                "antalhalvlekar": 2,
                "tidperhalvlek": 45,
                "antalforlangningsperioder": 0,
                "tidperforlangningsperiod": 0,
                "liverapporteringTillaten": True,
                "liverapporteringPaborjad": False,
                "liverapporteringAvslutad": False,
                "liverapporteringsAktorTypId": 2,
                "anvanderspelarleg": False,
                "foreningsanvandarefarredigeramotstandartrupp": True,
                "foreningsanvandarefarregistreramatchhandelser": False,
                "foreningsanvandarefarregistreramatchresultat": False,
                "domaruppdraglista": referees,
                "domarefargodkannarapport": True,
                "domarrapporteringTillaten": True,
                "noteringfranlag1": "",
                "noteringfranlag2": "",
                "noteringfrandomare": "",
                "tavlingFriaByten": False,
                "tavlingDomareMojliggorHamtningAvFrammandeSpelareTillMatchtrupp": True,
                "tavlingAntalTimmarInnanMatchForTruppAdministration": 45,
                # Require responsible team leader
                "tavlingDomareKravForekomstAvAnsvarigLagledareIGodkandDomarrapport": True,
                "tavlingAntalDagarEfterMatchForAdministrationAvDomarrapport": 3,
                "tavlingKonId": 2,
                "tavlingAlderskategori": 4,
                "kontaktpersoner": contacts,
                # Match squad publication time for home team
                "matchlag1OffentliggorMatchtruppDatumTid": (
                    MockDataFactory.generate_formatted_timestamp(True)
                ),
                # Match squad publication time for away team
                "matchlag2OffentliggorMatchtruppDatumTid": (
                    MockDataFactory.generate_formatted_timestamp(True)
                ),
                "tavlingDomareAntalMinuterForeMatchSomTrupperOffentliggors": 45,
                # Additional fields
                "domareArHuvuddomare": True,
                "tavlingMatchklimatDomareKanLamnaOmdome": False,
                # Match climate settings
                "tavlingDomareVisaVarningsOchAvstangningsAckumulering": True,
            }

            matches.append(match)

        # Create the full response structure
        response = {
            "d": {
                "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatcherAttRapportera",
                "anvandartyp": "Domare",
                "anvandareforeningid": 0,
                "matchlista": matches,
                "anvandare": None,
                "endastLiverapportor": False,
            }
        }

        return response

    @staticmethod
    def generate_match_details(match_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate sample match details."""
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match_number = MockDataFactory.generate_match_number()
        home_team = MockDataFactory.generate_team_name()
        away_team = MockDataFactory.generate_team_name()
        match_date = MockDataFactory.generate_date(True)
        match_time = MockDataFactory.generate_time()

        match_details = {
            "matchid": match_id,
            "matchnr": match_number,
            "datum": match_date,
            "tid": match_time,
            "hemmalag": home_team,
            "bortalag": away_team,
            "hemmalagid": MockDataFactory.generate_id(),
            "bortalagid": MockDataFactory.generate_id(),
            "arena": f"{random.choice(['Arena', 'Stadium', 'Park'])} {random.randint(1, 5)}",
            "status": "Fastställd",
            "domare": MockDataFactory.generate_full_name(),
            "ad1": MockDataFactory.generate_full_name(),
            "ad2": MockDataFactory.generate_full_name(),
            "fjarde": "",
            "matchtyp": "Serie",
            "tavling": f"Division {random.randint(1, 5)}",
            "grupp": f"Group {random.choice(['A', 'B', 'C', 'D'])}",
            "hemmamal": random.randint(0, 5),
            "bortamal": random.randint(0, 5),
            "publik": random.randint(100, 2000),
            "notering": "",
            "rapportstatus": "Ej påbörjad",
            "matchstart": None,
            "halvtidHemmamal": random.randint(0, 3),
            "halvtidBortamal": random.randint(0, 3),
        }

        return match_details

    @staticmethod
    def generate_match_players(
        match_id: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample match players."""
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        home_players = []
        away_players = []

        # Generate home team players
        for i in range(18):
            is_captain = i == 0
            position_id = 1 if i == 0 else (2 if i < 5 else (3 if i < 10 else 4))
            position = (
                "Målvakt"
                if position_id == 1
                else (
                    "Försvarare"
                    if position_id == 2
                    else ("Mittfältare" if position_id == 3 else "Anfallare")
                )
            )

            player = {
                "personid": MockDataFactory.generate_id(),
                "fornamn": MockDataFactory.generate_name(True),
                "efternamn": MockDataFactory.generate_name(False),
                "smeknamn": None,
                "tshirt": str(i + 1),
                "position": position,
                "positionid": position_id,
                "lagkapten": is_captain,
                "spelareid": MockDataFactory.generate_id(),
                "licensnr": "".join(random.choices(string.ascii_uppercase, k=3))
                + "".join(random.choices(string.digits, k=3)),
            }

            home_players.append(player)

        # Generate away team players
        for i in range(18):
            is_captain = i == 0
            position_id = 1 if i == 0 else (2 if i < 5 else (3 if i < 10 else 4))
            position = (
                "Målvakt"
                if position_id == 1
                else (
                    "Försvarare"
                    if position_id == 2
                    else ("Mittfältare" if position_id == 3 else "Anfallare")
                )
            )

            player = {
                "personid": MockDataFactory.generate_id(),
                "fornamn": MockDataFactory.generate_name(True),
                "efternamn": MockDataFactory.generate_name(False),
                "smeknamn": None,
                "tshirt": str(i + 1),
                "position": position,
                "positionid": position_id,
                "lagkapten": is_captain,
                "spelareid": MockDataFactory.generate_id(),
                "licensnr": "".join(random.choices(string.ascii_uppercase, k=3))
                + "".join(random.choices(string.digits, k=3)),
            }

            away_players.append(player)

        return {
            "hemmalag": home_players,
            "bortalag": away_players,
        }

    @staticmethod
    def generate_match_officials(
        match_id: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample match officials."""
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        home_officials = []
        away_officials = []

        # Generate home team officials
        for _, (role_id, role) in enumerate(
            [(1, "Tränare"), (2, "Assisterande tränare"), (3, "Lagledare")]
        ):
            official = {
                "personid": MockDataFactory.generate_id(),
                "fornamn": MockDataFactory.generate_name(True),
                "efternamn": MockDataFactory.generate_name(False),
                "roll": role,
                "rollid": role_id,
            }

            home_officials.append(official)

        # Generate away team officials
        for _, (role_id, role) in enumerate(
            [(1, "Tränare"), (2, "Assisterande tränare"), (3, "Lagledare")]
        ):
            official = {
                "personid": MockDataFactory.generate_id(),
                "fornamn": MockDataFactory.generate_name(True),
                "efternamn": MockDataFactory.generate_name(False),
                "roll": role,
                "rollid": role_id,
            }

            away_officials.append(official)

        return {
            "hemmalag": home_officials,
            "bortalag": away_officials,
        }

    @staticmethod
    def generate_match_events(
        match_id: Optional[int] = None, count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate sample match events."""
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        events = []
        home_score = 0
        away_score = 0

        for _ in range(count):
            # Determine event type
            event_types = [
                (6, "Mål"),  # Goal
                (1, "Gult kort"),  # Yellow card
                (2, "Rött kort"),  # Red card
                (7, "Byte"),  # Substitution
            ]
            event_code, event_type = random.choice(event_types)

            # Determine team (home or away)
            is_home_team = random.choice([True, False])
            team_id = MockDataFactory.generate_id()
            team_name = f"{'Home' if is_home_team else 'Away'} Team"

            # Determine minute
            minute = random.randint(1, 90)
            period = 1 if minute <= 45 else 2

            # Create player names
            player_name = f"Player {random.randint(1, 20)}"
            assisting_player = (
                f"Player {random.randint(1, 20)}" if event_code == 6 or event_code == 7 else None
            )

            # Update score for goals
            if event_code == 6:
                if is_home_team:
                    home_score += 1
                else:
                    away_score += 1

            # Create the event
            event = {
                "matchhandelseid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "handelsekod": event_code,
                "handelsetyp": event_type,
                "minut": minute,
                "lagid": team_id,
                "lag": team_name,
                "personid": MockDataFactory.generate_id(),
                "spelare": player_name,
                "period": period,
            }

            # Add goal-specific fields
            if event_code == 6:
                event["mal"] = True
                event["resultatHemma"] = home_score
                event["resultatBorta"] = away_score
                event["assisterande"] = assisting_player
                event["assisterandeid"] = MockDataFactory.generate_id()

            # Add substitution-specific fields
            if event_code == 7:
                event["assisterande"] = assisting_player
                event["assisterandeid"] = MockDataFactory.generate_id()

            events.append(event)

        return events

    @staticmethod
    def generate_match_result(match_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate sample match result."""
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        home_goals = random.randint(0, 5)
        away_goals = random.randint(0, 5)
        halftime_home = min(home_goals, random.randint(0, 3))
        halftime_away = min(away_goals, random.randint(0, 3))

        result = {
            "matchid": match_id,
            "hemmamal": home_goals,
            "bortamal": away_goals,
            "halvtidHemmamal": halftime_home,
            "halvtidBortamal": halftime_away,
        }

        return result

    @staticmethod
    def get_sample_match_list_response() -> str:
        """Get a sample match list response as a JSON string."""
        match_list = MockDataFactory.generate_match_list()
        return json.dumps(match_list)

    @staticmethod
    def get_sample_match_details_response() -> str:
        """Get a sample match details response as a JSON string."""
        match_details = MockDataFactory.generate_match_details()
        return json.dumps({"d": json.dumps(match_details)})

    @staticmethod
    def get_sample_match_players_response() -> str:
        """Get a sample match players response as a JSON string."""
        match_players = MockDataFactory.generate_match_players()
        return json.dumps({"d": json.dumps(match_players)})

    @staticmethod
    def get_sample_match_officials_response() -> str:
        """Get a sample match officials response as a JSON string."""
        match_officials = MockDataFactory.generate_match_officials()
        return json.dumps({"d": json.dumps(match_officials)})

    @staticmethod
    def get_sample_match_events_response() -> str:
        """Get a sample match events response as a JSON string."""
        match_events = MockDataFactory.generate_match_events()
        return json.dumps({"d": json.dumps(match_events)})

    @staticmethod
    def get_sample_match_result_response() -> str:
        """Get a sample match result response as a JSON string."""
        match_result = MockDataFactory.generate_match_result()
        return json.dumps({"d": json.dumps(match_result)})


# Sample data for the mock server
SAMPLE_MATCH_LIST = MockDataFactory.generate_match_list()
SAMPLE_MATCH = MockDataFactory.generate_match_details()
SAMPLE_MATCH_PLAYERS = MockDataFactory.generate_match_players()
SAMPLE_MATCH_OFFICIALS = MockDataFactory.generate_match_officials()
SAMPLE_MATCH_EVENTS = MockDataFactory.generate_match_events()
SAMPLE_MATCH_RESULT = MockDataFactory.generate_match_result()


if __name__ == "__main__":
    # Print sample data
    print("Sample Match List:")
    print(json.dumps(SAMPLE_MATCH_LIST, indent=2))

    print("\nSample Match Details:")
    print(json.dumps(SAMPLE_MATCH, indent=2))

    print("\nSample Match Players:")
    print(json.dumps(SAMPLE_MATCH_PLAYERS, indent=2))

    print("\nSample Match Officials:")
    print(json.dumps(SAMPLE_MATCH_OFFICIALS, indent=2))

    print("\nSample Match Events:")
    print(json.dumps(SAMPLE_MATCH_EVENTS, indent=2))

    print("\nSample Match Result:")
    print(json.dumps(SAMPLE_MATCH_RESULT, indent=2))
