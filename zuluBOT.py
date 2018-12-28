from discord.ext import commands
import discord
from discord import Embed, Game, Guild
from CoC_API import CoC
from CoC_Stats import CoC_Stats
from ZuluBot_DB import ZuluDB
from collections import OrderedDict
from configparser import ConfigParser
from requests import get
from datetime import datetime

#Permissions
# create_instant_invite

config = ConfigParser()
config.read('zuluConfig.ini')
discord_client = commands.Bot(command_prefix = config['Bot']['Bot_Prefix'])
discord_client.remove_command("help")
coc_client = CoC(config['Clash']['ZuluClash_Token'])
DB = ZuluDB()

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

def invite():
    obj = discord_client.get_guild(int(config['Discord']['PlanDisc_ID']))
    channel = obj.get_channel(int(config['Discord']['PlanDisc_Channel']))
    return channel

@discord_client.command()
async def test(ctx):
    pass
    

@discord_client.command()
async def kill(ctx):
    await ctx.send(embed = Embed(title="Later..", color=0x00FF00))
    await discord_client.logout()
    
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
    guild_obj = discord_client.get_guild(int(config['Bot']['ZuluDisc_ID']))
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


@discord_client.command(pass_context=True)
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
                member_stat = CoC_Stats(res.json())
                roleObj_CM = discord_client.get_guild(int(config['Discord']['ZuluDisc_ID'])).get_role(int(config['Discord Roles']['CoC_Members']))
                roleObj_TH, roleStr_TH = get_THRole(member_stat.th_lvl)
                #
                # Print out the warning
                #
                msg = "Standby, giving {} default roles, and changing their nickname on discord to reflect their in game name.".format(member_stat.coc_name)
                await ctx.send(embed = Embed(title=msg, color=0x5c0189))
                #
                # Adding CoC Members role
                #
                flag = True
                for role in disc_UserObj.roles:
                    if role.name == "CoC Members":
                        flag = False
                        await ctx.send(embed = Embed(title=f"{member_stat.coc_name} already has 'CoC Members' role assigned.", color=0xFFFF00))
                
                if flag:
                    await disc_UserObj.add_roles(roleObj_CM) # Give user CoC Members role
                    await ctx.send(embed = Embed(title=f"Successfully assigned {member_stat.coc_name} 'CoC Members' role.", color=0x00ff00))
                #
                # Adding TH# Members role
                #
                flag = True
                for role in disc_UserObj.roles:
                    if role.name.startswith('th'):
                        flag = False
                        if role.name == roleObj_TH.name:
                            msg = f"{member_stat.coc_name} already has {roleObj_TH.name} role assigned."
                            await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                        else:
                            await disc_UserObj.remove_roles(role)      # remove old th role
                            await disc_UserObj.add_roles(roleObj_TH)   # Give user TH# ROLE
                            msg = (f"Succesfully removed {role.name} and assigned {roleObj_TH}")
                            await ctx.send(embed = Embed(title=msg, color=0x00ff00))
                if flag:
                    await disc_UserObj.add_roles(roleObj_TH) # Give user TH# ROLE
                    msg = f"Successfully assigned {member_stat.coc_name} {roleStr_TH} role."
                    await ctx.send(embed = Embed(title=msg, color=0x00ff00))

                
                #
                # Chaning users nickname
                #
                if disc_UserObj.display_name != member_stat.coc_name:
                    old_name = disc_UserObj.display_name
                    await disc_UserObj.edit(nick=member_stat.coc_name)
                    msg = f"Changed {member_stat.coc_name}'s nickname from [{old_name}] to [{member_stat.coc_name}]."
                    await ctx.send(embed = Embed(title=msg, color=0x00ff00))
                else:
                    msg = f"{member_stat.coc_name} nickname already reflects their CoC name."
                    await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                #
                # Add user to database
                #
                #
                msg = f"Initiating database with {member_stat.coc_name}'s data."
                await ctx.send(embed = Embed(title=msg, color=0xFFFF00))
                DB.insert_userdata((
                    member_stat.coc_tag,
                    member_stat.coc_name,
                    member_stat.th_lvl,
                    member_stat.league,
                    member_stat.league_icon,
                    disc_UserObj.id,
                    datetime.utcnow(),
                    "False",
                    "True",
                    None
                ))
                # DB.update_donations((
                #     datetime.utcnow(),
                #     member_stat.coc_tag,
                #     member_stat.total_Donations,
                #     "True"
                # ))
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

@discord_client.event
async def on_ready():
    print("Bot connected.")
    game = Game("if __main__ == __name__:")
    await discord_client.change_presence(status=discord.Status.online, activity=game)  

discord_client.run(config['Bot']['Bot_Token'])