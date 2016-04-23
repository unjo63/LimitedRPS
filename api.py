"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

from datetime import datetime
import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import oauth
from google.appengine.ext import ndb

from models import User, Game
from models import StringMessage, StringMessages
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))

CREATE_GAME_REQUEST = endpoints.ResourceContainer(
    player_1_name=messages.StringField(1),
    player_2_name=messages.StringField(2))

GET_GAME_REQUEST = endpoints.ResourceContainer(
    game_key=messages.StringField(1))

PLAY_GAME_REQUEST = endpoints.ResourceContainer(
    game_key=messages.StringField(1),
    player_name=messages.StringField(2),
    move=messages.StringField(3))

GET_USER_GAME_REQUEST = endpoints.ResourceContainer(
    player_name=messages.StringField(1))

ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'

@endpoints.api(name='limitedRockPaperScissors', version='v1')
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
                    email=oauth_user.email(), win=0, lose=0, draw=0)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))


    @endpoints.method(request_message=CREATE_GAME_REQUEST,
                      response_message=StringMessage,
                      path='create_game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a Game between two Users)"""

        if request.player_1_name == request.player_2_name:
            raise endpoints.ConflictException(
                'Cannot create a game between a player and themselves!')
        for player_name in [request.player_1_name, request.player_2_name]:
            if not User.query(User.name == player_name).get():
                raise endpoints.ConflictException(
                    'No user named {} exists!'.format(player_name))

        game = Game(player_1_name = request.player_1_name,
                    player_2_name = request.player_2_name,
                    player_1_rock=3,
                    player_1_paper=3,
                    player_1_scissors=3,
                    player_2_rock=3,
                    player_2_paper=3,
                    player_2_scissors=3,
                    player_1_roundscore=0,
                    player_2_roundscore=0,
                    round=0,
                    start_time=datetime.now(),
                    is_active=True,
                    roundresult='Not all players have played yet.')

        game_key = game.put()
        return StringMessage(message='Game created!\n'
                                     '{}\'s cards remain (Rock{} : Paper{} : Scissors{}).\n'
                                     '{}\'s cards (Rock{} : Paper{} : Scissors{}).\n'
                                     '{} rounds have been finished.\n'
                                     '(key={})'.format(request.player_1_name, game.player_1_rock,
                                                       game.player_1_paper, game.player_1_scissors,
                                                       request.player_2_name, game.player_2_rock,
                                                       game.player_2_paper, game.player_2_scissors,
                                                       game.round,
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

        return StringMessage(message='Found game between {} and {}.\n'
                                     '(key={})\n'
                                     '{}\n'
                                     '{}\'s cards remain (Rock{} : Paper{} : Scissors{})\n'
                                     '{}\'s cards remain (Rock{} : Paper{} : Scissors{}).'
                                            .format(game.player_1_name,
                                                    game.player_2_name,
                                                    request.game_key,
                                                    game.roundresult,
                                                    game.player_1_name,
                                                    game.player_1_rock,
                                                    game.player_1_paper,
                                                    game.player_1_scissors,
                                                    game.player_2_name,
                                                    game.player_2_rock,
                                                    game.player_2_paper,
                                                    game.player_2_scissors))

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
        if game.player_1_name == request.player_name:
            if game.player_1_move == None:
                if request.move == ROCK:
                    if game.player_1_rock < 1:
                        raise endpoints.ConflictException(
                            '{}\'s rock card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_1_move = request.move
                        game.player_1_rock -= 1
                elif request.move == PAPER:
                    if game.player_1_paper < 1:
                        raise endpoints.ConflictException(
                            '{}\'s paper card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_1_move = request.move
                        game.player_1_paper -= 1
                elif request.move == SCISSORS:
                    if game.player_1_scissors < 1:
                        raise endpoints.ConflictException(
                            '{}\'s scissors card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_1_move = request.move
                        game.player_1_scissors -= 1
                else:
                    raise endpoints.ConflictException(
                        '{} chose a card we don\'t know about. You have to '
                        'choose rock, paper or scissors. Try to choose a '
                        'card again.'.format(request.player_name))
            else:
                raise endpoints.ConflictException(
                    '{} already used a {} card. Please wait to {}\'s move.'
                        .format(request.player_name, game.player_1_move, game.player_2_name))
        elif game.player_2_name == request.player_name:
            if game.player_2_move == None:
                if request.move == ROCK:
                    if game.player_2_rock < 1:
                        raise endpoints.ConflictException(
                            '{}\'s rock card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_2_move = request.move
                        game.player_2_rock -= 1
                elif request.move == PAPER:
                    if game.player_2_paper < 1:
                        raise endpoints.ConflictException(
                            '{}\'s paper card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_2_move = request.move
                        game.player_2_paper -= 1
                elif request.move == SCISSORS:
                    if game.player_2_scissors < 1:
                        raise endpoints.ConflictException(
                            '{}\'s scissors card does not remain. '
                            'Choose another type of card.'
                                .format(request.player_name))
                    else:
                        game.player_2_move = request.move
                        game.player_2_scissors -= 1
                else:
                    raise endpoints.ConflictException(
                        '{} chose a card we don\'t know about. You have to '
                        'choose rock, paper or scissors. Try to choose a '
                        'card again.'.format(request.player_name))
            else:
                raise endpoints.ConflictException(
                    '{} already used a {} card. Please wait to {}\'s move.'
                        .format(request.player_name, game.player_2_move, game.player_1_name))
        game.put()

        # Evaluate result and update Game and Match if game has finished
        if game.player_1_move is not None \
                and game.player_2_move is not None:
            if game.player_1_move == ROCK:
                if game.player_2_move == ROCK:
                    game_winner = 0                 #draw
                elif game.player_2_move == PAPER:
                    game_winner = 2                 #winner is player_2
                else:
                    game_winner = 1                 #winner is player_1
            elif game.player_1_move == PAPER:
                if game.player_2_move == ROCK:
                    game_winner = 1
                elif game.player_2_move == PAPER:
                    game_winner = 0
                else:
                    game_winner = 2
            else:
                if game.player_2_move == ROCK:
                    game_winner = 2
                elif game.player_2_move == PAPER:
                    game_winner = 1
                else:
                    game_winner = 0
            if game_winner == 1:
                game.roundresult = "Round result: Winer:{}, Loser:{}."\
                    .format(game.player_1_name, game.player_2_name)
                game.player_1_roundscore += 1
            elif game_winner == 2:
                game.roundresult = "Round result: Winer:{}, Loser:{}."\
                    .format(game.player_2_name, game.player_1_name)
                game.player_2_roundscore += 1
            else:
                game.roundresult = "Round result: Draw."

            game.player_1_move=None
            game.player_2_move=None
            game.round += 1
            game.put()

        # Update Game and Users if game has finished
        if (game.round > 8) or (game.player_1_roundscore > 4) \
                or (game.player_2_roundscore > 4):
            game.is_active = False
            game.put()
            if game.player_1_roundscore != game.player_2_roundscore:  # if not draw
                if game.player_1_roundscore < game.player_2_roundscore:
                    winner_name = game.player_1_name
                    loser_name = game.player_2_name
                else:
                    winner_name = game.player_2_name
                    loser_name = game.player_1_name
                winner = User.query(User.name == winner_name).get()
                loser = User.query(User.name == loser_name).get()
                winner.win += 1
                loser.lose += 1
                winner.put()
                loser.put()
                game_result = 'Game finished. Game result Winner:{}, Loser:{}.'\
                    .format(winner_name, loser_name)
            else:
                draw1 = User.query(User.name == game.player_1_name).get()
                draw2 = User.query(User.name == game.player_2_name).get()
                draw1.draw += 1
                draw2.draw += 1
                draw1.put()
                draw2.put()
                game_result = 'Game finished. Game result is Draw.'
        else:
            game_result = 'Game still in progress.'

        return StringMessage(message='{} played {}\'s card in this round.\n'
                                     '(key={})\n'
                                     '{}\n{}\n'
                                     '{}\'s cards remain (Rock{} : Paper{} : Scissors{}).\n'
                                     '{}\'s cards remain (Rock{} : Paper{} : Scissors{}).\n'
                                     '{} rounds have been finished.'
                             .format(request.player_name,
                                    request.move,
                                    request.game_key,
                                    game.roundresult,
                                    game_result,
                                    game.player_1_name,
                                    game.player_1_rock,
                                    game.player_1_paper,
                                    game.player_1_scissors,
                                    game.player_2_name,
                                    game.player_2_rock,
                                    game.player_2_paper,
                                    game.player_2_scissors,
                                    game.round))

    @endpoints.method(request_message=GET_USER_GAME_REQUEST,
                      response_message=StringMessages,
                      path='get_user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get all active Matches for a User"""

        games = Game.query(ndb.AND(Game.is_active == True,
                                      ndb.OR(
                                          Game.player_1_name ==
                                          request.player_name,
                                          Game.player_2_name ==
                                          request.player_name))).fetch()

        return StringMessages(message=[game.key.urlsafe()
                                       for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='cancel_game',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Cancel an active match"""

        game = get_by_urlsafe(request.game_key, Game)
        if not game:
            raise endpoints.ConflictException('Cannot find game with key {}'.
                                              format(request.game_key))
        if not game.is_active:
            raise endpoints.ConflictException('Game already inactive')

        game.round = 9
        game.is_active = False
        game.put()

        return StringMessage(message='Game {} cancelled'.
                             format(request.game_key))

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessages,
                      path='get_user_rankings',
                      name='get_user_rankings',
                      http_method='POST')
    def get_user_rankings(self, request):
        """Return list of Users in descending order of wins"""
        users = User.query().order(-User.win).fetch()

        return StringMessages(message=['{} (win:{}, lose:{}, draw:{})'.
                              format(user.name, user.win, user.lose,
                                     user.draw) for user in users])


    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessages,
                      path='get_active_users',
                      name='get_active_users',
                      http_method='GET')
    def get_active_users(self, request):
        """Return list of users with active games"""
        users = User.query().fetch()

        active_users = []
        for user in users:
            if self.get_user_games(
                    GET_USER_GAME_REQUEST.combined_message_class(
                        player_name=user.name)).message:
                active_users.append(user)

        return StringMessages(message=[user.name for user in active_users])

api = endpoints.api_server([LimitedRPSApi])

