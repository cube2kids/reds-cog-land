from redbot.core import commands, Config, checks
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions
import discord
import asyncio
import time
import datetime

def dateconverter(secondes):
    pretty = time.strftime('%HH %MM %SS', time.gmtime(secondes))
    return pretty
class Matchmaking(commands.Cog):
    def __init__(self):
        self.config = Config.get_conf(self, identifier=4269424269)
        default_guild = {
            "last_used": 0,
            "current_channels": {},
            "now_channels": [],
            "mm_channel": 0,
            "toggle": False,
            "role": None,
            "ping": 1800,
            "message": 900,
            "channel": 5400,
            "timeout": 1800
        }
        default_global = {
            "current_tasks": [],
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
    async def initialize(self):
        tasks = self.config.current_tasks()
        for i in tasks:
            guild = self.bot.get_guild(i["guild"])
            channel = guild.get_channel(i["channel"])
            start_ts = i["start_ts"]
            user = guild.get_member(i["user"])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.command()
    async def matchmaking(self, ctx):
        async def handle_channel(channel, guild, challenger, start_ts):
            #creating the task
            while True:
                current_chans = await self.config.guild(guild).now_channels()
                if id_channel not in current_chans:
                    return
                #verif que la limite absolue est atteinte
                now_ts = time.time()
                if now_ts > start_ts + await self.config.guild(guild).channel():
                    #await ctx.send(current_channels)
                    current_channels.remove(id_channel)
                    await self.config.guild(guild).now_channels.set(current_channels)
                    await channel.delete()
                    return
                #verif que la limite relative au last msg est atteinte
                if await self.config.guild(guild).message() != 0:
                    last_message_l = await guild.get_channel(id_channel).history(limit=1).flatten()
                    last_message = last_message_l[0]
                    last_message_ts = last_message.created_at.timestamp()
                    if now_ts > last_message_ts + await self.config.guild(guild).message():
                        current_channels.remove(id_channel)
                        await self.config.guild(guild).now_channels.set(current_channels)
                        await channel.delete()
                        return
                await asyncio.sleep(10)
        if ctx.guild.get_channel(await self.config.guild(ctx.guild).mm_channel()) == None:
            await ctx.send("veuillez définir le channel pour le matchmaking avec `{0}mmadmin channel`".format(ctx.clean_prefix))
            return
        if ctx.channel.id != await self.config.guild(ctx.guild).mm_channel():
            await ctx.send("cette commande ne peut-être utilisé que dans le sallon de matchmaking !")
            return
        active = await self.config.guild(ctx.guild).toggle()
        pingdelay = await self.config.guild(ctx.guild).ping()
        if time.time() > await self.config.guild(ctx.guild).last_used() + pingdelay and active == True:
            if await self.config.guild(ctx.guild).role() == None:
                await ctx.send("le role ping n'est pas configuré.")
                return
            msg = await ctx.send("recherche d'adverssaires en cours.\n\n"
                        "hey {1}, {0} veut se batter ! \n"
                        "si une personne est disponnible, \n"
                        "régissez avec :white_check_mark: pour lancer un combat.\n"
                        "et créer un channel textuel dédié\n"
                        "cette commande sera disponnible à nouveau dans 1 minute, et le ping dans {2}.".format(ctx.author.mention, ctx.guild.get_role(await self.config.guild(ctx.guild).role()).mention, dateconverter(await self.config.guild(ctx.guild).ping())))
        else:
            msg = await ctx.send("recherche d'adverssaires en cours.\n\n"
                        "hey, {0} veut se batter ! \n"
                        "si une personne est disponnible, \n"
                        "régissez avec :white_check_mark: pour lancer un combat.\n"
                        "et créer un channel textuel dédié\n"
                        "cette commande sera disponnible à nouveau dans 1 minute.".format(ctx.author.mention))
        await self.config.guild(ctx.guild).last_used.set(time.time())
        await msg.add_reaction('✅')
        #attendre une réaction
        def check(reaction, user):
            return user != ctx.me and user != ctx.author and str(reaction.emoji) == '✅' and reaction.message.id == msg.id 
        try:
            timeout = await self.config.guild(ctx.guild).timeout()
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            await ctx.send("personne ? tant pis.\nDésolé {0}".format(ctx.author.mention))
            return
        else:
            await ctx.send('LET\'S GO !')
            #créer les chans
            chan = await ctx.channel.category.create_text_channel("quickplay", reason="c'est l'heure de la bagarre")
            await chan.send("{0} VS {1} \n           :crossed_swords:  \n\n BATTEZ VOUS !\n\n ce chan sera supprimé 15 minutes après sa dernière activité, ou dans 1h30 quoi qu'il arrive.\n Vous pouvez aussi utiliser `{3}closechannel` pour supprimer ce sallon.\n"
                            "`{3}addmember @mention` pour ajouter une personne dans le salon (vous pouvez utiliser son ID, et la commande ne marche que dans ce sallon).\n"
                            "{2} peut aussi utiliser `{3}kickchannel @mention` pour retirer un membre".format(ctx.author.mention, user.mention, ctx.author.mention, ctx.clean_prefix))
            await chan.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
            await chan.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await chan.set_permissions(user, read_messages=True, send_messages=True)
            
            tasks = self.config.guild.current_tasks()
            current_channels = await self.config.guild(ctx.guild).now_channels()
            start_ts = time.time()
            id_channel = channel.id
            current_channels.append(id_channel)
            await self.config.guild(ctx.guild).now_channels.set(current_channels)
            tasks.append({
                "guild": ctx.guild.id,
                "start_ts": start_ts,
                "channel": chan.id,
                "user": user.id,
            })
            await self.config.current_tasks.set(tasks)
            await handle_channel(chan, ctx.guild, user, start_ts)

    @commands.command()
    async def closechannel(self, ctx):
        current_channels = await self.config.guild(ctx.guild).now_channels()
        chan_id = ctx.channel.id
        if chan_id in current_channels:
            msg = await ctx.send("vous êtes sur le point de supprimer ce channel. \n sur ?")
            start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
            pred = ReactionPredicate.yes_or_no(msg, ctx.author)
            await ctx.bot.wait_for("reaction_add", check=pred)
            if pred.result is True:
                current_channels.remove(ctx.channel.id)
                await self.config.guild(ctx.guild).now_channels.set(current_channels)
                await ctx.channel.delete()
            else:
            	await msg.delete()
        else:
            await ctx.send("vous n'êtes pas dans un channel temporaire !")
    @commands.command()
    async def addmember(self, ctx, user: discord.Member):
        current_channels = await self.config.guild(ctx.guild).now_channels()
        if ctx.channel.id in current_channels:
            await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
            await ctx.tick()
    @commands.command()
    async def kickchannel(self, ctx, user: discord.Member):
        current_channels = await self.config.guild(ctx.guild).now_channels()
        if ctx.channel.id in current_channels:
            await ctx.channel.set_permissions(user, overwrite=None)
            await ctx.tick()
    @commands.group()
    @commands.admin_or_permissions(manage_roles=True)
    @checks.bot_in_a_guild()
    async def mmadmin(self, ctx: commands.Context):
        """réglages du module"""
        
        pass
    @mmadmin.command(name="channel")
    async def mmadmin_channel(self, ctx: commands.Context, *, role: discord.TextChannel):
        """la commande ne marchera que dans ce channel."""
        await self.config.guild(ctx.guild).mm_channel.set(role.id)
        await ctx.send("Channel configuré!")
    @mmadmin.command(name="ping")
    async def mmadmin_ping(self, ctx: commands.Context, state: bool):
        """définis si le bot doit mentionner ou pas le rôle.
        utilisez True/False, On/Off, Y/N"""
        if state:
            await self.config.guild(ctx.guild).toggle.set(True)
            await ctx.send("le ping a été activé. utilisez `{0}mmadmin role` pour changer le role.".format(ctx.clean_prefix))
        else:
            await self.config.guild(ctx.guild).toggle.set(False)
            await ctx.send("le ping a été désactivé.")
    @mmadmin.command(name="role")
    async def mmadmin_role(self, ctx: commands.Context, role: discord.Role):
        """pour définir le rôle a ping pour le matchmaking"""
        await self.config.guild(ctx.guild).role.set(role.id)
        await ctx.send("le role a été configuré.\nPour qu'il soit actif, utilisez `{0}mmadmin ping yes`".format(ctx.clean_prefix))
    @mmadmin.group(name="delays")
    async def mmadmin_delays(self, ctx: commands.Context):
        """règle les différents délais"""
        
        pass
    @mmadmin_delays.command(name="ping")
    async def mmadmin_delays_ping(self, ctx, duree: int):
        """règle l'interval entre 2 pings en minutes"""
        if duree > 2888:
            await ctx.send("durée trop longue. Doit être inferieur a 2 jours.")
            return
        await self.config.guild(ctx.guild).ping.set(duree * 60)
        await ctx.send("durée reglée")
    @mmadmin_delays.command(name="message")
    async def mmadmin_delays_message(self, ctx, duree: int):
        """règle le délai de supression après le dernière activité, en minutes. Mettez a 0 pour désactiver"""
        if duree > 2888:
            await ctx.send("durée trop longue. Doit être inferieur a 2 jours.")
            return
        await self.config.guild(ctx.guild).message.set(duree * 60)
        await ctx.send("durée reglée")
    @mmadmin_delays.command(name="channel")
    async def mmadmin_delays_channel(self, ctx, duree: int):
        """règle le délai de supression du channel."""
        if duree > 2888:
            await ctx.send("durée trop longue. Doit être inferieur a 2 jours.")
            return
        await self.config.guild(ctx.guild).channel.set(duree * 60)
        await ctx.send("durée reglée")
    @mmadmin.command(name="timeout")
    async def mmadmin_timeout(self, ctx, duree: int):
        """règle la durée max pendent laquelle un peut réagir. Doit-être en minutes."""
        if duree > 120:
            await ctx.send("durée trop longue. Doit être inferieur a 2 heures.")
            return
        await self.config.guild(ctx.guild).timeout.set(duree * 60)
        await ctx.send("durée reglée")
