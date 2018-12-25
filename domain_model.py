import random
import names

from active_record import Player, Team, Match


class PlayerDomainModel:

    def __init__(self, player_data=None):
        self.player_data = player_data

    @staticmethod
    def generate_player(team: int) -> 'PlayerDomainModel':
        name, surname = names.get_full_name(gender='male').split(' ')
        year = random.randint(1970, 2000)
        month = random.randint(1, 12)
        if month < 10:
            month = f'0{month}'
        day = random.randint(1, 29)
        if day < 10:
            day = f'0{day}'
        birthday = f'{year}.{month}.{day}'
        number_in_team = random.randint(1, 99)
        role = random.choice(['вратарь',
                              'центральный защитник',
                              'правый защитник',
                              'левый защитник',
                              'опорный полузащитник',
                              'правый выдвинутый защитник',
                              'левый выдвинутый защитник'])

        player = Player(name=name, surname=surname, birthday=birthday,
                        number_in_team=number_in_team, role=role, team=team)
        player.create()
        return PlayerDomainModel(player_data=player)

    def get_club_name(self):
        return self.player_data.get_club().name

    @staticmethod
    def get_all_players() -> list('PlayerDomainModel'):
        return list(map(lambda p: PlayerDomainModel(player_data=p), Player.read_all()))

    @staticmethod
    def get_players_of_team(team_id) -> list('PlayerDomainModel'):
        return list(map(lambda p: PlayerDomainModel(player_data=p), Player.players_of_team(team_id)))

    def add_goal(self, goal_count=1):
        self.player_data.add_goal(goal_count)


class TeamDomainModel:

    def __init__(self, team_data=None, players=None):
        self.players: list(PlayerDomainModel) = players or list()
        self.team_data: Team = team_data

    @staticmethod
    def get_all_teams() -> list('TeamDomainModel'):
        return list(map(lambda t: TeamDomainModel(team_data=t), Team.read_all()))

    @staticmethod
    def get_team(_id: int):
        return TeamDomainModel(team_data=Team.read(_id),
                               players=PlayerDomainModel.get_players_of_team(_id))

    @staticmethod
    def create_team(name: str = '', city: str = ''):
        """Созадние команды + генерация 5ти игроков."""
        team = Team(name=name, city=city)
        team.create()
        players = list()
        for i in range(5):
            players.append(PlayerDomainModel.generate_player(team._id))
        return TeamDomainModel(players=players, team_data=team)

    def win_match(self):
        self.team_data.win_match()

    def loose_match(self):
        self.team_data.loose_match()

    def get_match(self):
        self.team_data.get_match()

    def update_team(self, name='', city=''):
        self.team_data.name = name
        self.team_data.city = city
        self.team_data.update()


class MatchDomainModel:

    def __init__(self, match_data=None, team=None, opponent=None):
        self.match_data = match_data
        self.team = team
        self.opponent = opponent

    @staticmethod
    def get_all_matches() -> list('MatchDomainModel'):
        matches = list(map(lambda m: MatchDomainModel(match_data=m), Match.read_all()))
        for match in matches:
            match.team = TeamDomainModel.get_team(match.match_data.team)
            match.opponent = TeamDomainModel.get_team(match.match_data.opponent)
        return matches

    @staticmethod
    def generate_match(team_id: int, opponent_id: int) -> 'MatchDomainModel':
        team = TeamDomainModel.get_team(team_id)
        opponent = TeamDomainModel.get_team(opponent_id)
        team_goals = random.randint(0, 10)
        opponent_goals = random.randint(0, 10)
        match = Match(team=team.team_data._id,
                      opponent=opponent.team_data._id,
                      team_goals=team_goals,
                      opponent_goals=opponent_goals)
        match.create()
        if match.team_goals > match.opponent_goals:
            team.win_match()
            opponent.loose_match()
        elif match.team_goals < match.opponent_goals:
            opponent.win_match()
            team.loose_match()
        else:
            opponent.get_match()
            team.get_match()
        team_players = PlayerDomainModel.get_players_of_team(team_id)
        if team_players:
            for _ in range(team_goals):
                player = random.choice(team_players)
                player.add_goal()

        opponent_players = PlayerDomainModel.get_players_of_team(opponent_id)
        if opponent_players:
            for _ in range(opponent_goals):
                player = random.choice(opponent_players)
                player.add_goal()

        return MatchDomainModel(match_data=match, team=team, opponent=opponent)
