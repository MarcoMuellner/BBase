import dbl
import requests
from discord.ext import commands

import asyncio
import logging
from copy import deepcopy


class DiscordBotsOrgAPI(commands.Cog):
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot,d):
        self.bot = bot

        if 'dev' in d and d['dev']:
            return

        self.task_list = []
        if "bot_list_tokens" in d.keys():
            for key,value in d["bot_list_tokens"].items():
                if key == "discordbots":
                    self.discord_bots_token = d["bot_list_tokens"]["discordbots"]
                    self.dblpy = dbl.Client(self.bot, self.discord_bots_token)
                    self.updating = self.bot.loop.create_task(self.update_discord_bots())
                else:
                    if 'headers' in value.keys() and 'payload' in value.keys():
                        self.task_list.append(
                            self.bot.loop.create_task(self.update_bot_count(value['url']
                                                                            ,value['headers']
                                                                            ,value['payload'])))


    async def update_discord_bots(self):
        """This function runs every 30 minutes to automatically update your server count"""
        if self.discord_bots_token is None:
            return
        while not self.bot.is_closed():
            logger.info('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
            except Exception as e:
                logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

    async def update_bot_count(self,url,headers,payload):
        while not self.bot.is_closed():
            guild_count = len(self.bot.guilds)
            payload[list(payload.keys())[0]] = guild_count
            r = requests.post(url,data=payload,headers=headers)
            await asyncio.sleep(1800)


def discordbot_update(bot,d):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(DiscordBotsOrgAPI(bot,d))