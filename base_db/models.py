from django.db import models
from django.utils import timezone

class BaseGuild(models.Model):
    id = models.BigIntegerField(verbose_name="Guild id, discord",primary_key=True)
    name = models.CharField(max_length=1024,verbose_name="Name of server")
    time_stamp = models.DateTimeField(verbose_name="Date of adding the guild", default=timezone.now)
    mod_role = models.CharField(max_length=1024, verbose_name="Role id of mods", null=True, default=None)
    log_channel = models.IntegerField(verbose_name="Channel for logging", null=True, default=None)
    show_updates = models.BooleanField(verbose_name="Show updates in logchannel", default=True)
    run = models.BooleanField(verbose_name="Bot running for guild", default=False)
    prefix = models.CharField(max_length=1024, verbose_name="Prefix for guild", default=";")

    def __repr__(self):
        return f"{self.id}:{self.name}"

    def __str__(self):
        return self.__repr__()

    def m_role(self):
        if self.mod_role is not None:
            return [int(i) for i in self.mod_role.split(";")]
        else:
            return None

    def add_role(self,role):
        if self.mod_role is not None:
            self.mod_role += f";{role}"
        else:
            self.mod_role = f"{role}"

    def rm_role(self,role):
        if f"{role}" in self.mod_role and f"{role}" != self.mod_role:
            self.mod_role = self.mod_role.replace(f";{role}","")
        elif f"{role}" == self.mod_role:
            self.mod_role = None


class BaseUser(models.Model):
    d_id = models.BigIntegerField(verbose_name="User id, discord")
    d_name = models.CharField(max_length=64,verbose_name="Name on server",default="")
    g = models.ForeignKey(BaseGuild, verbose_name="ID of server", on_delete=models.CASCADE)
    g_mod = models.BooleanField(verbose_name="Mod flag", default=False)
    is_bot = models.BooleanField(verbose_name="Flag if user is a bot",default=False)
    value_card_background = models.CharField(max_length=1024, verbose_name="Value url of imgur", null=True, default=None)
    money_card_background = models.CharField(max_length=1024, verbose_name="Money url of imgur", null=True, default=None)
    base_role_reached = models.BooleanField(verbose_name="Base role reached",default=False)
    first_joined = models.DateTimeField(verbose_name="First joined time and date", default=None,null=True)
    last_joined = models.DateTimeField(verbose_name="Last time the user joined",default=None,null=True)
    leave_date = models.DateTimeField(verbose_name="Leave time of the user",default=None,null=True)
    enabled_value_card_until = models.DateTimeField(verbose_name="Value card enabled until",default=None,null=True)
    bingo_message = models.BooleanField(verbose_name="Received bingo message",default=False)
    active_user = models.BooleanField(verbose_name="Flags this user as active",default=False)
    notify_upvote = models.BooleanField(verbose_name="Marks this as a user who wants to be reminded to upvote",default=False)
    notified = models.BooleanField(verbose_name="Marks that this user has been notified",default=False)

    class Meta:
        unique_together = (('d_id','g'))

    def __repr__(self):
        return f"ID:{self.d_name}({self.d_id}), gld: {self.g.name}"

    def __str__(self):
        return self.__repr__()

class UserIgnore(models.Model):
    user_id = models.BigIntegerField(verbose_name="User id that should be ignored in messages")
