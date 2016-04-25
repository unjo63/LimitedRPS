"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    winning_rate = ndb.FloatProperty()
    # Rate of wining games per all finished games
    win = ndb.IntegerProperty()  # Number of win games
    lose = ndb.IntegerProperty()  # Number of lose games
    draw = ndb.IntegerProperty()  # Number of draw games


class Game(ndb.Model):
    """Game with players name and cards remain."""
    player_1_name = ndb.StringProperty(required=True)
    player_2_name = ndb.StringProperty(required=True)
    player_1_rock = ndb.IntegerProperty()  # Number of Player1's rock cards
    player_1_paper = ndb.IntegerProperty()  # Number of Player1's paper cards
    player_1_scissors = ndb.IntegerProperty()
    # Number of Player1's scissors cards
    player_2_rock = ndb.IntegerProperty()  # Number of Player2's rock cards
    player_2_paper = ndb.IntegerProperty()  # Number of Player2's paper cards
    player_2_scissors = ndb.IntegerProperty()
    # Number of Player2's scissors cards
    player_1_round_score = ndb.IntegerProperty()
    # Number of rounds Player1 wins in the game
    player_2_round_score = ndb.IntegerProperty()
    # Number of rounds Player2 wins in the game
    round = ndb.IntegerProperty()  # Number of played rounds in this game
    player_1_move = ndb.StringProperty()  # rock or paper or scissors
    player_2_move = ndb.StringProperty()  # rock or paper or scissors
    is_active = ndb.BooleanProperty()
    # True corresponds to this game is active.
    # False corresponds to this game was finished.
    round_result = ndb.StringProperty()  # Result of round


class UserScores(ndb.Model):
    """Record user scores with each games"""
    player = ndb.StringProperty()  # Player name
    score = ndb.IntegerProperty() # Number of winning round in game


class PlayerMoves(ndb.Model):
    """Record player's move play in round"""
    player_1_move = ndb.StringProperty()  # Player_1's move
    player_2_move = ndb.StringProperty()  # Player_2's move
    round = ndb.IntegerProperty()  # Number of rounds played in the game


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class StringMessages(messages.Message):
    """StringMessage-- outbound (repeated) string message"""
    message = messages.StringField(1, repeated=True)
