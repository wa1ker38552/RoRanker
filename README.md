
<img align="left" width="80" height="80" src="https://user-images.githubusercontent.com/100868154/170111822-218e8d8b-c437-4cf2-bb95-cc846e66a25d.png" alt="RoRanker">
<h1>RoRanker<h1>

<a href="https://github.com/Rapptz/discord.py/">
  <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
</a>
<a href="https://www.python.org/downloads/">
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/Red-Discordbot">
</a>

# Overview

RoRanker is a multi-purpose Discord bot that can be used to connect Roblox groups as well as verify Roblox users. RoRanker has many features such as Discord roles ranked according to the connected Roblox group and a comprehensive, easy to use, verification system.
  
**Verification**
  
Verification through RoRanker is made easy, simply using `#verify username` will return a code which you will then paste onto your profile. Using `#verify` username again after pasting the code will succesfully verify you. If you happen to have to code tagged out, you can regenerate another verification code using `#regenerateauthcode`. If for some reason, you want to disconnect your verified account, simply use, `#removeverfication` to remove your verified user.
  
Upon being verified, you will receive the "Verified" role which will optimally allow the users to view the different channels. Other users will also be able to see which Roblox account a verified user is connected to use `#viewprofile user#0000`.
  
**Group Connections**
  
Connecting your Roblox group to the Discord server is done by using the command, `#connectgroup groupID`. After connecting the group, RoRanker will automatically add all of the groups ranks as roles and will update user roles whenever the `#updateroles` command is used. To disconnct a group, simply use `#disconnectgroup` and RoRanker will succesfully disconnct the currently connected group. To check what group the server is connected to, use `#connectedgroup` to show all group information.

**Usage**
  
You can set custom prefixes for your user using `#prefix customprefix`. Any custom prefixes will be saved onto your account and using commands with the old prefix will not work. To view your current prefix, use "roranker prefix" to check.
