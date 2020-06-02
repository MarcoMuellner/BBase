from typing import Union
from discord import Guild,Member,Message
from discord.ext.commands import Context
from datetime import timedelta
import re
import pytz

from BBase.base_db.models import BaseGuild,BaseUser
from db.models import Join_Leave


def add_guild(ctx: Union[Context,Guild]):
    """
    Stores a guild into the db
    :param ctx: Context from command or Guild object
    """
    try:
        g_id = ctx.guild.id if isinstance(ctx,Context) else ctx.id
    except:
        return False
    g_name = ctx.guild.name if isinstance(ctx, Context) else ctx.name
    try:
        BaseGuild.objects.get(id=g_id)
    except BaseGuild.DoesNotExist:
        BaseGuild(id=g_id, name=g_name).save()

    return True

def get_user(member : Member, g:BaseGuild):
    try:
        u = BaseUser.objects.get(d_id=member.id, g=g)
        u.d_name = member.display_name
        u.save()
    except BaseUser.DoesNotExist:
        u = BaseUser(d_id=member.id,d_name=member.display_name, g=g
                     ,first_joined=member.joined_at.replace(tzinfo=pytz.UTC)
                     ,last_joined=member.joined_at.replace(tzinfo=pytz.UTC))
        u.save()

    return u

async def send_table(send_fun : callable, txt : str,add_raw = True):
    text = [txt[i:i+1000] for i in range(0, len(txt), 1000)]
    if add_raw:
        for i in range(0,len(text)):
            if i ==0:
                text[i] += "```"
            elif i == len(text) - 1:
                text[i] = "```" + text[i]
            else:
                text[i] = "```" + text[i] + "```"

    for text_part in text[:-1]:
        await send_fun(text_part)

    return await send_fun(text[-1])

def pretty_time(time : int):
    d_time = timedelta(seconds=time)
    days,hours,minutes = d_time.days, d_time.seconds//3600, (d_time.seconds//60)%60
    seconds = time - (days*24*3600 + hours*3600 + minutes*60)
    text = ""

    for val,txt in [(days,'day'),(hours,'hour'),(minutes,'minute'),(seconds, 'second')]:
        if val != 0:
            text += f"{int(val)} {txt}{'' if val == 1 else 's'} "
    return text.strip()

async def get_pre(_,message : Message):
    if not isinstance(message.author,Member):
        return ";"

    author_g_id = message.author.guild.id
    try:
        g = BaseGuild.objects.get(id=author_g_id)
    except BaseGuild.DoesNotExist:
        g = BaseGuild(id=author_g_id,name=message.author.guild.name)
        g.save()

    return g.prefix

def convert_str_date(time_string: str):
    time = 0
    if "d" in time_string:
        days = re.findall(r"(\d+)d", time_string)[0]
        time += int(days) * 24 * 3600

    if "h" in time_string:
        hours = re.findall(r"(\d+)h", time_string)[0]
        time += int(hours) * 3600

    if "m" in time_string:
        minutes = re.findall(r"(\d+)m", time_string)[0]
        time += int(minutes) * 60

    if "s" in time_string:
        seconds = re.findall(r"(\d+)s", time_string)[0]
        time += int(seconds)

    return time