import datetime

import aoe_api
from info import Match, GameInfo
from aoe_api import get_player_matches


START_OF_PERIOD = datetime.datetime.today() - datetime.timedelta(days=14)


class Player:
    MATCHES_TO_ANALYZE = 1000

    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.matches = []
        self.rating_history = {}
        self.add_matches()
        self.add_rating_history()
        try:
            first_match = self.matches[0]
            for participant in first_match.participants:
                if participant.profile_id == self.profile_id:
                    self.name = participant.name
                    self.country = participant.country
        except IndexError:
            pass

    def add_matches(self):
        matches = get_player_matches(self.profile_id, Player.MATCHES_TO_ANALYZE)
        for match in matches:
            match_info = Match(self.profile_id, match['match_id'], match['ranked'],
                               match['leaderboard_id'], match['rating_type'], match['server'],
                               match['started'], match['finished'], match['players'], match['map_type'])
            self.matches.append(match_info)

    def add_rating_history(self):
        for leaderboard_id, name in GameInfo.leaderboards.items():
            self.rating_history[name] = []
            rating_history = aoe_api.get_player_rating_history(self.profile_id, 0, Player.MATCHES_TO_ANALYZE,
                                                               leaderboard_id)

            for element in rating_history:
                rating_point = self.get_rating_point_from_rating_history(element)
                self.rating_history[name].append(rating_point)

    @staticmethod
    def get_rating_point_from_rating_history(element):
        win_percentage = round(100 * element['num_wins'] / (element['num_wins'] + element['num_losses']), 2)
        rating_point = {
            'rating': element['rating'],
            'wins': element['num_wins'],
            'defeats': element['num_losses'],
            'win_percentage': win_percentage,
            'date': datetime.datetime.fromtimestamp(element['timestamp'])
        }
        return rating_point

    @property
    def current_stats(self):
        current_stats = {}
        for name, history in self.rating_history.items():
            if len(history) > 0:
                current_stats[name] = history[0]

        return current_stats

    @property
    def get_civ_stats(self):
        civ_stats = self._create_stats_dict(GameInfo.civilizations.values())
        for match in self.matches:
            for participant in match.participants:
                if participant.profile_id == self.profile_id:
                    if participant.won:
                        civ_stats[participant.civilization]['wins'] += 1
                        if START_OF_PERIOD < match.finished:
                            civ_stats[participant.civilization]['last_month_wins'] += 1
                    else:
                        civ_stats[participant.civilization]['defeats'] += 1
                        if START_OF_PERIOD < match.finished:
                            civ_stats[participant.civilization]['last_month_defeats'] += 1
        self._delete_empty_stats(civ_stats)
        self._calculate_total_and_percentage(civ_stats)

        return self._sort_by_total_matches(civ_stats)

    @property
    def get_map_stats(self):
        map_stats = self._create_stats_dict(GameInfo.map_types.values())
        for match in self.matches:
            if match.player_won_the_match(self.profile_id):
                map_stats[match.map]['wins'] += 1
                if START_OF_PERIOD < match.finished:
                    map_stats[match.map]['last_month_wins'] += 1
            else:
                map_stats[match.map]['defeats'] += 1
                if START_OF_PERIOD < match.finished:
                    map_stats[match.map]['last_month_defeats'] += 1
        self._delete_empty_stats(map_stats)
        self._calculate_total_and_percentage(map_stats)
        return self._sort_by_total_matches(map_stats)

    @staticmethod
    def _create_stats_dict(collection):
        stats = {element: {'wins': 0, 'defeats': 0, 'win_percentage': 0,
                           'last_month_wins': 0, 'last_month_defeats': 0, 'last_month_win_percentage': 0}
                 for element in collection}
        return stats

    @staticmethod
    def _delete_empty_stats(stats):
        keys_for_deletion = [key for key in stats.keys() if stats[key]['wins'] + stats[key]['defeats'] == 0]
        for key in keys_for_deletion:
            del stats[key]

    @staticmethod
    def _calculate_total_and_percentage(stats):
        for stats in stats.values():
            stats['win_percentage'] = round(100 * stats['wins'] / (stats['wins'] + stats['defeats']), 2)
            if stats['last_month_wins'] + stats['last_month_defeats'] == 0:
                stats['last_month_win_percentage'] = 0
            else:
                stats['last_month_win_percentage'] = round(100 * stats['last_month_wins'] /
                                                           (stats['last_month_wins'] + stats['last_month_defeats']), 2)
            stats['total_matches'] = stats['wins'] + stats['defeats']

    @staticmethod
    def _sort_by_total_matches(stats):
        return {k: v for k, v in sorted(stats.items(), key=lambda item: item[1]['total_matches'], reverse=True)}
