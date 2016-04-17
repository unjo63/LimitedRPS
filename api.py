"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

from datetime import datetime
import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import oauth
from google.appengine.ext import ndb

from models import User, Game, Match
from models import StringMessage, StringMessages
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))

CREATE_MATCH_REQUEST = endpoints.ResourceContainer(
    player_1_name=messages.StringField(1),
    player_2_name=messages.StringField(2))

GET_MATCH_REQUEST = endpoints.ResourceContainer(
    match_key=messages.StringField(1))

CREATE_GAME_REQUEST = endpoints.ResourceContainer(
    match_key=messages.StringField(1))

GET_GAME_REQUEST = endpoints.ResourceContainer(
    game_key=messages.StringField(1))

PLAY_GAME_REQUEST = endpoints.ResourceContainer(
    game_key=messages.StringField(1),
    player_name=messages.StringField(2),
    move=messages.StringField(3))

GET_USER_MATCH_REQUEST = endpoints.ResourceContainer(
    player_name=messages.StringField(1))

ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
DRAW = 'draw'

@endpoints.api(name='LimitedRockPaperScissors', version='v1')
class LimitedRPSApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='create_user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username.
        Gets email from oauth account"""
        scope = 'https://www.googleapis.com/auth/userinfo.email'
        oauth_user = oauth.get_current_user(scope)

        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')

        user = User(name=request.user_name,
                    email=oauth_user.email(), score=0)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=CREATE_MATCH_REQUEST,
                      response_message=StringMessage,
                      path='create_match',
                      name='create_match',
                      http_method='POST')
    def create_match(self, request):
        """Create a Match between two Users"""

        if request.player_1_name == request.player_2_name:
            raise endpoints.ConflictException(
                'Cannot create a match between a player and themselves!')
        for player_name in [request.player_1_name, request.player_2_name]:
            if not User.query(User.name == player_name).get():
                raise endpoints.ConflictException(
                    'No user named {} exists!'.format(player_name))

        match = Match(player_1_name=request.player_1_name,
                      player_2_name=request.player_2_name,
                      player_1_score=0,
                      player_1_rock=3,
                      player_1_paper=3,
                      player_1_scissors=3,
                      player_2_score=0,
                      player_2_rock=3,
                      player_2_paper=3,
                      player_2_scissors=3,
                      games_remaining=9,
                      is_active=True)

        match_key = match.put()
        return StringMessage(message='Match created between {} and {}! '
                                     '(key={})'.format(request.player_1_name,
                                                       request.player_2_name,
                                                       match_key.urlsafe()))

    @endpoints.method(request_message=CREATE_GAME_REQUEST,
                      response_message=StringMessage,
                      path='create_game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a Game in a Match (between participating Users)"""

        match = get_by_urlsafe(request.match_key, Match)
        if not match:
            raise endpoints.ConflictException('Cannot find match with key {}'.
                                              format(request.match_key))
        if not match.is_active:
            raise endpoints.ConflictException('Cannot create new Game in the '
                                              'following Match; it has already'
                                              ' finished: {}'.
                                              format(request.match_key))

        game = Game(parent=match.key,
                    start_time=datetime.now(),
                    is_active=True,
                    result='Not all players have played yet.')

        game_key = game.put()
        return StringMessage(message='Game created between {} and {}! '
                                     '(key={})'.format(match.player_1_name,
                                                       match.player_2_name,
                                                       game_key.urlsafe()))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='get_game',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Get a Game from its websafe key"""

        game = get_by_urlsafe(request.game_key, Game)
        if not game:
            raise endpoints.ConflictException('Cannot find game with key {}'.
                                              format(request.game_key))
        match = game.key.parent().get()

        return StringMessage(message='Found game between {} and {} with key {}'
                                     '. {} '
                                     # '{}\'s cards remain Rock {} : Paper {} : '
                                     # 'Scissors {}. '
                                     # '{}\'s cards remain Rock {} : Paper {} : '
                                     # 'Scissors {}.'
                                                    .format(match.player_1_name,
                                                           match.player_2_name,
                                                           request.game_key,
                                                           game.result,
                                                           # match.player_1_name,
                                                           # match.player_1_rock,
                                                           # match.player_1_paper,
                                                           # match.player_1_scissors,
                                                           # match.player_2_name,
                                                           # match.player_2_rock,
                                                           # match.player_2_paper,
                                                           # match.player_2_scissors
                                                            ))

    @endpoints.method(request_message=PLAY_GAME_REQUEST,
                      response_message=StringMessage,
                      path='play_game',
                      name='play_game',
                      http_method='POST')
    def play_game(self, request):
        """Play move in a Game."""
        scope = 'https://www.googleapis.com/auth/userinfo.email'
        oauth_user = oauth.get_current_user(scope)

        # Verify inputs and game state
        game = get_by_urlsafe(request.game_key, Game)
        if not game:
            raise endpoints.ConflictException('Cannot find game with key {}'.
                                              format(request.game_key))
        if not game.is_active:
            raise endpoints.ConflictException('Game has already finished')

        player = User.query(User.name == request.player_name).get()
        if not player:
            raise endpoints.ConflictException(
                'No user named {} exists!'.format(request.player_name))

        if not player.email == oauth_user.email():
            raise endpoints.ConflictException(
                'You are not authorized to play for {}!'.format(
                    request.player_name))

        # Save single player's move. Players can choose
        # rock, paper or scissors from the cards remaining.
        match = game.key.parent().get()
        if match.player_1_name == request.player_name:
            if request.move == ROCK and match.player1_rock < 1:
                raise endpoints.ConflictException(
                    'Your Rock card does not remain. Choose another '
                    'type of card.')
            elif request.move == PAPER and match.player_1_paper < 1:
                raise endpoints.ConflictException(
                    'Your Paper card does not remain. Choose another '
                    'type of card.')
            elif request.move == SCISSORS and match.player_1_scissors < 1:
                raise endpoints.ConflictException(
                    'Your Scissors card does not remain. Choose another '
                    'type of card.')
            elif not (request.move is ROCK or PAPER or SCISSORS):
                raise endpoints.ConflictException(
                    'You chose a card we don\'t know about. You have to '
                    'choose rock or paper or scissors. Try to choose a '
                    'card again.')
            else:
                game.player_1_move = request.move
        elif match.player_2_name == request.player_name:
            if request.move == ROCK and match.player1_rock < 1:
                raise endpoints.ConflictException(
                    'Your Rock card does not remain. Choose another '
                    'type of card.')
            elif request.move == PAPER and match.player_1_paper < 1:
                raise endpoints.ConflictException(
                    'Your Paper card does not remain. Choose another '
                    'type of card.')
            elif request.move == SCISSORS and match.player_1_scissors < 1:
                raise endpoints.ConflictException(
                    'Your Scissors card does not remain. Choose another '
                    'type of card.')
            elif not (request.move is ROCK or PAPER or SCISSORS):
                raise endpoints.ConflictException(
                    'You chose a card we don\'t know about. You have to '
                    'choose rock or paper or scissors. Try to choose a '
                    'card again.')
            else:
                game.player_2_move = request.move
        else:
            raise endpoints.ConflictException('Player {} is not playing in '
                                              'game {}'.
                                              format(request.player_name,
                                                     request.game_key))
        game.put()

        # Evaluate result and update Game and Match if game has finished
        if game.player_1_move is not None \
                and game.player_2_move is not None:
            if game.player_1_move == ROCK:
                match.player_1_rock -= 1
                if game.player_2_move == ROCK:
                    match.player_2_rock -= 1
                    game_winner = 0                 #draw
                elif game.player_2_move == PAPER:
                    match.player_2_paper -= 1
                    game_winner = 2                 #winner is player_2
                else:
                    match.player_2_scissors -= 1
                    game_winner = 1                 #winner is player_1
            elif game.player_1_move == PAPER:
                match.player_1_paper -= 1
                if game.player_2_move == ROCK:
                    match.player_2_rock -= 1
                    game_winner = 1
                elif game.player_2_move == PAPER:
                    match.player_2_paper -= 1
                    game_winner = 0
                else:
                    match.player_2_scissors -= 1
                    game_winner = 2
            else:
                match.player_1_scissors -= 1
                if game.player_2_move == ROCK:
                    match.player_2_rock -= 1
                    game_winner = 2
                elif game.player_2_move == PAPER:
                    match.player_2_paper -= 1
                    game_winner = 1
                else:
                    match.player_2_scissors -= 1
                    game_winner = 0
            if game_winner == 1:
                game.result = "Game result: Winer:{}, Loser:{}.".format(
                match.player_1_name, match.player_2_name)
                match.player_1_score += 1
            elif game_winner == 2:
                game.result = "Game result: Winer:{}, Loser:{}.".format(
                match.player_2_name, match.player_1_name)
                match.player_2_score += 1
            else:
                game.result = "Game result: Draw."
            game.is_active = False
            game.put()

            match.games_remaining -= 1
            match.put()

        # Update Match and Users if match has finished
        if (match.games_remaining < 1) or (match.player_1_score > 4) \
                or (match.player_2_score > 4):
            match.is_active = False
            match.put()
            if match.player_1_score != match.player_2_score:  # if not draw
                if match.player_1_score < match.player_2_score:
                    winner_name = match.player_1_name
                    loser_name = match.player_2_name
                else:
                    winner_name = match.player_2_name
                    loser_name = match.player_1_name
                winner = User.query(User.name == winner_name).get()
                loser = User.query(User.name == loser_name).get()
                winner.score += 1
                loser.score -= 1
                winner.put()
                loser.put()
                match_result = 'Match finished. Winner:{}, Loser:{}.'.format(
                    winner_name, loser_name)
            else:
                match_result = 'Match finished. Result is Draw.'
        else:
            match_result = 'Match still in progress.'

        return StringMessage(message='Registered player {}\'s play of {} in '
                                     'game {}. {} {} '
                                     '{}\'s cards remain Rock {} : Paper {} : '
                                     'Scissors {}. '
                                     '{}\'s cards remain Rock {} : Paper {} : '
                                     'Scissors {}.'.
                             format(request.player_name,
                                    request.move,
                                    request.game_key,
                                    game.result,
                                    match_result,
                                    match.player_1_name,
                                    match.player_1_rock,
                                    match.player_1_paper,
                                    match.player_1_scissors,
                                    match.player_2_name,
                                    match.player_2_rock,
                                    match.player_2_paper,
                                    match.player_2_scissors))

    @endpoints.method(request_message=GET_USER_MATCH_REQUEST,
                      response_message=StringMessages,
                      path='get_user_matches',
                      name='get_user_matches',
                      http_method='GET')
    def get_user_matches(self, request):
        """Get all active Matches for a User"""

        matches = Match.query(ndb.AND(Match.is_active == True,
                                      ndb.OR(
                                          Match.player_1_name ==
                                          request.player_name,
                                          Match.player_2_name ==
                                          request.player_name))).fetch()

        return StringMessages(message=[match.key.urlsafe()
                                       for match in matches])

    @endpoints.method(request_message=GET_MATCH_REQUEST,
                      response_message=StringMessage,
                      path='cancel_match',
                      name='cancel_match',
                      http_method='POST')
    def cancel_match(self, request):
        """Cancel an active match"""

        match = get_by_urlsafe(request.match_key, Match)
        if not match:
            raise endpoints.ConflictException('Cannot find match with key {}'.
                                              format(request.match_key))
        if not match.is_active:
            raise endpoints.ConflictException('Match already inactive')

        match.games_remaining = 0
        match.is_active = False
        match.put()

        return StringMessage(message='Match {} cancelled'.
                             format(request.match_key))

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessages,
                      path='get_user_rankings',
                      name='get_user_rankings',
                      http_method='POST')
    def get_user_rankings(self, request):
        """Return list of Users in descending order of score"""
        users = User.query().order(-User.score).fetch()

        return StringMessages(message=['{} (score:{})'.
                              format(user.name, user.score) for user in users])

    @endpoints.method(request_message=GET_MATCH_REQUEST,
                      response_message=StringMessages,
                      path='get_match_history',
                      name='get_match_history',
                      http_method='GET')
    def get_match_history(self, request):
        """Return list of Game plays in Match"""

        match = get_by_urlsafe(request.match_key, Match)
        if not match:
            raise endpoints.ConflictException('Cannot find match with key {}'.
                                              format(request.match_key))

        games = Game.query(ancestor=match.key).order(Game.start_time)

        return StringMessages(message=[
            '{}:{}, {}:{}. {}'.format(match.player_1_name, game.player_1_move,
                                      match.player_2_name, game.player_2_move,
                                      game.result) for game in games])

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessages,
                      path='get_active_users',
                      name='get_active_users',
                      http_method='GET')
    def get_active_users(self, request):
        """Return list of users with active matches"""
        users = User.query().fetch()

        active_users = []
        for user in users:
            if self.get_user_matches(
                    GET_USER_MATCH_REQUEST.combined_message_class(
                        player_name=user.name)).message:
                active_users.append(user)

        return StringMessages(message=[user.name for user in active_users])

api = endpoints.api_server([LimitedRPSApi])
