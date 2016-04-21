#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with active Games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)

        for user in users:
            games = Game.query(ndb.AND(Game.is_active == True,
                                          ndb.OR(
                                              Game.player_1_name == user.name,
                                              Game.player_2_name == user.name)
                                          )).fetch()

            if games:
                subject = 'Unfinished game reminder!'
                body = 'Hello {}, \n\nThe following games are still in ' \
                       'progress:\n'.format(user.name)
                html = 'Hello {}, <br><br>The following games are still in ' \
                       'progress:<br>'.format(user.name)
                for game in games:
                    body += '{} vs {}\n'.format(game.player_1_name,
                                                game.player_2_name)
                    html += '{} vs {}<br>'.format(game.player_1_name,
                                                  game.player_2_name)
                body += 'https://{}.appspot.com">Continue playing'\
                    .format(app_id)
                html += '<a href="https://{}.appspot.com">Continue playing' \
                        '</a>'.format(app_id)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email, subject, body, html=html)

app = webapp2.WSGIApplication([('/crons/send_reminder', SendReminderEmail)],
                              debug=True)
