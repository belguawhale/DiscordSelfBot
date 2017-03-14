# Discord Self Bot
A selfbot (runs on your user account and provides extra functionality) for Discord written in Python.
You can find me on Discord as belungawhale#4813.

## Installation
Clone this repository, edit the Email and Password fields at the bottom of selfbot.py, and run `python selfbot.py` (on UNIX based systems, you may need to run `python3 selfbot.py` or `python3.5 selfbot.py`. If you want the bot to auto-restart on Windows, run the provided selfbot.bat file.

## Documentation
The bot only responds to the account the bot is running on, obviously.
### Commands
Use `//list` to list all commands, `//alias list` to list all aliases, `//help command` to return help for a command, and `//alias show alias` to show what alias is an alias for.

## Changelog
### v0.1.2
Added: Variants of eval and exec. `//oldeval` and `//oldexec` show only the output, and `//silenteval` and `//silentexec` return nothing.

Added: Echo command. This command simply sends a message to the same channel this command was used in.

Added: Timer command. This displays a running timer.

Changed: Say command can send messages to users too.

### v0.1.1
Added: Scheduler command! Use this to schedule commands. Examples: `//scheduler add 1m reply 1 minute passed!` `//scheduler add 5h role - @baduser Muted` Note: All scheduled commands are lost on bot restart due to it requiring a Message object.

Added: Say command. Use `//say #channel message`.

Changed: Minor bugfixes

### v0.1.0
#### MAJOR UPDATE!
I did a complete rewrite of the bot, using a brand new commands parser I wrote!

Added: Aliases! Try `//alias` for documention. Examples: `//alias add time eval datetime.datetime.now()` `//alias add mute role add {0} Muted` (the {0} inputs all parameters. Use {1} for first parameter, {2} for second parameter, etc.)

Added: Help command! Try `//help command`

Added: List command to display all commands!

Added: Reply command (aliases are especially fun with this one! Example: `//alias add give reply gives a {1} to {2}`)

Added: Error handling for errors!

Changed: Userinfo and serverinfo commands now display time since joined

Changed: Rewrites to many commands to make them more streamlined

Changed: `//ping` now displays latency!

Changed: `//eval` and `//exec` have a better-looking interface

Changed: Many bugfixes

### v0.0.3
Changed: `//role` now takes any number of mentions rather than just one mention

Changed: Bot now edits the message instead of sending a new message

Changed: Some formatting stuff like bolding some things in reply message

### v0.0.2.1
Changed: Username to Email since it was confusing

### v0.0.2
Added: `//role` and `//info` commands

Added: Help information for some commands (if you just do `//role` for example, it will return help for the command `//role`)

### v0.0.1
Initial commit

## Acknowledgements
Thanks to SexualRhinoceros for making RH1-N0, a discord bot in Python which inspired me to try writing stuff for Discord. The eval and exec commands are taken from SexualRhinoceros's code.