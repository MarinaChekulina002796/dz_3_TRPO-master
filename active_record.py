import MySQLdb

conn = MySQLdb.connect(host="localhost",user="root",
                       passwd="1234",db="football", charset='utf8')


def curs_decorator(commit=False):
    def decorator(function):
        def wrapper(*args, **kwargs):
            curs = conn.cursor()
            result = function(*args, **kwargs, conn=conn)
            if commit:
                conn.commit()
            curs.close()
            return result
        return wrapper
    return decorator


class CRUD_operations:
    """Класс круд-операций."""

    def create(self):
        raise NotImplementedError

    @staticmethod
    def read(id: int):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class Interprety_Query:

    @staticmethod
    def get_result(cursor):
        result = []
        columns = tuple([d[0] for d in cursor.description])
        for row in cursor:
            result.append(dict(zip(columns, row)))
        return result


class Player(CRUD_operations, Interprety_Query):
    """Класс игрока."""

    # TODO read query
    read_all_query = """SELECT * from Player"""
    update_query = """
    UPDATE  Player SET 
    name="{name}", 
    surname="{surname}",
    birthday="{birthday}",
    number_in_team={number_in_team},
    role="{role}",
    goal_count={goal_count}
    WHERE id={id};
    """
    create_query="""
    INSERT INTO Player
    (name, surname, birthday,
    number_in_team, role, goal_count, team)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s)
    """
    my_club_query="""
    SELECT * from Team where id = %s;
    """
    players_of_team_query="""
    SELECT * from Player where team = %s;
    """

    def __init__(self, id=0, name: str='', surname: str = '',
                 birthday: str = '', number_in_team: int = 0, role: str = '',
                 goal_count: int = 0, team: int = None):
        self._id = id
        self.name = name
        self.surname = surname
        self.birthday = birthday
        self.number_in_team = number_in_team
        self.role = role
        self.goal_count = goal_count
        self.team=team

    @staticmethod
    def read(id: int) -> 'Player':
        c = conn.cursor()
        c.execute("""select * from Player where id = 1;""")
        result = []
        columns = tuple([d[0] for d in c.description])
        for row in c:
            result.append(dict(zip(columns, row)))
        p = Player(**result[0])
        c.close()
        return p

    @staticmethod
    def read_all()-> list('Player'):
        curs = conn.cursor()
        curs.execute(Player.read_all_query)
        result = Player.get_result(curs)
        curs.close()
        return list(map(lambda r: Player(**r), result))

    def update(self):
        c = conn.cursor()
        c.execute(self.update_query.format(
            name=self.name,
            surname=self.surname,
            birthday=self.birthday,
            number_in_team=self.number_in_team,
            role=self.role,
            goal_count=self.goal_count,
            id=self._id,
        ))

    def create(self):
        curs = conn.cursor()
        curs.execute(self.create_query,
                     (self.name, self.surname, self.birthday, self.number_in_team,
                      self.role, self.goal_count, self.team))
        conn.commit()
        self._id = curs.lastrowid
        curs.close()

    def get_club(self) -> 'Team':
        curs = conn.cursor()
        curs.execute(Player.my_club_query, (self.team,))
        result = Player.get_result(curs)
        curs.close()
        return Team(**result[0])

    def add_goal(self, goal_count: int = 1):
        """Добавить забитый гол."""
        self.goal_count += goal_count
        self.update()

    @staticmethod
    def players_of_team(team_id: int):
        curs = conn.cursor()
        curs.execute(Player.players_of_team_query, (team_id,))
        result = Player.get_result(curs)
        curs.close()
        return list(map(lambda r: Player(**r), result))



class Team(CRUD_operations, Interprety_Query):
    """Класс футбольной команды."""

    read_query = """
    SELECT id, name, city, games_count, win_games_count from Team
    WHERE id={id};
    """
    read_all_query = """
    SELECT id, name, city, games_count, win_games_count from Team;
    """
    update_query = """
    UPDATE Team SET 
    name="{name}", 
    city="{city}",
    games_count={games_count},
    win_games_count={win_games_count}
    WHERE id={id};
    """
    create_query="""
    INSERT INTO Team
    (name, city, games_count, win_games_count)
    VALUES
    (%s, %s, %s, %s)
    """

    def __init__(self, id: int = 0, name: str ='', city: str ='',
                 games_count: int = 0, win_games_count: int = 0):
        if id:
            self._id = id
        self.name = name
        self.city = city
        self.games_count = games_count
        self.win_games_count = win_games_count

    @staticmethod
    def read(_id: int) -> 'Team':
        curs = conn.cursor()
        curs.execute(Team.read_query.format(id=_id))
        result = Team.get_result(curs)
        curs.close()
        return Team(**result[0])

    def update(self):
        curs = conn.cursor()
        curs.execute(self.update_query.format(
            name=self.name,
            city=self.city,
            games_count=self.games_count,
            win_games_count=self.win_games_count,
            id=self._id,
        ))
        conn.commit()
        curs.close()

    def create(self):
        curs = conn.cursor()
        curs.execute(self.create_query,
                     (self.name, self.city, self.games_count, self.win_games_count))
        conn.commit()
        self._id = curs.lastrowid
        curs.close()

    @staticmethod
    def read_all()-> list('Team'):
        curs = conn.cursor()
        curs.execute(Team.read_all_query)
        result = Team.get_result(curs)
        curs.close()
        return list(map(lambda r: Team(**r), result))

    def get_match(self):
        self.games_count += 1
        self.update()

    def win_match(self):
        self.get_match()
        self.win_games_count +=1
        self.update()

    def loose_match(self):
        self.get_match()


class Match(CRUD_operations, Interprety_Query):
    """Класс футбольного матча."""

    create_query="""
    INSERT INTO FootballMatch
    (team, opponent, team_goals, opponent_goals)
    VALUES
    (%s, %s, %s, %s)
    """
    read_all_query = """
    SELECT id, team, opponent, team_goals, opponent_goals from FootballMatch;
    """


    def __init__(self, id: int = 0, team: int = 0, opponent: int = 0,
                 team_goals: int = 0, opponent_goals: int = 0):
        self._id = id
        self.team = team
        self.opponent = opponent
        self.team_goals = team_goals
        self.opponent_goals = opponent_goals

    def create(self):
        curs = conn.cursor()
        curs.execute(self.create_query,
                     (self.team, self.opponent, self.team_goals, self.opponent_goals))
        conn.commit()
        self._id = curs.lastrowid
        curs.close()

    @staticmethod
    def read_all()-> list('Match'):
        curs = conn.cursor()
        curs.execute(Match.read_all_query)
        result = Match.get_result(curs)
        curs.close()
        return list(map(lambda r: Match(**r), result))


