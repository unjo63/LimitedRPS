# Udacity Full Stack Nanodegree Project 4: "Design a Game" 
*"The backend for a platform-agnostic app using Google App Engine backed by Google Datastore."*  
This application is the backend for an implementation of the *Limited Rock Paper Scissors* game.


## About the Limited Rock Paper Scissors
- Rock-Paper-Scissors in general:  
Rock-paper-scissors is a zero-sum hand game usually played between two people,
in which each player simultaneously forms one of three shapes with an outstretched hand.
These shapes are "rock" (a simple fist), "paper" (a flat hand), and "scissors"
(a fist with the index and middle fingers together forming a V). The game has only
three possible outcomes other than a tie: a player who decides to play rock will beat
another player who has chosen scissors ("rock crushes scissors") but will lose to one
who has played paper ("paper covers rock"); a play of paper will lose to a play of scissors
("scissors cut paper"). If both players throw the same shape, the game is considered a draw.  
(From [wikipedia](https://en.wikipedia.org/wiki/Rock-paper-scissors))


- Limited Rock Paper Scissors:  
Limited Rock Paper Scissors(LimitedRPS) is the rule customized Rock Paper Scissors.  
LimitedRPS is played between two players.
Two players play Rock Paper Scissors each other 5~9 rounds by one game. 
Each players have 3 rock cards, 3 paper cards and 3 scissors cards at the start of the game.
If a player plays rock, the player lost his/har one rock card.
If a player has no rock cards, he/she can't play rock until the game is over,
that is, a player can play each cards only 3 times by one game.
The player who wins 5 rounds, or if 9 rounds over, the player 
who wins more rounds than the opponent is the winner of the game.
If two players wins same times, game result is draw.

## Features  

This backend for an online two player Limited Rock Paper Scissors game has the following functionality.

- Create Users (players).  Users' email addresses are sourced from their google login and are used for game notifications.
- Create Games with multiple rounds between Users.
- Play Games with scores saved to User profiles
- Get result of current round in a Game.
- Get User rankings order by the number of wins.
- Notify Users of unfinished Games by email (automatically every hour).

## Files Included
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Requirements
- *[Python 2.7](https://www.python.org/downloads/)* (tested with version 2.7.6)  
- *[Google App Engine SDK](https://cloud.google.com/appengine/downloads)* (tested with version 1.9.28)  

## Setup
0. Clone this repository.
1. Create a new project in your *[Google Cloud Platform Console](https://console.cloud.google.com/)* and copy your application ID to *app.yaml* in place of `limitedrps`.
2. Deploy your project. (See the [docs](https://cloud.google.com/appengine/docs/python/) for details).
3. While launching chrome to test API, you will have to launch it using the console as follows: [path-to-Chrome] --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost: `port`

## Endpoints
 - **create_user**
    - Path: 'create_user'
    - Method: POST
    - Parameters: user_name
    - Returns: StringMessage confirming creation of the User.
    - Description: *Create a User. Requires a unique username. Gets email from oauth account*

 - **create_game**
    - Path: 'create_game'
    - Method: POST
    - Parameters: player_1_name, player_2_name
    - Returns: StringMessage confirming creation of the Game.
    - Description: *Create a Game between two Users specified by their names*

 - **get_game**
    - Path: 'get_game'
    - Method: GET
    - Parameters: game_key
    - Returns: StringMessage listing players and game status/result if Game is found.
    - Description: *Get a description of a Game from its websafe key*
    
 - **play_game**
    - Path: 'play_game'
    - Method: POST
    - Parameters: game_key, player_name, move
    - Returns: StringMessage listing move and result.
    - Description: *Play a single player's move in a Game.* You can choose a move from rock,paper or scissors.
    If both player's have played, it scores the round and returns the result.  It also automatically updates the Game and player User objects.
    
 - **get_user_games**
    - Path: 'get_user_games'
    - Method: GET
    - Parameters: player_name
    - Returns: StringMessage containing list of active games for the user specified by name
    - Description: *Play move in a Game.*

 - **cancel_game**
    - Path: 'cancel_game'
    - Method: POST
    - Parameters: game_key
    - Returns: StringMessage containing confirmation message
    - Description: *Cancel an active game*
 
 - **get_user_rankings**
    - Path: 'get_user_rankings'
    - Method: GET
    - Parameters:
    - Returns: StringMessage containing list of Users in descending order of score
    - Description: *Return list of Users in descending order of score*
    
 - **get_active_users**
    - Path: 'get_active_users'
    - Method: GET
    - Parameters: 
    - Returns: StringMessage containing list of users with active games
    - Description: *Return list of users with active games*