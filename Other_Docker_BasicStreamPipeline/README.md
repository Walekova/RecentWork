# Docker - Basic Pipeline

### Team Members

Andy Cui 
Ivan Fan
Miroslava Walekova

### Project Description

Understanding revenue streams and game retention for a game. 

There are two major actions that players can use to interact with our game financially they can: 

(1) add money to their accounts\
(2) purchase in game items

There are also two major events that users can take on the social site:

(1) join a guild to network with other players\
(2) cancel or leave the guild if they are unhappy. 

We've set up our pipeline to stream in data from the game api into our data pipeline, and are able to issue queries on these pieces of data to better understand our users and drive business decisions.

### Content of repository:

	  *`docker-compose.yml` - definition of the stack used\
	  * Project Report - Jupyter Notebook\
	  * Project - game_api.py - Python file with available game actions\
	  * Project - write_stream.py - Python file - stream definition