from discord.utils import get
from alive import keepAlive
from replit import db
import requests
import discord
import random
import os

client = discord.Client()
alpha = list('abcdefghijklmnopqrstuvwxyz1234567890')


# RESETS THE DATABASE
# db['verified'] = {}
# db['verify_codes'] = {}
# db['connectedgroup'] = {}
# db['prefix'] = {}

def indexsegment(text, start, index):
  start = text.index(start)+len(start)
  x = start
  while text[x] != index: x += 1
  return text[start:x]

def query_users(username, key):
  r = requests.get(f'https://www.roblox.com/search/users/results?keyword={username}&maxRows=12&startIndex=0')
  results = r.json()['UserSearchResults']
  return results[0][key]

def get_information(id: str):
  results = {}
  request = requests.get(f'https://users.roblox.com/v1/users/{id}').json()
  results['description'] = request['description']
  results['displayname'] = request['displayName']
  results['created'] = request['created'].split('T')[0]
  results['thumbnail'] = requests.get(f'https://thumbnails.roblox.com/v1/users/avatar?userIds={id}&size=100x100&format=Png&isCircular=false').json()['data'][0]['imageUrl']
  results['friends'] = requests.get(f'https://friends.roblox.com/v1/users/{id}/friends/count').json()['count']
  results['following'] = requests.get(f'https://friends.roblox.com/v1/users/{id}/followings/count').json()['count']
  results['followers'] = requests.get(f'https://friends.roblox.com/v1/users/{id}/followers/count').json()['count']

  collections = []
  request = requests.get(f'https://www.roblox.com/users/profile/robloxcollections-json?userId={id}').json()['CollectionsItems']
  for item in request: collections.append(item['Name'])
  results['collections'] = collections
    
  return results

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="#help"))
  print(client.user)

@client.event
async def on_message(message):
  if client.user != message.author:
    auth = str(message.author)
    cont = str(message.content)
    if auth in db['prefix']:
      prefix = db['prefix'][auth]
    else:
      prefix = '#'
      db['prefix'][auth] = '#'
    if cont == 'roranker prefix':
      await message.channel.send(f"Your prefix is: {db['prefix'][auth]}")
    if cont.split()[0] == f'{prefix}verify':
      try:
        user = cont.split()[1]

        if auth in db['verify_codes']: 
          if auth in db['verified']:
            embed = discord.Embed(title=f'User {auth} is already connected to Roblox user {db["verified"][auth]}!', color=0xfe7171)
            await message.channel.send(embed=embed)
          else:
            request = requests.get(f'https://www.roblox.com/users/{query_users(user, "UserId")}/profile')
            
            if db['verify_codes'][auth] in request.text:
              embed = discord.Embed(title=f'User {auth} succesfully verified!', color=0xfe7171)
              db['verified'][auth] = user
              role = get(message.author.guild.roles, name='Verified')
              await message.author.add_roles(role)
            else:
              embed = discord.Embed(title=f'Failed to verify user {auth}.', color=0xfe7171)
            await message.channel.send(embed=embed)
          
        else:
          verify_id = ''.join([random.choice(alpha) for i in range(10)])
          db['verify_codes'][auth] = verify_id
          embed = discord.Embed(title=f'Add this code to your profile to be verified:  `{verify_id}`', color=0xfe7171)
          await message.channel.send(embed=embed)
          
      except IndexError:
        embed = discord.Embed(title=f'Missing parameters (username)!', color=0xfe7171)
        await message.channel.send(embed=embed)
  
    if cont.split()[0] == f'{prefix}verified':
      if auth in db['verified']:
        embed = discord.Embed(title=f'User {auth} is connected to Roblox user {db["verified"][auth]}', color=0xfe7171)
      else:
        embed = discord.Embed(title=f'No Roblox account verified under {auth}', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}removeverification':
      try:
        request = requests.get(f'https://groups.roblox.com/v1/groups/{db["connectedgroup"][str(message.guild.name)]}/roles').json()
        unparsed_roles, roles = request['roles'], []
        for role in unparsed_roles: roles.append(role['name'])
        roles.pop(0)

        for role in roles:
          await message.author.remove_roles(get(message.author.guild.roles, name=role))
        
        del db['verify_codes'][auth]
        del db['verified'][auth]
        role = get(message.author.guild.roles, name='Verified')
        await message.author.remove_roles(role)
        embed = discord.Embed(title=f'Sucesfully disconnected Roblox verification from {auth}', color=0xfe7171)
      except KeyError:
        embed = discord.Embed(title=f'No Roblox account verified under {auth}', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}regenerateauthcode':
      verify_id = ''.join([random.choice(alpha) for i in range(10)])
      db['verify_codes'][auth] = verify_id
      embed = discord.Embed(title=f'Verification code regenerated to `{verify_id}`.', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}connectgroup':
      try:
        r = requests.get(f'https://groups.roblox.com/v2/groups?groupIds={cont.split()[1]}')
        if not r.json()['data'] == []:
          db['connectedgroup'][str(message.guild.name)] = cont.split()[1]
          request = requests.get(f'https://groups.roblox.com/v1/groups/{cont.split()[1]}/roles').json()
          unparsed_roles, roles = request['roles'], []
          for role in unparsed_roles: roles.append(role['name'])
          roles.pop(0)
          for role in roles:
            role = await message.guild.create_role(name=role, color=0xfe7171)
          
          embed = discord.Embed(title=f'Sucesfully connected {r.json()["data"][0]["name"]} to Discord server! Roles were updated!', color=0xfe7171)
        else:
          embed = discord.Embed(title=f'Could not connect group with id: {cont.split()[1]}', color=0xfe7171)
      except IndexError:
        embed = discord.Embed(title=f'Missing parameters (group ID)!', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}connectedgroup':
      try:
        r = requests.get(f'https://groups.roblox.com/v2/groups?groupIds={db["connectedgroup"][str(message.guild.name)]}').json()['data'][0]
        request = requests.get(f'https://users.roblox.com/v1/users/{r["owner"]["id"]}').json()
        embed = discord.Embed(title=f'{r["name"]}',
                              description=f'''
                              **Owner:** {request["name"]}
                              
                              {r["description"]}
                              ''',
                              color=0xfe7171)
        embed.set_thumbnail(url=indexsegment(requests.get(f'https://www.roblox.com/groups/{db["connectedgroup"][str(message.guild.name)]}').text, '<meta property="og:image" content="', '"'))
      except IndexError:
        embed = discord.Embed(title=f'Discord server is not connected to a group.', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}disconnectgroup':
      if str(message.guild.name) in db['connectedgroup']:
        request = requests.get(f'https://groups.roblox.com/v1/groups/{db["connectedgroup"][str(message.guild.name)]}/roles').json()
        unparsed_roles, roles = request['roles'], []
        for role in unparsed_roles: roles.append(role['name'])
        roles.pop(0)
        for role in roles:
          r = get(message.guild.roles, name=role)
          await r.delete()
          
        del db['connectedgroup'][str(message.guild.name)]
        embed = discord.Embed(title=f'Removed connected group from Discord server.', color=0xfe7171)
      else:
        embed = discord.Embed(title=f'Discord server is not connected to a group.', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}updateroles':
      if auth in db['verified']:
        if str(message.guild.name) in db["connectedgroup"]:
          groupname = requests.get(f'https://groups.roblox.com/v2/groups?groupIds={db["connectedgroup"][str(message.guild.name)]}').json()['data'][0]['name']
          id = query_users(db['verified'][auth], "UserId")
          request = requests.get(f'https://groups.roblox.com/v2/users/{id}/groups/roles')
          for group in request.json()['data']:
            if group['group']['name'] == groupname:
              role = get(message.author.guild.roles, name=group['role']['name'])
              await message.author.add_roles(role)
              embed = discord.Embed(title=f'Succesfully added role {group["role"]["name"]}!', color=0xfe7171)
        else:
          embed = discord.Embed(title=f'Discord server is not connected to a group!', color=0xfe7171)
      else:
        embed = discord.Embed(title=f'User {auth} is not verified! Use `#verify` to get verified!', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}roles':
      if str(message.guild.name) in db['connectedgroup']:
        request = requests.get(f'https://groups.roblox.com/v1/groups/{db["connectedgroup"][str(message.guild.name)]}/roles').json()
        unparsed_roles, roles = request['roles'], []
        for role in unparsed_roles: roles.append(role['name'])
        roles.pop(0)

        groupname = requests.get(f'https://groups.roblox.com/v2/groups?groupIds={db["connectedgroup"][str(message.guild.name)]}').json()['data'][0]['name']
        embed = discord.Embed(title=f'Roles for {groupname}:', 
                              description='\n'.join(roles),
                              color=0xfe7171)
      else:
        embed = discord.Embed(title=f'Discord server is not connected to a group!', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}viewprofile':
      try:
        user = cont.split()[1]
        if user in db['verified']:
          results = get_information(query_users(db['verified'][user], 'UserId'))
          embed = discord.Embed(title=f'{results["displayname"]} ({user})', 
                                description=f'''
                                {results["description"]}

                                **Join Date:** {results["created"]}
                                **Collections:** {", ".join(results["collections"])}
                                ''',
                                color=0xfe7171)
          embed.add_field(name='Friends', value=results['friends'], inline=True)
          embed.add_field(name='Following', value=results['following'], inline=True)
          embed.add_field(name='Followers', value=results['followers'], inline=True)
          embed.set_thumbnail(url=results["thumbnail"])
                                
        else:
          embed = discord.Embed(title=f'User {user} is not verified!')    
      except IndexError:
        embed = discord.Embed(title=f'Missing parameters (Discord user)!', color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}changeprefix':
      try:
        db['prefix'][auth] = cont.split()[1]
        embed = discord.Embed(title=f'Succesfully changed prefix to `{cont.split()[1]}`!', color=0xfe7171)
      except IndexError:
        embed = discord.Embed(title=f'Missing parameters (prefix)!', color=0xfe7171)
      await message.channel.send(embed=embed)
    
    if cont.split()[0] == f'{prefix}help':
      embed = discord.Embed(title='RoRanker Help',
                            description=f'''
                            RoRanker is a bot used to verify Discord users to Roblox as well as connect group rankings to Discord roles. To verify, type in `#verify username` and then use the same command again after pasting the code onto your profile page.

                            Update your Discord roles from the Roblox group using #updateroles.
                            
                            Commands:

                            Verification

                            `{prefix}verify (username)`: 
                            - Generates a verification code for you to add to your Roblox profile.
                            `{prefix}verified`: 
                            - Shows which Roblox account, if there is one, is verified to your Discord user.
                            `{prefix}removeverification`: 
                            - Removes all vertification from your Discord account (You will lose your roles!).
                            `{prefix}regenerateauthcode`: 
                            - Regenerates verification code in case Roblox tags it out.
                            `{prefix}connectedgroup`:
                            - Shows what group the Discord server is connected to.

                            Roles
                            
                            `{prefix}updateroles`:
                            - Updates your Discord roles from your Roblox roles.
                            `{prefix}roles`:
                            - Shows roles avaliable in Roblox group/Discord server.

                            Miscellaneous

                            `{prefix}viewprofile (Discord user)`:
                            Shows Roblox profile of the specified Discord user.
                            `{prefix}changeprefix (prefix)`:
                            Changes prefix to specified prefix only for your Discord user.

                            Admin Only:
                            `{prefix}connectgroup (ground ID)`:
                            - Connects a Roblox group to the Discord server. Roles will be created.
                            `{prefix}disconnectgroup`:
                            - Disconnects the connected Roblox group. Roles will be deleted.
                            ''',
                            color=0xfe7171)
      await message.channel.send(embed=embed)

    if cont.split()[0] == f'{prefix}cleardatabase':
      if auth == 'VERIFIED DATABASE CLEAR, PUT IN YOUR OWN USER TO CLEAR FROM DISCORD':
        await message.channel.send(f'```{db["verify_codes"]}\n{db["verified"]}```')
        db['verify_codes'] = {}
        db['verified'] = {}
        await message.channel.send('Database cleared!')
      else:
        await message.channel.send('Invalid permissions.')
    
keepAlive()
client.run(os.environ['TOKEN'])
