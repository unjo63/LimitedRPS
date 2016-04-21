"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    win = ndb.IntegerProperty(required=True)  # Number of wins
    lose = ndb.IntegerProperty(required=True)  # Number of losses
    draw = ndb.IntegerProperty(required=True)  # Number of draws



class Game(ndb.Model):
    """Game (in Match)"""
    player_1_name = ndb.StringProperty(),
    player_2_name = ndb.StringProperty(),
    player_1_rock=ndb.IntegerProperty(),
    player_1_paper=ndb.IntegerProperty(),
    player_1_scissors=ndb.IntegerProperty(),
    player_2_rock=ndb.IntegerProperty(),
    player_2_paper=ndb.IntegerProperty(),
    player_2_scissors=ndb.IntegerProperty(),
    player_1_roundscore=ndb.IntegerProperty(),
    player_2_roundscore=ndb.IntegerProperty(),
    games_remain=ndb.IntegerProperty(),
    player_1_move = ndb.StringProperty()  # rock or paper or scissors
    player_2_move = ndb.StringProperty()  # rock or paper or scissors
    is_active = ndb.BooleanProperty()
    start_time = ndb.DateTimeProperty()
    roundresult = ndb.StringProperty()  # Result of game round


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class StringMessages(messages.Message):
    """StringMessage-- outbound (repeated) string message"""
    message = messages.StringField(1, repeated=True)
