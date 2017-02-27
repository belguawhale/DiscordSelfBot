import discord
import asyncio
import aiohttp
import traceback
import datetime
import sys
import json
import os
from io import BytesIO, StringIO

client = discord.Client()

VERSION = '0.1.0'
PREFIX = "//"

MAX_RECURSION_DEPTH = 10

commands = {}
aliases = {}

if os.path.isfile('aliases.json'):
    with open('aliases.json', 'r') as aliases_file:
        aliases = json.load(aliases_file)
else:
    with open('aliases.json', 'a+') as aliases_file:
        aliases_file.write('{}')

def cmd(name, description, *aliases, server=True, pm=True):
    def real_decorator(func):
        commands[name] = [func, description, [server, pm]]
        for alias in aliases:
            if alias not in commands:
                commands[alias] = [func, "```\nAlias for {0}{1}.```".format(PREFIX, name), [server, pm]]
            else:
                print("ERROR: Cannot assign alias {0} to command {1} since it is already the name of a command!".format(alias, name))
        return func
    return real_decorator

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.invisible)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if not message.author.id == client.user.id:
        return
    if message.content.startswith(PREFIX):
        print('Command: ' + message.content)
    else:
        return
    command = message.content[len(PREFIX):].strip().split(' ')[0].lower()
    parameters = ' '.join(message.content.strip().split(' ')[1:])
    await parse_command(message, command, parameters)

async def parse_command(message, command, parameters, recursion=0):
    print("Parsing command {} with parameters {}".format(command, parameters))
    if recursion >= MAX_RECURSION_DEPTH:
        print("Hit max recursion depth of {}".format(MAX_RECURSION_DEPTH))
        await reply(message, "ERROR: reached max recursion depth of {}".format(MAX_RECURSION_DEPTH))
        return
    if message.channel.is_private:
        pm = True
    else:
        pm = False
    if command in commands:
        if pm and not commands[command][2][1]:
            await reply(message, "ERROR: Command {} may not be used in pm!".format(command))
            return
        elif not pm and not commands[command][2][0]:
            await reply(message, "ERROR: Command {} may not be used in a server!".format(command))
            return
        else:
            try:
                await commands[command][0](message, parameters)
            except:
                traceback.print_exc()
                try:
                    await reply(message, "An error has occurred and has been logged. See console for details.")
                except:
                    print("Printing error message failed, wtf?")
    elif command in aliases:
        aliased_command = aliases[command].split(' ')[0]
        actual_params = ' '.join(aliases[command].split(' ')[1:]).format(parameters, *parameters.split(' '))
        await parse_command(message, aliased_command, actual_params, recursion=recursion + 1)
    else:
        await reply(message, "Invalid command.")

@cmd("shutdown", "```\n{0}shutdown takes no arguments\n\nShuts the bot down.```")
async def cmd_shutdown(message, parameters):
    await reply(message, 'Shutting down...')
    await client.logout()

@cmd("ping", "```\n{0}ping takes no arguments\n\nTests the bot's connectivity.```")
async def cmd_ping(message, parameters):
    ts = message.timestamp
    new_msg = await reply(message, 'PONG!')
    latency = new_msg.edited_timestamp - ts
    await reply(message, "PONG! {}ms".format(latency.microseconds // 1000))

@cmd("eval", "```\n{0}eval <evaluation string>\n\nEvaluates <evaluation string> using Python's eval() function and returns a result.```")
async def cmd_eval(message, parameters):
    output = None
    if parameters == '':
        await reply(message, commands['eval'][1].format(PREFIX))
        return
    try:
        output = eval(parameters)
    except:
        await reply(message, '```\n' + str(traceback.format_exc()) + '\n```')
        traceback.print_exc()
        return
    if asyncio.iscoroutine(output):
        output = await output
    await reply(message, "**Input:**```\n{}\n```\n**Output:**```\n{}\n```".format(parameters, output))

@cmd("exec", "```\n{0}exec <exec string>\n\nExecutes <exec string> using Python's exec() function.```")
async def cmd_exec(message, parameters):
    if parameters == '':
        await reply(message, commands['exec'][1].format(PREFIX))
        return
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(parameters)
    except Exception:
        formatted_lines = traceback.format_exc().splitlines()
        await reply(message, '```py\n{}\n{}\n```'.format(formatted_lines[-1], '\n'.join(formatted_lines[4:-1])))
        return
    finally:
        sys.stdout = old_stdout

    await reply(message, "**Input:**```\n{}\n```\n**Output:**```\n{}\n```".format(parameters, redirected_output.getvalue()))

@cmd("info", "```\n{0}info takes no arguments\n\nDisplays information on the selfbot.```", "")
async def cmd_info(message, parameters):
    await reply(message, 'I am a Discord selfbot written in Python by belungawhale#4813 and am on version ' + VERSION + '. You can get me at https://github.com/belguawhale/DiscordSelfBot.')

@cmd("userinfo", "```\n{0}userinfo [<user>]\n\nDisplays information about [<user>].```", "uinfo")
async def cmd_userinfo(message, parameters):
    msg_server = message.server
    user = parameters.strip("<!@>")
    if not user:
        user = message.author.id
    if not user.isdigit():
        await reply(message, "ERROR: Please enter a valid user.")
        return
    msg = "```autohotkey\n"
    server = msg_server
    if not msg_server:
        temp_member = discord.utils.get(client.get_all_members(), id=user)
        if temp_member:
            server = temp_member.server
    if server:
        member = server.get_member(user)
        if not member:
            await reply(message, "ERROR: Please enter a valid member mention or id.")
            return
        msg += "              user: {member.name}#{member.discriminator}\n"
        msg += "          nickname: {member.nick}\n"
        msg += "      display name: {member.display_name}\n"
        msg += "                id: {member.id}\n"
        msg += "               bot: {member.bot}\n"
        msg += "            status: {member.status}\n"
        msg += "           playing: {member.game}\n"
    if msg_server:
        msg += "     voice channel: {member.voice.voice_channel}\n"
        msg += "             roles: " + ', '.join([x.name for x in server.role_hierarchy if x in member.roles]) + '\n'
        msg += "         joined at: {member.joined_at} ({} ago)\n".format(strfdelta(datetime.datetime.utcnow() - member.joined_at), member=member)
    else:
        await reply(message, "ERROR: Could not get info on user")
        return
    msg += "        created at: {member.created_at} ({} ago)\n".format(strfdelta(datetime.datetime.utcnow() - member.created_at), member=member)
    msg += "            avatar:```{member.avatar_url}"
    await reply(message, msg.format(member=member, server=server))

@cmd("serverinfo", "```\n{0}serverinfo takes no arguments\n\nDisplays information about the server this command was used in.```", "sinfo", pm=False)
async def cmd_serverinfo(message, parameters):
    server = message.server
    text = 0
    voice = 0
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            text += 1
        elif channel.type == discord.ChannelType.voice:
            voice += 1
    msg = "```autohotkey\n"
    msg += '                id: {server.id}\n'
    msg += '       server name: {server.name}\n'
    try:
        msg += '             owner: {server.owner.name}#{server.owner.discriminator} ({server.owner.id})\n'
    except:
        msg += '             owner: <error - could not get information on owner>\n'
    msg += '        created at: {server.created_at} ({} ago)\n'.format(strfdelta(datetime.datetime.utcnow() - server.created_at), server=server)
    msg += '            region: {server.region}\n'
    msg += '           members: {server.member_count}\n'
    msg += 'verification level: {server.verification_level}\n'
    msg += '          channels: {} channels ({} text, {} voice)\n'.format(text + voice, text, voice)
    if len(server.roles) > 50:
        msg += '             roles: {} roles, showing top 50\n{}\n'.format(len(server.roles), ', '.join([x.name for x in server.role_hierarchy][0:50]))
    else:
        msg += '             roles: {} roles\n{}'.format(len(server.role_hierarchy), ', '.join(map(lambda x: x.name, server.role_hierarchy)))
    msg += '            emojis: {}\n'.format(len(server.emojis))
    msg += '              icon:```{server.icon_url}'
    await reply(message, msg.format(server=server))

@cmd("removeallrole", "```\n{0}removeallrole <role name>\n\nRemoves <role name> from all members with that role.```", "rar", pm=False)
async def cmd_removeallrole(message, parameters):
    if parameters == "":
        await reply(message, commands['removeallrole'][1].format(PREFIX))
        return
    server = message.server
    role = None
    for temp_role in server.role_hierarchy:
        if temp_role.name == parameters:
            role = temp_role
            break
    if role:
        members_with_role = []
        for member in server.members:
            if role in member.roles:
                members_with_role.append(member)
        for member in members_with_role:
            await client.remove_roles(member, role)
        await reply(message, "Removed role **{}** from **{}** member{}.".format(role.name, len(members_with_role), '' if len(members_with_role) == 1 else 's'))
    else:
        await reply(message, "ERROR: could not find role named {}. Please ensure the role is spelled correctly and your capitalization is correct.".format(parameters))

@cmd("changegame", "```\n{0}changegame [<game>]\n\nChanges your Playing... message to [<game>] or unsets it.```")
async def cmd_changegame(message, parameters):
    if message.server:
        me = message.server.me
    else:
        me = list(client.servers)[0].me
    if parameters == '':
        game = None
    else:
        game = discord.Game(name=parameters)
    await client.change_presence(game=game, status=me.status)
    await reply(message, ":thumbsup:")

@cmd("changestatus", "```\n{0}changestatus <status>\n\nChanges your status. Status must be one of: online, idle, dnd, invisible.```")
async def cmd_changestatus(message, parameters):
    parameters = parameters.lower()
    statusmap = {'online' : discord.Status.online,
                 'idle' : discord.Status.idle,
                 'dnd' : discord.Status.dnd,
                 'invisible' : discord.Status.invisible}
    if message.server:
        me = message.server.me
    else:
        me = list(client.servers)[0].me
    if parameters == '':
        msg = "Your current status is " + str(me.status)
    else:
        if parameters in statusmap:
            await client.change_presence(status=statusmap[parameters], game=me.game)
            msg = ":thumbsup:"
        else:
            msg = "Status must be one of: online, idle, dnd, invisible."
    await reply(message, msg)
            
@cmd("role", "```\n{0}role <add | remove> <mention1 [mention2 ...]> <role name>\n\nAdds or removes <role name> from each member in <mentions>.```", pm=False)
async def cmd_role(message, parameters):
    server = message.server
    params = parameters.split(' ')
    if len(params) < 3:
        await reply(message, commands['role'][1].format(PREFIX))
        return
    action = params[0].lower()
    if action in ['add', '+']:
        action = 'add'
    elif action in ['remove', '-']:
        action = 'remove'
    else:
        await reply(message, "ERROR: first parameter must be one of: add, remove.")
        return
    params = params[1:]
    ids = [x.strip('<@!>') for x in params if x.strip('<@!>').isdigit()]
    params = [x for x in params if x.strip('<@!>') not in ids]
    members = [server.get_member(x) for x in ids]
    members = [x for x in members if x]
    if not members:
        await reply(message, "ERROR: no valid mentions found.")
        return
    role = ' '.join(params)
    if not role:
        await reply(message, "ERROR: no role name given!")
        return
    roles = [x for x in server.role_hierarchy if x.name == role]
    if not roles:
        await reply(message, "ERROR: could not find role named {}. Please ensure the role is spelled correctly and your capitalization is correct.".format(role))
        return
    role = roles[0]
    if action == 'add':
        function = client.add_roles
    elif action == 'remove':
        function = client.remove_roles
    for member in members:
        await function(member, role)
    if action == 'add':
        msg = "Successfully added **{}** to **{}** member{}."
    elif action == 'remove':
        msg = "Successfully removed **{}** from **{}** member{}."
    await reply(message, msg.format(role.name, len(members), '' if len(members) == 1 else 's'))

@cmd("help", "```\n{0}help <command>\n\nDisplays hopefully helpful information on <command>. Try {0}list for a listing of commands.```")
async def cmd_help(message, parameters):
    if parameters == "":
        parameters = "help"
    if parameters in commands:
        await reply(message, commands[parameters][1].format(PREFIX))
    else:
        await reply(message, "Command {} does not exist.".format(parameters))

@cmd("list", "```\n{0}list takes no arguments\n\nDisplays a listing of commands.```")
async def cmd_list(message, parameters):
    await reply(message, "Available commands: {}".format(', '.join(sorted(commands))))

@cmd("reply", "```\n{0}reply <message>\n\nReplies with <message>. Use with aliases for more fun!```")
async def cmd_reply(message, parameters):
    await reply(message, parameters)

@cmd("alias", "```\n{0}alias <add | edit | remove | list | show> <alias name> [<command string>]\n\nManipulates aliases.```")
async def cmd_alias(message, parameters):
    params = parameters.split(' ')
    if len(params) == 0:
        await reply(message, commands['alias'][1].format(PREFIX))
        return
    action = params[0]
    if action not in ['add', '+', 'edit', '=', 'remove', 'del', 'delete', '-', 'list', 'show']:
        await reply(message, commands['alias'][1].format(PREFIX))
        return
    if len(params) == 1:
        if action in ['add', '+', 'edit', '=']:
            await reply(message, "```\n{0}alias {1} <alias name> <command string>```".format(PREFIX, action))
        elif action in ['show', 'remove', '-', 'del', 'delete']:
            await reply(message, "```\n{0}alias {1} <alias name>```".format(PREFIX, action))
        elif action == 'list':
            await reply(message, "Available aliases: {}".format(', '.join(sorted(aliases))))
        return
    alias = params[1]
    if not alias in aliases and action not in ['add', '+']:
        await reply(message, "ERROR: alias {} does not exist!".format(alias))
        return
    if len(params) == 2:
        if action in ['add', '+', 'edit', '=']:
            await reply(message, "```\n{0}alias {1} {2} <command string>```".format(PREFIX, action, alias))
        elif action == 'show':
            await reply(message, "**{}** is an alias for: ```\n{}\n```".format(alias, aliases[alias]))
        elif action in ['remove', 'del', 'delete', '-']:
            del aliases[alias]
            await reply(message, "Successfully deleted alias **{}**.".format(alias))
    else:
        commandstring = ' '.join(params[2:])
        aliases[alias] = commandstring
        await reply(message, "Successfully {} alias **{}**.".format(action + "ed", alias))
    with open('aliases.json', 'w') as aliases_file:
        json.dump(aliases, aliases_file)
                    
def strtodatetime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')

def strfdelta(delta):
    output = [[delta.days, 'day'],
              [delta.seconds // 3600, 'hour'],
              [delta.seconds // 60 % 60, 'minute'],
              [delta.seconds % 60, 'second']]
    for i in range(len(output)):
        if output[i][0] != 1:
            output[i][1] += 's'
    reply_msg = ''
    if output[0][0] != 0:
        reply_msg += "{} {} ".format(output[0][0], output[0][1])
    for i in range(1, len(output)):
        reply_msg += "{} {} ".format(output[i][0], output[i][1])
    reply_msg = reply_msg[:-1]
    return reply_msg

async def reply(message, text):
    return (await client.edit_message(message, message.author.mention + ', ' + text))

























client.run('Email','Password')
