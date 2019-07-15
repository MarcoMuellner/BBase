from discord.ext.commands import command,Context, Bot
from discord import Role,Member
import re
from typing import Union
import os

from BBase.discord.cog_interface import ICog,AuthorState
from BBase.base_db.models import BaseUser
path = os.path.dirname(os.path.realpath(__file__)) + "/../../"

class BaseOwner(ICog):
    def __init__(self,bot : Bot):
        super().__init__(bot,AuthorState.Owner)

    def get_user(self,ctx : Context,u_id: Union[int, str]):

        m = None
        u_id = int(re.findall(r"\d+", u_id)[0]) if isinstance(u_id, str) else u_id

        for i in ctx.guild.members:
            if i.id == u_id:
                m = i
                break

        try:
            u = BaseUser.objects.get(d_id=u_id, g=self.g)
        except BaseUser.DoesNotExist:
            u = BaseUser(d_id=u_id,g=self.g,d_name=m.display_name if m is not None else "")
            u.save()

        return u,m

    @command(
        name='set_prefix',
        help="Sets the prefix for the bot"
    )
    async def set_prefix(self, ctx: Context, prefix: str):
        self.g.prefix = prefix
        self.g.save()
        await ctx.send(f"**Prefix has ben set to _{self.g.prefix}_**")

    @command(
        name='add_mod',
        brief='Gives a user moderation privileges.',
        help='Gives a user moderation privileges. A flag is turned on for this user. He has then access to the Mod '
             'group of commands as seen in the help command.'
    )
    async def add_mod(self, ctx: Context, user_id: Union[int, Member]):
        if isinstance(user_id,Member):
            user_id = user_id.id

        u, m = self.get_user(ctx, user_id)
        u.g_mod = False
        u.save()
        await ctx.send(f":white_check_mark:**User {m.mention if m is not None else u.d_name}({u.d_id}) "
                       f"is now a mod!**")

    @command(
        name='add_mod_role',
        brief='Gives users with this role moderation privileges.',
        help='Gives users with this role moderation privileges. All users that have this role will then be able to '
             'access the Mod group of commands as seen in the help command. If a role is already set, this '
             'method will not remove the old role, but rather both will then have moderation privileges.'
    )
    async def add_mod_role(self,ctx: Context, role_id: Union[int, Role]):
        if isinstance(role_id, int):
            role = ctx.guild.get_role(role_id)
        else:
            role = role_id

        if role is None:
            await ctx.send(f"Sorry, {role_id} is not available as a role on the guild.")
            return

        self.g.add_role(role_id)
        self.g.save()
        await ctx.send(f":white_check_mark:**Users with {role.mention}({role.id}) role are now mods**")

    @command(
        name='rm_mod_role',
        brief='Resets moderation role.',
        help='Removes **all** moderation roles that are set on the server. You can add new roles using add_mod_role '
    )
    async def rm_mod_role(self,ctx: Context):
        self.g.mod_role = None
        self.g.save()
        await ctx.send(f":red_circle:**Removed mod role**")

    @command(
        name='rm_mod',
        brief='Removes moderation privileges from the user',
        help='Removes moderation privileges from the user. This is only valid for the individual permissions, so if '
             'the user was given moderation privileges trough add_mod. If a mod role is set and he still has this '
             'role, he will still have moderation privileges!'
    )
    async def rm_mod(self, ctx: Context, user_id: Union[int, str]):
        u,m = self.get_user(ctx,user_id)
        u.g_mod = False
        u.save()
        await ctx.send(f":red_circle:**User {m.mention if m is not None else u.d_name}({u.d_id}) "
                       f"is no longer a mod!**")

    @command(
        name='show_updates',
        help="Enables/Disables messages from the QOTD-Bot devs. Use True/False for <val>"
    )
    async def show_updates(self, ctx: Context, val: bool):
        self.g.show_updates = val
        self.g.save()
        await ctx.send(f"**Show updates has been set to _{self.g.show_updates}_**")

    @command(
        name='set_logchannel',
        brief='Sets the log channel for QOTD-Bot',
        help='Sets the log channel for the QOTD-Bot. This log channel will be used for various updates from QOTD-Bot,'
             'including but not limited to: Expiration of reasons and consequences, user information for users that '
             'have punishments/consequences on other servers and bot messages. It is highly recommended to set this!'
    )
    async def set_logchannel(self,ctx: Context, channel: Union[str, int]):
        ch_id = int(re.findall(r"\d+", channel)[0]) if isinstance(channel, str) else channel
        self.g.log_channel = ch_id
        self.g.save()
        ch = None
        for i in ctx.guild.channels:
            if i.id == ch_id:
                ch = i

        await ctx.send(f"Setting logchannel to {ch.mention} ({ch_id})")