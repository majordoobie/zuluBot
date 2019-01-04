from discord.ext import commands
import discord
from discord import Embed, Game, Guild
from CoC_API import CoC
from CoC_Stats import CoC_Stats
from ZuluBot_DB import ZuluDB
from collections import OrderedDict
from configparser import ConfigParser
from requests import get
from datetime import datetime, timedelta
import pandas as pd
import asyncio

#Permissions
# create_instant_invite

config = ConfigParser()
config.read('zuluConfig.ini')
discord_client = commands.Bot(command_prefix = config['Bot']['Bot_Prefix'])
discord_client.remove_command("help")
coc_client = CoC(config['Clash']['ZuluClash_Token'])
DB = ZuluDB()

# Question function for await
def yesno_check(m):
        if m.content.lower() in ['yes','no']:
            return True
        else:
            return False

# Function to check if user is a leader/admin
def authorized(users_roles):
    for role in users_roles:
        if role.name == "CoC Leadership":
            return True
    return False

# Check if discord_ID is part of the server
def is_DiscordUser(member_ID):
    guild_obj = discord_client.get_guild(int(config['Discord']['ZuluDisc_ID']))
    user_obj = guild_obj.get_member(int(member_ID))
    if user_obj == None:
        return False, None
    else:
        return True, user_obj

# Function for getting the TH object role by providing the TH level with CoC_API
def get_THRole(userLevel):
    guild_obj = discord_client.get_guild(int(config['Discord']['ZuluDisc_ID']))
    levels = [9, 10, 11, 12]
    str_roles = ['th9s', 'th10s', 'th11s', 'th12s']
    for level, str_role in zip(levels, str_roles):
        if userLevel == level:
            objRole = guild_obj.get_role(int(config['Discord Roles'][str(str_role)]))
            return objRole, str_role
    return None, None

# create an invitation for the planning server
def invite():
    obj = discord_client.get_guild(int(config['Discord']['PlanDisc_ID']))
    channel = obj.get_channel(int(config['Discord']['PlanDisc_Channel']))
    return channel

# find the datetime object that represents last sunday at 8pm (EST) 
# in UTC this is Monday at 1am
def lastSunday():
    today = datetime.utcnow()
    delta = 1 - today.isoweekday()
    monday = today + timedelta(delta)
    return_date = monday.strftime('%Y-%m-%d')+" 01:00:00"
    return return_date


# backgroup query refresh
async def weeklyRefresh():
    await discord_client.wait_until_ready()
    while not discord_client.is_closed():
        # Calculate the wait time in minute for next "top of hour"
        wait_time = 60 - datetime.utcnow().minute
        if wait_time <= 15:
            pass
        elif wait_time <= 30:
            wait_time = wait_time - 15
        elif wait_time <= 45:
            wait_time = wait_time - 30
        else:
            wait_time = wait_time - 45

        print(f"Waiting {wait_time} minutes until next update.")
        await asyncio.sleep(wait_time * 60)

        # Get all users in the databse
        get_all = DB.get_allUsers()
        mem_ids = [ mem.id for mem in discord_client.get_guild(int(config['Discord']['PlanDisc_ID'])).members ]

        # See if the users are still part of the clan
        user = ''
        for user in get_all:
            if user[7] == "False":
                continue
            else:
                pass
            # Make user each user is in the planning server. Adjust their row accordingly 
            if user[6] == "True" and (user[4] in mem_ids):
                pass
            elif user[6] == "True" and (user[4] not in mem_ids):
                DB.set_inPlanning("False", user[0])
            elif user[6] == "False" and (user[4] in mem_ids):
                DB.set_inPlanning("True", user[0])
            elif user[6] == "False" and (user[4] not in mem_ids):
                pass
            else:
                print("Error")

            # Grab the users CoC stats to see if there is any updates needed on their row
            res = coc_client.get_member(user[0])
            mem_stat = CoC_Stats(res.json())
            if res.status_code != 200:
                  print(f"Could not connect to CoC API with {user[0]}")
                  return

            # Grab the users discord object and the object for the TH role
            exists, disc_UserObj = is_DiscordUser(user[4])
            if exists == False:
                print(f"User does not exist {user[4]}")
                continue
            roleObj_TH, roleStr_TH = get_THRole(mem_stat.th_lvl)
            
            # find if their TH role has changed
            for role in disc_UserObj.roles:
                if role.name.startswith('th'):
                    if role.name == roleObj_TH.name:
                        pass
                    else:
                        print("Updating TH level role")
                        await disc_UserObj.remove_roles(role)      # remove old th role
                        await disc_UserObj.add_roles(roleObj_TH)   # Give user TH# ROLE

            # Update donation table
            in_zulu = "False"
            if mem_stat.currentClan_name == "Reddit Zulu":
                in_zulu = "True"
            else:
                in_zulu = "False"
            DB.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    mem_stat.coc_tag,
                    mem_stat.total_Donations,
                    in_zulu,
                    mem_stat.trophies
                ))

            # update users table
            DB.update_users(mem_stat.coc_tag, mem_stat.th_lvl, mem_stat.league)


@discord_client.command()
async def test(ctx):
    pass
    

@discord_client.command()
async def kill(ctx):
    if int(ctx.message.author.id) == int(config['Discord']['KillSwitch']):
        await ctx.send("Closing database..")
        DB.conn.close()
        await ctx.send("Terminating bot..")
        await ctx.send("_Later._")
        await discord_client.logout()

@discord_client.command()
async def help(ctx):
    arg = ctx.message.content.split(" ")[1:]
    if len(arg) == 0:
        embed = Embed(color=0x8A2BE2)
    elif arg[0] == '-v':
        embed = Embed(color=0x8A2BE2)
    elif arg[0] == '-vv':
        desc = ("Welcome to Zulu's donation tracker!")
        embed = Embed(title='NameComingSoon!', description= desc, color=0x8A2BE2)

    embed.add_field(name="Commands:", value="-----------", inline=True)
    
    helpp = ("Provides this help menu. \nOptional: -v provide CoC Leaders commands "
    "\nOptional: -vv provide a indepth description of the bot.")
    embed.add_field(name="/help <opt: -v>", value=helpp, inline=False)

    newinvite = ("Provides caller with a temporary link to the planning server with a default "
    "expiration of 10 minutes. You have the option of providing an integer which changes the "
    "expiration in minutes.")
    embed.add_field(name="/newinvite <opt: int>", value=newinvite, inline=False)

    lcm = ("Provides caller with a list of names and tags of all the users currently in Zulu.")
    embed.add_field(name="/lcm", value=lcm, inline=False)

    donation = ("Provides the caller with their donation progress for the week. The caller has the "
    "option of providing a clash tag to get the status of other users. A list of tags can be found in /lcm. "
    "\nNOTE: A full week must pass for the progression counts to be accurate.")
    embed.add_field(name="/donation <opt: clash tag>", value=donation, inline=False)

    if arg and (arg[0] == "-v" or arg[0] == "-vv"):
        embed.add_field(name="..", value="..", inline = False)
        embed.add_field(name="Commands: CoC Leaders", value="-----------", inline=True)

        useradd = ("Register the a new user into the SQL DataBase. This will also set default discord "
        "roles such as TH# role and CoC Members role. Finally, the users nickname will be changed "
        "to reflect their in game name.")
        embed.add_field(name="/useradd <@discord_mention> <#coc_tag>", value=useradd, inline=False)

        userkick = ('Places a "is_Active = False" flag on the user to stop the bot from tracking the user. '
        'The caller will be prompt with the option of adding an administrative note such as '
        '"User was kicked for misconduct" or "User is on temporary leave". These notes can be retrived with the '
        '"insert command here for it" command.')
        embed.add_field(name="/userkick <#coc_tag>", value=userkick, inline=False)

        activeUsers = ('Queries the database for all the users that are "active". This is helpful '
        'to verify users that are kicked.')
        embed.add_field(name="/active_users", value=activeUsers, inline=False)

        listroles = ("Simple command used for debugging.")
        embed.add_field(name="/listroles", value=listroles, inline=False)

        killit = ("Command to safely terminate the bot.")
        embed.add_field(name="/killswitch", value=killit, inline=False)

    
    await ctx.send(embed = embed)





@discord_client.command()
async def newinvite(ctx):
    arg = ctx.message.content.split(" ")[1:]
    if len(arg) == 1 and arg[0].isdigit():
        inv = await invite().create_invite(max_age = (int(arg[0]) *60), max_uses = 1 )
        await ctx.send(inv)
    if len(arg) == 0:
        inv = await invite().create_invite(max_age = 600, max_uses = 1 )
        await ctx.send(inv)
    return


@discord_client.command()
async def listroles(ctx):
    tupe = []
    guild_obj = discord_client.get_guild(int(config['Discord']['ZuluDisc_ID']))
    for i in guild_obj.roles:
        tupe.append((i.name,i.id))

    max_length = 0
    for name in tupe:
        if len(name[0]) > max_length:
            max_length = len(name[0])
    tupe.sort()

    output = ''
    for name in tupe:
        output += "{:<{}} {}\n".format(name[0], max_length, name[1])

    await ctx.send("```{}```".format(output))


@discord_client.command()
async def lcm(ctx):
    # Read clan code to query the clans users list
    res = coc_client.get_clan(config['Clash']['ZuluClash_Tag'])

    # Quick check to  make sure that the https request was good
    if int(res.status_code) > 300:
        embed = Embed(color=0xff0000)
        msg = ("Bad HTTPS request, please make sure that the bots IP is in the CoC whitelist."
        "Our current exit node is {}".format(get('https://api.ipify.org').text))
        embed.add_field(name="Bad Request: {}".format(res.status_code),value=msg)
        await ctx.send(embed=embed)
        return

    #here we'll ad our actual lcm code
    else:
        #conver json into a list
        mem_list = []
        for user in res.json()['memberList']:
            mem_list.append((user['name'],user['tag']))

        #sort the list and get the max length
        max_length = 0
        for user in mem_list:
            if len(user[0]) > max_length:
                max_length = len(user[0])
        mem_list.sort()

        output = ''
        for user in mem_list:
            output += "{:<{}} {}\n".format(user[0], max_length, user[1])

        await ctx.send("```{}```".format(output))


@discord_client.command()
async def useradd(ctx):
    """
        This section is used to add users to the DB
    """
    # If user is authorized to use this command 
    if authorized(ctx.message.author.roles):
        while True:
            args = ctx.message.content.split(" ")[1:]
            #
            # allocate the discord ID variable and CoC name 
            #
            if len(args) == 2:
                # Get the Clash tag of the user
                coc_Tag = args[1].lstrip("#")  # converts #PJK123 to PJK123

                # Get discord ID of the user
                if args[0].startswith("<"):
                    # this turns <@123456> to 123456
                    member_ID = ''.join(list(args[0])[2:-1])
                    # If user already has a nickname, their discord ID will begin with a ! 
                    if member_ID.startswith("!"):
                        member_ID = member_ID[1:]
                else:
                    # if user supplied a string instead of a mention throw an error
                    msg = ("Can't interpret discord user name argument **{}** make sure you're" 
                    "using the '@' prefix and you're allowing discord to highlight the 'mention'.".format(args[0]))        
                    await ctx.send(embed=Embed(title=msg, color=0xff0000))
                    break
                #
                # Make sure discord ID exists in the discord
                #
                exists, disc_UserObj = is_DiscordUser(member_ID)
                if exists == False:
                    embed = Embed(color=0xff0000)
                    msg = "User provided **{}** is not a member of this discord server.".format(args[0])
                    embed.add_field(name="Input Error",value=msg)
                    await ctx.send(embed=embed)
                    break
                #
                # Attempt to make a CoC api request to make sure
                # user tag supplied exists
                #
                res = coc_client.get_member(coc_Tag)
                if res.status_code != 200:
                    msg = "CoC tag `{}` was not found in Reddit Zulu\n Use the /lcm command to list Reddit Zulu Tags".format(coc_Tag)
                    await ctx.send(embed = Embed(title=msg, color=0xff0000))
                    break
                #
                # Break out the json and start adding the user
                # coc_R == response 
                #
                mem_stat = CoC_Stats(res.json())
                roleObj_CM = discord_client.get_guild(int(config['Discord']['ZuluDisc_ID'])).get_role(int(config['Discord Roles']['CoC_Members']))
                roleObj_TH, roleStr_TH = get_THRole(mem_stat.th_lvl)
                if roleObj_TH == None:
                    msg = f"{mem_stat.coc_name} has a Town Hall level that is not supported: TH{mem_stat.th_lvl}."
                    await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
                    return

                #
                # Print out the warning
                #
                msg = "Standby, giving {} default roles, and changing their nickname on discord to reflect their in game name.".format(mem_stat.coc_name)
                await ctx.send(embed = Embed(title=msg, color=0x5c0189))
                #
                # Adding CoC Members role
                #
                flag = True
                for role in disc_UserObj.roles:
                    if role.name == "CoC Members":
                        flag = False
                        await ctx.send(embed = Embed(title=f"{mem_stat.coc_name} already has 'CoC Members' role assigned.", color=0xFFFF00))
                
                if flag:
                    await disc_UserObj.add_roles(roleObj_CM) # Give user CoC Members role
                    await ctx.send(embed = Embed(title=f"Successfully assigned {mem_stat.coc_name} 'CoC Members' role.", color=0x00ff00))
                #
                # Adding TH# Members role
                #
                flag = True
                for role in disc_UserObj.roles:
                    if role.name.startswith('th'):
                        flag = False
                        if role.name == roleObj_TH.name:
                            msg = f"{mem_stat.coc_name} already has {roleObj_TH.name} role assigned."
                            await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                        else:
                            await disc_UserObj.remove_roles(role)      # remove old th role
                            await disc_UserObj.add_roles(roleObj_TH)   # Give user TH# ROLE
                            msg = (f"Succesfully removed {role.name} and assigned {roleObj_TH}")
                            await ctx.send(embed = Embed(title=msg, color=0x00ff00))
                if flag:
                    await disc_UserObj.add_roles(roleObj_TH) # Give user TH# ROLE
                    msg = f"Successfully assigned {mem_stat.coc_name} {roleStr_TH} role."
                    await ctx.send(embed = Embed(title=msg, color=0x00ff00))

                
                #
                # Chaning users nickname
                #
                if disc_UserObj.display_name != mem_stat.coc_name:
                    old_name = disc_UserObj.display_name
                    try:
                        await disc_UserObj.edit(nick=mem_stat.coc_name)
                        msg = f"Changed {mem_stat.coc_name}'s nickname from [{old_name}] to [{mem_stat.coc_name}]."
                        await ctx.send(embed = Embed(title=msg, color=0x00ff00))
                    except:
                        msg = f"It is impossible to change the nickname of discord server owners."
                        await ctx.send(embed = Embed(title=f"**DISCORD ERROR**", description=msg, color=0xff0000))
                else:
                    msg = f"{mem_stat.coc_name} nickname already reflects their CoC name."
                    await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                #
                # Add user to database
                #
                #
                msg = f"Adding {mem_stat.coc_name}'s data to the database"
                await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                send = DB.insert_userdata((
                    mem_stat.coc_tag,
                    mem_stat.coc_name,
                    mem_stat.th_lvl,
                    mem_stat.league,
                    disc_UserObj.id,
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "False",
                    "True",
                    None
                ))
                
                if send != None:
                    if send.args[0] == "database is locked": #e.args[0] == 'database is locked'
                        msg = "Terminating to prevent corruption. Please release handles to databse before using me."
                        await ctx.send(embed = Embed(title=f"**SQL ERROR**\n__{send}__", description=msg, color=0xff0000))
                        await ctx.send("Terminating process..")
                        return

                    msg = f"Clash tag {mem_stat.coc_tag} already exists in the database."
                    await ctx.send(embed = Embed(title=f"**SQL ERROR**\n__{send}__", description=msg, color=0xff0000))
                    
                    # Query to see why the user is already in the database
                    user_row = DB.is_Active(mem_stat.coc_tag)
                    # If user is in the database and is active exit. 
                    if user_row[7] == "True":
                        msg = (f"{mem_stat.coc_name} is already registered and their active status is set to True. "
                        "Terminating user enrollment.")
                        await ctx.send(embed = Embed(title=f"**User Status:** TRUE\n__{send}__", description=msg, color=0x5c0189))
                        return
                    # If user is in the database and was not active, ask if they really want to add someone they kicked
                    elif user_row[7] == "False":
                        msg = (f"{mem_stat.coc_name} is already registered, but has a active status of False. "
                        f"The reasoning if supplied by admin is:\n\n---\n{user_row[8]}")
                        await ctx.send(embed = Embed(title=f"**User Status:** TRUE\n{send}", description=msg, color=0x5c0189))
                        await ctx.send("Would you like to continue adding them? (Yes/No)")
                        msg = await discord_client.wait_for('message', check = yesno_check)
                        if msg.content.lower() == 'no':
                            await ctx.send("Terminating process.")
                            return
                        elif msg.content.lower() == 'yes':
                            await ctx.send(f"Changing {mem_stat.coc_name} active status to True.")
                            DB.set_Active("True", mem_stat.coc_tag)
                            
                
                send = DB.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    mem_stat.coc_tag,
                    mem_stat.total_Donations,
                    "True",
                    mem_stat.trophies
                ))
                if send != None:
                    msg = f"Operational Error while inserting data."
                    await ctx.send(embed = Embed(title=f"**SQL ERROR**\n{send}", description=msg, color=0xff0000))
                #
                # Welcome the user and display their stats
                #
                await ctx.send(await invite().create_invite(max_age = 600, max_uses = 1))
                msg = (f"{disc_UserObj.mention}, welcome to Zulu! "
                "Don't forget to join the planning server! The server is used to plan "
                "attacks and get feedback from your clanmates.")
                await ctx.send(msg)
                break
    
            else:
                msg = "This command only takes two arguments. Try /help"
                await ctx.send(embed = Embed(title=msg, color=0xff0000))
                return
    else:
        msg = "Sorry, you don't have the approved role for this command."
        await ctx.sendy(embed = Embed(title=msg, color=0xff0000))

@discord_client.command()
async def active_users(ctx):
    """
    Get a list of all users that have the active flag set to true in the database
    """
    if authorized(ctx.message.author.roles):
        rows = DB.get_allUsers()
        mem_ids = [ mem.id for mem in discord_client.get_guild(int(config['Discord']['PlanDisc_ID'])).members ]
        for row in rows:
            if row[6] == "True" and (row[4] in mem_ids):
                print("passing")
                pass
            elif row[6] == "True" and (row[4] not in mem_ids):
                print("hello")
                DB.set_inPlanning("False", row[0])
            elif row[6] == "False" and (row[4] in mem_ids):
                print('yo')
                rows = DB.set_inPlanning("True", row[0])
                print(rows)
            elif row[6] == "False" and (row[4] not in mem_ids):
                print("passing2")
                pass
            else:
                print("Error")

            if row[4] in mem_ids:
                await ctx.send(embed = Embed(title=f"{row[1]}", description=f"{row[0]}",color=0x8A2BE2))
            else:
                await ctx.send(embed = Embed(title=f"{row[1]}", description=f"{row[0]}\n{row[1]} is not in the planning server. Please use /newinvite",color=0xFF0000))

    else:
        msg = "Sorry, you don't have the approved role for this command."
        await ctx.send(embed = Embed(title=msg, color=0xff0000))

@discord_client.command()
async def donation(ctx):
    """
    Find the donation status of your account
    """
    # First find the user in the databse
    flag = False
    user_tupe = ()
    arg = ctx.message.content.split(" ")[1:]
    if len(arg) == 0:
        rows = DB.get_allUsers()
        for row in rows:
            if int(row[4]) == int(ctx.author.id):
                user_tupe = row
                flag = True

    elif len(arg) == 1:
        if arg[0].startswith("#"):
            pass
        else:
            arg[0] = "#"+arg[0]
        rows = DB.get_allUsers()
        for row in rows:
            if str(row[0]) == str(arg[0]):
                user_tupe = row
                flag = True

    if flag == False:
        msg = (f"Could not find the user {arg[0]} in the database. Please make sure "
        "that they exists in the clan by using the /lcm command, then add them using /useradd.")
        await ctx.send(embed = Embed(title=f"**DB ERROR**", description=msg, color=0xff0000))

    # if user exists proceed to calculate their donation
    if flag:
        # update the db first
        user_tag = user_tupe[0]
        res = coc_client.get_member(user_tag)
        mem_stat = CoC_Stats(res.json())
        in_zulu = "False"
        if mem_stat.currentClan_name == "Reddit Zulu":
            in_zulu = "True"
        else:
            in_zulu = "False"
        send = DB.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    mem_stat.coc_tag,
                    mem_stat.total_Donations,
                    in_zulu,
                    mem_stat.trophies
                ))
        if send != None:
            msg = f"Operational Error while inserting data."
            await ctx.send(embed = Embed(title=f"**SQL ERROR**\n{send}", description=msg, color=0xff0000))
            return

        rows = DB.get_allDonations(user_tupe[0], lastSunday())
        if len(rows) > 2:
            cur_donation = rows[-1][2] - rows[0][2]
            await ctx.send(f"{cur_donation}/300")
        else:
            await ctx.send(f"Not enough data to calcualte your progress. "
            f"current FIN #: {rows[-1][2]}")


@discord_client.event
async def on_ready():
    print("Bot connected.")
    game = Game("if __main__ == __name__:")
    await discord_client.change_presence(status=discord.Status.online, activity=game)  

discord_client.loop.create_task(weeklyRefresh())
discord_client.run(config['Bot']['Bot_Token'])