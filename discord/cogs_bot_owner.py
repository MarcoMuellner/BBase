from discord.ext.commands import Bot,command,Context,Cog
from discord import DMChannel,Member,File,Guild,TextChannel,Message
from discord.errors import Forbidden
from typing import Union
from django.utils import timezone
import os
from BBase.discord.cog_interface import ICog,AuthorState
import datetime
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.axes import Axes
from texttable import Texttable
from aiohttp import web
from aiohttp.web import Request
import logging
from json.decoder import JSONDecodeError

from BBase.helper import send_table
from BBase.base_db.models import BaseUser,BaseGuild,Error,UserIgnore

logger = logging.getLogger(__name__)
path = os.path.dirname(os.path.realpath(__file__)) + "/../../"

class BotOwner(ICog):
    def __init__(self, bot : Bot,d : dict):
        super().__init__(bot, AuthorState.BotOwner)
        if 'bot_owner_id' in d.keys():
            self.bot_owner_id = d['bot_owner_id']
        else:
            self.bot_owner_id = None

        if 'bot_owner_server' in d.keys():
            self.bot_owner_server = d['bot_owner_server']
        else:
            self.bot_owner_server = None

        if 'bot_owner_info_channel' in d.keys():
            self.bot_owner_info_channel = d['bot_owner_info_channel']
        else:
            self.bot_owner_info_channel = None

        if 'bot_owner_messages_channel' in d.keys():
            self.bot_owner_dm_channel = d['bot_owner_messages_channel']
        else:
            self.bot_owner_dm_channel = None

    @command(
        name='show_guilds',
        help='Shows the guilds used by QOTD-Bot.'
    )
    async def show_guilds(self,ctx : Context):
        text = f"{ctx.bot.user.name} is on the following guilds:\n\n"
        for i in ctx.bot.guilds:
            text += f'__**{i.name}**__ ({i.id})\n'
            text += f"_Total members_: {i.member_count}\n"
            text += f"_Guild description_: {i.description}\n"
            text += f"_Created at_: {i.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"_Guild owner_: {i.owner.name}({i.owner.id})\n"
        await send_table(ctx.send,text,False)

    @command(
        name='bot_info',
        help='Shows some information about the bot.'
    )
    async def b_info(self,ctx : Context):
        text = f"{ctx.bot.user.name} Bot information: \n\n"
        text += f"__Total amount of saved users__: {len(BaseUser.objects.all())}\n"
        text += f"__Active on servers__: {len(ctx.bot.guilds)}\n"

        times = [g.time_stamp.date() for g in BaseGuild.objects.all() if g.id in [i.id for i in ctx.bot.guilds]]
        time_stamps,count_per_day = np.unique(times,return_counts=True)
        total_counts = np.cumsum(count_per_day)
        fig = pl.figure()
        ax : Axes = fig.add_subplot(111)
        ax.plot(time_stamps,count_per_day,color='green',linestyle='--', marker='o',label='growth')
        ax.set_xticks(time_stamps)
        ax.set_ylim(0, max(count_per_day) + 1)
        ax.set_ylabel('Guild growth')
        p_growth = f"{path}plots/guild_stat_plot_growth.png"
        pl.tight_layout()
        pl.savefig(p_growth)

        fig = pl.figure()
        ax_total : Axes = fig.add_subplot(111)
        ax_total.plot(time_stamps, total_counts, color='k', linestyle=':', marker='o',label='Total')
        ax_total.set_xticks(time_stamps)
        ax_total.set_ylabel('Total number of guilds')
        ax_total.set_ylim(0,max(total_counts)+1)
        pl.tight_layout()
        p_total = f"{path}plots/guild_stat_plot_total.png"
        pl.savefig(p_total)

        await ctx.send(text,file=File(p_growth))
        await ctx.send(file=File(p_total))
        os.remove(p_growth)
        os.remove(p_total)


    @command(
        name='show_errors',
        help='Shows all errors that occured in a given timeframe'
    )
    async def show_errors(self,ctx : Context, nr_of_days : int):
        table = Texttable()
        tabledata = [["Time","Guild", "CMD string", "Error Type", "Error"]]
        er = Error.objects.filter(time_stamp__gt=(timezone.now() + datetime.timedelta(-nr_of_days))).order_by('time_stamp')
        for i in er:
            i : Error
            in_guild = None
            for j in ctx.bot.guilds:
                if j.id == i.g.id:
                    in_guild = j.name
            tabledata.append([f'{i.time_stamp.strftime("%Y-%m-%d %H:%M")}',in_guild,i.cmd_string,i.error_type,i.error])
        table.set_deco(Texttable.VLINES | Texttable.HEADER | Texttable.BORDER)
        table.add_rows(tabledata, True)
        table.set_cols_width([16, 10, 20, 15,40])
        txt = "```" + table.draw() + "```"
        await send_table(ctx.send,txt)

    @command(
        name='broadcast_update',
        help='Broadcasts a message to all servers'
    )
    async def broadcast_update(self, ctx: Context, text : str):
        g_list = [g for g in ctx.bot.guilds if g.id in [j.id for j in BaseGuild.objects.all()]]
        s_text = ":up: Update message from QOTDBot::up: \n\n " + text + "\n\n **To disable these messages, use " \
                                                                         "the __show_updates__ command. But " \
                                                                         "i won't bother you often, i promise.**"
        for g in g_list:
            g : Guild
            g_db = BaseGuild.objects.get(id=g.id)
            if g_db.show_updates and g_db.log_channel is not None:
                try:
                    channel : TextChannel= [i for i in g.channels if i.id == g_db.log_channel][0]
                except KeyError:
                    continue
                await channel.send(s_text)

    @command(
        name='ignore_user',
        help='Ignores the user messages from this user'
    )
    async def ignore_user(self,ctx : Context,u_id : int):
        if len(UserIgnore.objects.filter(user_id=u_id)) > 0:
            await ctx.send(f"{u_id} is already ignored!")
        else:
            UserIgnore(user_id=u_id).save()
            await ctx.send(f"Messages from {u_id} will be ignored.")

    async def send_error_notification(self,e : Error,guild : Guild):
        text = f":exclamation: An error occured on {guild.name} ({guild.id}): @here:exclamation: \n\n" \
            f"_cmd string_: {e.cmd_string}\n" \
            f"_error type_: {e.error_type}\n" \
            f"_error_: {e.error}\n" \
            f"_time stamp_: {e.time_stamp}\n" \
            f"_traceback_: {e.traceback}\n"

        await self.send_update(text,self.bot_owner_info_channel,guild,True)

    @Cog.listener()
    async def on_guild_join(self,guild : Guild):
        text = f"**:white_check_mark: Guild {guild.name}({guild.id}) added QODTBot! :smile:**\n"
        text += f"**Total members**: {guild.member_count}\n"
        text += f"**Guild description**: {guild.description}\n"
        text += f"**Created at**: {guild.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        text += f"**Guild owner**: {guild.owner.name}({guild.owner.id})\n"

        await self.send_update(text, self.bot_owner_info_channel,guild)

    @Cog.listener()
    async def on_guild_remove(self,guild : Guild):
        text = f"**:interrobang:  Guild {guild.name}({guild.id}) removed QOTDBot !:confused:**\n"
        text += f"**Total members**: {guild.member_count}\n"
        text += f"**Guild description**: {guild.description}\n"
        text += f"**Created at**: {guild.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        text += f"**Guild owner**: {guild.owner.name}({guild.owner.id})\n"

        await self.send_update(text, self.bot_owner_info_channel,guild)

    @Cog.listener()
    async def on_message(self,message : Message):
        if message.author.id == self.bot.user.id:
            return

        if len(UserIgnore.objects.filter(user_id=message.author.id)) > 0:
            return

        if isinstance(message.author,Member):
            return
        else:
            text = f"**:e_mail:@here User {message.author.name} ({message.author.id}) has sent you a message:e_mail:\n\n **"
            text += f"Time: {message.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"Content: _{message.content}_"

        if 'server_invite' in message.content:
            text_invite = "Hi there. If you need any help setting up QOTD-Bot you can join our Support server for further " \
                   "help:\n https://discord.gg/WQFyXzb"
            await message.channel.send(text_invite)

        await self.send_update(text, self.bot_owner_dm_channel,None)

    async def send_update(self,text : str,channel : int, guild : Union[Guild,None],always_send = False):
        try:
            if self.bot_owner_server is None or channel is None:
                raise KeyError()

            if guild is not None and guild.id == self.bot_owner_server and not always_send:
                return

            owner_guild: Guild = [i for i in self.bot.guilds if i.id == self.bot_owner_server][0]
            owner_channel: TextChannel = [i for i in owner_guild.channels if i.id == channel][0]
            await send_table(owner_channel.send, text, False)
        except (KeyError,Forbidden) as e:
            if self.bot_owner_id is not None:
                for bot_owner in self.bot_owner_id:
                    u: Member = self.bot.get_user(bot_owner)
                    if u is not None:
                        dm_channel: DMChannel = await u.create_dm()
                        try:
                            await send_table(dm_channel.send,text,False)
                        except Forbidden:
                            pass

    @Cog.listener()
    async def on_ready(self):
        app = web.Application()
        app.add_routes([web.post('/', self.handle)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        try:
            await site.start()
        except OSError:
            pass

    async def handle_upvote(self,data):
        if 'bot' not in data.keys() or 'user' not in data.keys() or 'type' not in data.keys():
            return

        text = f"**User {data['user']}** performed {data['type']} for bot {data['bot']}"

        guild = None
        for g in self.bot.guilds:
            if g.id==self.bot_owner_server:
                guild = g
        await self.send_update(text,self.bot_owner_info_channel,guild,True)

    async def handle(self,request: Request):
        try:
            data = await request.json()
        except JSONDecodeError:
            return web.Response(text='OK')
        auth = request.headers.get('Authorization')

        if auth != self.webhook_auth:
            logger.error(f"Auth error from {request.url}: url auth : {auth}, self: {self.webhook_auth}")
            return web.Response(text='AuthError')

        logger.info(f"Received http request with data: {data}")
        await self.handle_upvote(data)

        return web.Response(text='OK')



