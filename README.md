# Bot WhyNot 

____

## What can this bot do for a user? 

* Give information about the weather in Moscow, Nizhny Novgorod and Saint Petersburg. It includes pressure, max., min., cf. temperature, humidity, wind speed, sunset and dawn time. Everything is implemented with the help of buttons under the bot's messages for more comfort. Moreover the bot can advise users how to dress for the current day.
* Give a huge amount of information about the state of coronovirus. User can ask WhyNot about the quantity of dead, infected, recoveries, ill right now and new infected by comparing the state yesterday and today by choosing Provinces/States, Countries/Districts to see the required statistics about the top 5 'biggest' countries. Users can also enter the name of the country to get information exactly about it. 
* Give information about the dollar or euro rate for the current date. This function is implemented by buttons as others. 
* Get user's favorite post on cat-fact.herokuapp.com.

#### To make the process more convenient users can choose a command: 
- /start - start working with the bot.
- /help - overview of available functionality.
- /date - see the current date and time.
- /fact - see your favorite post on cat-fact.herokuapp.com.
- /weather - see the weather
- /check_exchange_rates - see the dollar or euro rate for the current date.
- /corono_stats - overview the coronovirus state in the World

____

## What can WhyNot do for the authors? 

* Get information about the time between the last message sent from the bot and our time when we get the message of a user. This function helps to understand how opened for communication with the bot our user is. 
* Get information about the five last users, who were communicating with the bot.

#### To make the process more convenient its available to choose a command: 
			
- /elapsed_time - to get the time between messages 
- /history - to get the history of users

### How to install our chat_bot? 

1. Set up Python environment
2. Create virtual environment python -m venv venv
3. Activate virtual environment and install requirements:
	
	venv\Scripts\activate - on Linux

	venv\Scripts\activate.bat - on Windows

4. pip install -r requirements.txt

5. Execute python chat_bot_template.py
Try your bot - find it in Telegram and press /start.

