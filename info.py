import datetime
from dataclasses import dataclass

import aoe_api


class GameInfo:
    strings = aoe_api.get_strings()

    ages = {element['id']: element['string'] for element in strings['age']}
    civilizations = {element['id']: element['string'] for element in strings['civ']}
    game_types = {element['id']: element['string'] for element in strings['game_type']}
    leaderboards = {element['id']: element['string'] for element in strings['leaderboard']}
    map_sizes = {element['id']: element['string'] for element in strings['map_size']}
    map_types = {element['id']: element['string'] for element in strings['map_type']}
    rating_types = {element['id']: element['string'] for element in strings['rating_type']}
    resources = {element['id']: element['string'] for element in strings['resources']}
    speed = {element['id']: element['string'] for element in strings['speed']}
    victory = {element['id']: element['string'] for element in strings['victory']}
    visibility = {element['id']: element['string'] for element in strings['visibility']}


class Match:
    def __init__(self, profile_id: str, match_id: str, ranked: bool, leaderboard_id: int, rating_type: int, server: str,
                 started: int, finished: int, players: list, map_type: int):
        self.participants = []
        self.id = match_id
        self.ranked = ranked
        self.leaderboard = GameInfo.leaderboards[leaderboard_id]
        self.rating_type = GameInfo.rating_types[rating_type]
        self.map = GameInfo.map_types[map_type]
        self.server = server
        self.started = datetime.datetime.fromtimestamp(started)
        self.finished = datetime.datetime.fromtimestamp(finished)
        duration_in_seconds = datetime.timedelta.total_seconds(self.finished - self.started)
        self.duration = int(duration_in_seconds / 60)
        self._add_participants(players)
        self.set_won_flag(profile_id)

    def set_won_flag(self, profile_id):
        for participant in self.participants:
            if participant.profile_id == profile_id:
                self.won = participant.won

    def _add_participants(self, players):
        for player in players:
            participant = MatchParticipant(str(player['profile_id']), player['name'], player['country'],
                                           player['rating'],
                                           player['civ'], player['team'], player['won'])
            self.participants.append(participant)

    def player_won_the_match(self, profile_id):
        for participant in self.participants:
            if participant.profile_id == profile_id:
                return participant.won

    def __str__(self) -> str:
        return f'{self.map} {"Victory" if self.won else "Defeat"} ({self.finished.strftime("%d.%m.%Y %H:%M:%S")}) {self.leaderboard}'


class MatchParticipant:
    def __init__(self, profile_id: str, name: str, country: str, rating: int, civ: int, team: int, won: bool):
        self.profile_id = profile_id
        self.name = name
        self.country = country
        self.rating = rating
        self.civilization = GameInfo.civilizations[civ]
        self.team = team
        self.won = won

    def __str__(self):
        return f'{self.name}-{self.country} {self.civilization} {self.rating}'
