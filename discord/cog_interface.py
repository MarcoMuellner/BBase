from discord.ext.commands import Cog, Bot, Context
from discord import Member,Guild,User
from discord.ext.commands.errors import *
from discord.errors import Forbidden

from BBase.helper import  add_guild,get_user
from BBase.base_db.models import BaseGuild,BaseUser,Error
import traceback

class AuthorState:
    User = 1
    Mod = 2
    Owner = 3
    BotOwner = 4

class ICog(Cog):
    def __init__(self, bot: Bot,min_perm :int):
        self.bot = bot
        self.min_perm = min_perm

    async def cog_check(self, ctx):
        perm = await self.a_perm(ctx)
        return perm >= self.min_perm

    async def notify_error_bot_owner(self, e : Error,ctx : Context):
        bot_owner = self.bot.get_cog('BotOwner')
        await bot_owner.send_error_notification(e,ctx.guild)

    async def cog_command_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CheckFailure):
            if isinstance(error,BotMissingPermissions):
                text = "To use this command, the bot needs the following permissions:\n"
                for i in error.missing_perms:
                    text += f"**- {i}**\n"
                text += "Please make sure that these are available to QOTDBot."
                await ctx.send(text)

                guild = ctx.guild
                me = guild.me if guild is not None else ctx.bot.user
                permissions = ctx.channel.permissions_for(me)

                e = Error(g=self.g, cmd_string=ctx.message.system_content
                          , error_type=f'{type(error.original)}', error=f'{error}', traceback=f"Has : "
                    f"{permissions}\n\nNeeds: {error.missing_perms}")
                e.save()
                await self.notify_error_bot_owner(e, ctx)
            else:
                await ctx.send('** Error **: You are not allowed to use this command!')
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(f"** Error **: Command _**{ctx.command.qualified_name}**_ misses some arguments."
                           f" See the help:")
            await ctx.send_help(ctx.command)

        elif isinstance(error, ConversionError):
            await ctx.send(f'** Error **: Cannot convert arguments for _**{ctx.command.qualified_name}**_. '
                           'Please make sure, you use the correct types. See the help:')
            await ctx.send_help(ctx.command)

        elif isinstance(error, BadArgument):
            await ctx.send(f'** Error **: Bad Argument for _**{ctx.command.qualified_name}**_! Please '
                           f'check help.')
            await ctx.send_help(ctx.command)

        elif isinstance(error.original,Forbidden):
            text = f'** Error **: Permissions missing for the Bot. The bot needs at least\n'\
                   f'__Manage Roles__\n'\
                   f'__Manage Channels__\n'\
                   f'__Send Messages__\n'\
                   f'__Manage Messages__\n'\
                   f'__Read message history__\n'\
                   f'__Add reactions__\n'\
                   f'Total integer value: 268511344\n'\
                   f'Please make sure that these permissions are given to the bot.'
            try:
                await ctx.send(text)
            except Forbidden:
                u :User= self.bot.get_user(ctx.author.id)
                dm_channel = u.create_dm()
                try:
                    await dm_channel.send(text)
                except Forbidden:
                    pass

                e = Error(g=self.g, cmd_string=ctx.message.system_content
                          , error_type=f'{type(error.original)}', error=f'{error}', traceback=traceback.format_exc())
                e.save()
                await self.notify_error_bot_owner(e, ctx)
        else:
            e = Error(g=self.g, cmd_string=ctx.message.system_content
                      , error_type=f'{type(error.original)}', error=f'{error}',traceback=traceback.format_exc())
            e.save()
            await self.notify_error_bot_owner(e, ctx)
            await ctx.send(f'Sorry an error occured. My creator has been notified.')

    async def cog_before_invoke(self, ctx : Context):
        add_guild(ctx)
        self.g = BaseGuild.objects.get(id=ctx.guild.id)
        self.m : Member = ctx.guild.get_member(ctx.author.id)
        self.u : BaseUser = get_user(self.m, self.g)
        try:
            self.u_perm_state = await self.a_perm_intern(self.u,self.m)
        except AttributeError:
            self.m = None
            self.u_perm_state = AuthorState.User

    async def a_perm(self,ctx : Context):
        add_guild(ctx)
        g = BaseGuild.objects.get(id=ctx.guild.id)
        u = get_user(ctx.author,g)
        member = ctx.author
        return await self.a_perm_intern(u,member)

    async def a_perm_intern(self, u : BaseUser, member : Member):
        if await self.is_bot_owner(member):
            return AuthorState.BotOwner
        elif await  self.is_admin(member):
            return AuthorState.Owner
        elif await self.is_mod(u,member):
            return AuthorState.Mod
        else:
            return AuthorState.User

    async def is_admin(self,member : Member):
        return member.guild_permissions.administrator or member.guild_permissions.manage_roles

    async def is_bot_owner(self,member : Member):
        bot_owner = self.bot.get_cog('BotOwner')
        return member.id == bot_owner.bot_owner_id

    async def is_mod(self, u : BaseUser, member : Member):
        if u is not None:
            mod_role = u.g.m_role()
            mod_flag = u.g_mod
            if mod_role is not None:
                role_ids = [i.id for i in member.roles]
                mod_role = len([i for i in mod_role if i in role_ids]) > 0
            else:
                mod_role = False

            mod = mod_flag or mod_role
        else:
            mod = False

        return mod or member.guild_permissions.ban_members

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        add_guild(guild)

