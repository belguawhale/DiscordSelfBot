# Discord Self Bot
A selfbot (runs on your user account and provides extra functionality) for Discord written in Python.
You can find me on Discord as belungawhale#4813.

## Installation
Clone this repository, edit the Email and Password fields at the bottom of selfbot.py, and run `python selfbot.py` (on UNIX based systems, you may need to run `python3 selfbot.py` or `python3.5 selfbot.py`. If you want the bot to auto-restart on Windows, run the provided selfbot.bat file.

## Documentation
The bot only responds to the account the bot is running on, obviously.
### Commands
* `//ping`: Simply checks if the bot is running or not.
* `//info`: Returns information about the bot
* `//shutdown`: Shuts down the bot. If you are running the auto-restarter, the bot will automatically restart after 5 seconds. Useful for running the bot after you edit the code.
* `//eval`: Evaluates a Python expression using `eval()` and replies with the result.
* `//exec`: Executes a Python command and replies with the redirected stdout.
* `//userinfo`: Gets information of a user by mention, id, or name. It will give information on the discord.Member if the command is run in a server, otherwise it will get information on the discord.User.
* `//serverinfo`: Gets information on the server the command is used in.
* `//removeallrole`: A utility command to remove the specified role from all members in a server who have that role.
* `//changegame`: Changes your Playing... status on Discord. Note that the Discord client may not update this, but it will show for other users.
* `//changestatus`: Changes your status to online, idle, dnd, or invisible. This does not work for some reason though.
* `//role`: Adds or removes a role from a member.

## Changelog
### v0.0.2.1
Changed Username to Email since it was confusing

### v0.0.2
Added `//role` and `//info` commands
Added Help information for some commands (if you just do `//role` for example, it will return help for the command `//role`)

### v0.0.1
Initial commit

## Acknowledgements
Thanks to SexualRhinoceros for making RH1-N0, a discord bot in Python which inspired me to try writing stuff for Discord. The eval and exec commands are taken from SexualRhinoceros's code.