import requests

API_PATH = 'https://aoe2.net/api'


def get_strings():
    return requests.get(API_PATH + '/strings?game=aoe2de&language=en').json()


def get_player_matches(player_id, matches_to_analyze):
    return requests.get(API_PATH +
                        f'/player/matches?game=aoe2de&profile_id={player_id}&count={matches_to_analyze}').json()


def get_player_rating_history(profile_id, start=0, count=1000, leaderboard_id=0):
    return requests.get(API_PATH +
                        f'/player/ratinghistory?game=aoe2de'
                        f'&leaderboard_id={leaderboard_id}&profile_id={profile_id}&count={count}'
                        f'&start={start}').json()


def get_profile_id_by_username(username):
    user_info = requests.get(API_PATH + f'/leaderboard?game=aoe2de&search={username}').json()
    return user_info['leaderboard'][0]['profile_id']
