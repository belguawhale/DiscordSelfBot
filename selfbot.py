import discord
import asyncio
import traceback
import sys
from io import BytesIO, StringIO

client = discord.Client()

VERSION = '0.0.2'

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print(client)


@client.event
async def on_message(message):
    if not message.author.id == client.user.id:
        return
    if message.content.startswith('//'):
        print('Command: ' + message.content)
    command = message.content
    parameters = ' '.join(message.content.strip().split(' ')[1:])
    if command.startswith('//shutdown'):
        await reply(message, ':thumbsup:')
        await client.logout()
    elif command.startswith('//ping'):
        await reply(message, 'PONG!')
    elif command.startswith('//pong'):
        await reply(message, '\\*ping\\*')
    elif command.startswith('//info'):
        await reply(message, 'I am a Discord selfbot written in Python by belungawhale and am on version ' + VERSION + '. You can get me at https://github.com/belguawhale/DiscordSelfBot.')
    elif command.startswith('//eval'):
        output = None
        if parameters == '':
            await reply(message, '```//eval <evaluation string>\n\nEvaluates <evaluation string> using Python\'s eval() function and returns a result```')
            return
        try:
            output = eval(parameters)
        except:
            await reply(message, '```\n' + str(traceback.format_exc()) + '\n```')
            traceback.print_exc()
        if asyncio.iscoroutine(output):
            output = await output
        if output:
            await reply(message, '```\n' + str(output) + '\n```')
    elif command.startswith('//exec'):
        if parameters == '':
            await reply(message, '```//exec <exec string>\n\nExecutes <exec string> using Python\'s exec() function```')
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

        if redirected_output.getvalue():
            await reply(message, redirected_output.getvalue())
            return
        await reply(message, ':thumbsup:')
        return
    elif command.startswith('//userinfo'):
        user_check = parameters.split(' ')[0]
        if parameters == '':
            user_id = message.author.id
        elif user_check.startswith('<@') & user_check.endswith('>'):
            user_id = user_check.strip('<@!>')
            if not user_id.isdigit():
                await reply(message, 'ERROR: Please enter a valid user.')
                return
        elif user_check.isdigit():
            user_id = user_check
        else:
            temp_user = None
            for i in client.get_all_members():
                if i.name.lower() == user_check:
                    temp_user = i
                    break
            if temp_user == None:
                await reply(message, 'Could not get info on user ' + user_check)
                return
            user_id = temp_user.id
        if message.server:
            user_member = message.server.get_member(user_id)
        else:
            user_member = None
        if user_member:
            role_string = ''
            for role in user_member.roles:
                role_string += role.name + ', '
            role_string = role_string.rstrip(', ')
            # member is same server as command
            user_info = ['```xl\n'
                         '           user: ' + user_member.name + '#' + user_member.discriminator,
                         '       nickname: ' + str(user_member.nick),
                         '   display name: ' + user_member.display_name,
                         '             id: ' + user_member.id,
                         '            bot: ' + str(user_member.bot),
                         '         status: ' + str(user_member.status),
                         '        playing: ' + str(user_member.game),
                         '  voice channel: ' + str(user_member.voice.voice_channel),
                         '          roles: ' + role_string,
                         '     created at: ' + str(discord.utils.snowflake_time(user_member.id)),
                         '         joined: ' + str(user_member.joined_at),
                         '         avatar:```' + str(user_member.avatar_url)
                         ]
        else:
            for i in client.get_all_members():
                if i.id == user_id:
                    user_member = i
            try:
                user_user = user_member
                # user is not in server where command was used
                user_info = ['```xl\n'
                         '           user: ' + user_user.name + '#' + user_user.discriminator,
                         '   display name: ' + user_user.display_name,
                         '             id: ' + user_user.id,
                         '            bot: ' + str(user_user.bot),
                         '     created at: ' + str(discord.utils.snowflake_time(user_user.id)),
                         '         avatar:```' + str(user_user.avatar_url)
                         ]
            except Exception as e:
                print(e)
                await reply(message, 'Could not get info on user with id ' + user_id)
                return
        await reply(message, '\n'.join(user_info))
    elif command.startswith('//serverinfo'):
        if message.server == None or message.server.unavailable:
            await reply(message, 'ERROR: serverinfo command may only be used in a server')
            return
        else:
            server = message.server
            role_string = ''
            for role in server.role_hierarchy:
                role_string += role.name + ', '
            role_string = role_string.rstrip(', ')
            server_members = 0
            server_channels = 0
            server_voice = 0
            for i in server.members:
                server_members += 1
            for i in server.channels:
                if i.type == discord.ChannelType.text:
                    server_channels += 1
                elif i.type == discord.ChannelType.voice:
                    server_voice += 1
            server_info = ['```xl\n'
                           '                id: ' + server.id,
                           '       server name: ' + server.name,
                           '             owner: ' + server.owner.name + '#' + server.owner.discriminator + ' (' + server.owner.id + ')',
                           '        created at: ' + str(server.created_at),
                           '            region: ' + str(server.region),
                           '           members: ' + str(server.member_count),
                           'verification level: ' + str(server.verification_level),
                           '          channels: ' + str(server_channels + server_voice),
                           '              text: ' + str(server_channels),
                           '             voice: ' + str(server_voice),
                           #'   number of roles: ' + str(len(role_string.split(', '))),
                           '             roles: ' + str(len(role_string.split(', '))) + ' total roles: ' + role_string,
                           '              icon:```' + str(server.icon_url)
                           ]
            await reply(message, '\n'.join(server_info))
    elif command.startswith('//removeallrole'):
        if parameters == '':
            await reply(message, '```//removeallrole <role>\n\nRemoves <role> from all members in the current server who have <role>```')
            return
        #print('Role to remove: ' + parameters)
        if message.server == None or message.server.unavailable:
            await reply(message, 'ERROR: removeallrole command may only be used in a server')
            return
        else:
            server = message.server
            server_role = None
            for role in server.role_hierarchy:
                if role.name.lower() == parameters.lower():
                    server_role = role
            if server_role == None:
                await reply(message, 'ERROR: Could not find a role named ' + parameters + ' in the server')
                return
            #print(server_role.name)
            members_with_role = []
            for member in server.members:
                if server_role in member.roles:
                    members_with_role.append(member)
            #print(members_with_role)
            for member in members_with_role:
                await client.remove_roles(member, server_role)
            await reply(message, 'Removed ' + server_role.name + ' from ' + str(len(members_with_role)) + ' members')
    elif command.startswith('//changegame'):
        if parameters in ['none','None']:
            await client.change_presence(game=None,status=message.server.me.status)
            await reply(message, ':thumbsup:')
        else:
            await client.change_presence(game=discord.Game(name=parameters),status=message.server.me.status)
            print(parameters)
            await reply(message, ':thumbsup:')
    elif command.startswith('//changestatus'):
        string_status = str(parameters).lower()
        if string_status in ['online','idle','dnd','invisible']:
            if string_status == 'online':
                object_status = discord.Status.online
            elif string_status == 'idle':
                object_status = discord.Status.idle
            elif string_status == 'dnd':
                object_status = discord.Status.dnd
            elif string_status == 'invisible':
                object_status = discord.Status.invisible
            await client.change_presence(game=message.server.me.game,status=object_status)
            await reply(message, ':thumbsup:')
        else:
            await reply(message, 'Status must be online, idle, dnd, or invisible.')
    elif command.startswith('//role'):
        if parameters == '':
            await reply(message, '```//role <add / + / remove / - > <mention> <role name>\n\nAdds or removes <role name> from <mention>```')
            return
        if message.server == None or message.server.unavailable:
            await reply(message, 'ERROR: role must be used in a server')
            return
        if len(parameters.split(' ')) < 2:
            await reply(message, 'ERROR: missing parameters')
            return
        if parameters.split(' ')[0].lower() not in ['add', '+', 'remove', '-']:
            await reply(message, 'ERROR: first parameter must be one of the following: add, +, remove, -')
            return
        mode = parameters.split(' ')[0].lower()
        if not parameters.split(' ')[1].strip('<@!>').isdigit():
            await reply(message, 'ERROR: second parameter must be a mention')
            return
        member_id = parameters.split(' ')[1].strip('<@!>')
        member = message.server.get_member(member_id)
        role = None
        for i in message.server.role_hierarchy:
            if i.name.lower() == ' '.join(parameters.split(' ')[2:]).lower():
                role = i
        if role == None:
            await reply(message, 'ERROR: role ' + ' '.join(parameters.split(' ')[2:]) + ' was not found')
            return
        if member == None:
            await reply(message, 'ERROR: member with id ' + member_id + ' was not found in this server')
            return
        print(mode + ' ' + member.name + ' ' + role.name)
        if mode in ['add','+']:
            await client.add_roles(member, role)
            await reply(message, ':thumbsup:')
            return
        elif mode in ['remove', '-']:
            await client.remove_roles(member, role)
            await reply(message, ':thumbsup:')
            return

async def reply(message, text):
    await client.send_message(message.channel, message.author.mention + ', ' + text)

client.run('Username','Password')
