from typing import Union
from discord import Guild,Member
from discord.ext.commands import Context
from db.models import DBUser as BaseUser,DBGuild as BaseGuild

def add_guild(ctx: Union[Context,Guild]):
    """
    Stores a guild into the db
    :param ctx: Context from command or Guild object
    """
    g_id = ctx.guild.id if isinstance(ctx,Context) else ctx.id
    g_name = ctx.guild.name if isinstance(ctx, Context) else ctx.name
    try:
        BaseGuild.objects.get(id=g_id)
    except BaseGuild.DoesNotExist:
        BaseGuild(id=g_id, name=g_name).save()

def get_user(member : Member, g:BaseGuild):
    try:
        u = BaseUser.objects.get(d_id=member.id, g=g)
    except BaseUser.DoesNotExist:
        u = BaseUser(d_id=member.id,d_name=member.display_name, g=g)
        u.save()
    return u

async def send_table(send_fun : callable, txt : str,add_raw = True):
    rows = txt.split("\n")
    send_text = ""
    for r in rows:
        if len(send_text) > 1900:
            if add_raw:
                send_text += "```"
            await send_fun(send_text)
            if add_raw:
                send_text = "```"
            else:
                send_text = ""
        send_text += r
        send_text += "\n"
    await send_fun(send_text)