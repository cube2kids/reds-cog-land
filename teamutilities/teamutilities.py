from redbot.core import commands, Config, utils, checks
from redbot.core.utils import mod
import discord
import asyncio

class Teamutilities(commands.Cog):
    """My custom cog"""
    def __init__(self):
        self.config = Config.get_conf(self, identifier=5765483508)
        default_guild = {
            "list_roles": [],
            "leader_role": 0
        }

        self.config.register_guild(**default_guild)
    @checks.admin()
    @commands.command()
    async def teamset(self, ctx, teamleader: discord.Role):
        """ajouter le role de team leader"""
        await self.config.guild(ctx.guild).leader_role.set(teamleader.id)
        await ctx.tick()

    @commands.command()
    async def addteam(self, ctx, membre: discord.Member):
        """ajouter un role de team a un membre"""
        leaderrole = ctx.guild.get_role(await self.config.guild(ctx.guild).leader_role())
        if leaderrole == None:
            await ctx.send("le role team leader n'est pas configuré ou n'est pas valide.\n Demandez à un admin d'utiliser `.teamset` pour l'ajouter")
            return
        if leaderrole in [y for y in ctx.author.roles]:
            liste_roles = await self.config.guild(ctx.guild).list_roles()
            nouvelle_liste = {v.id for v in ctx.author.roles}
            nf = [x for x in liste_roles if x in nouvelle_liste]
            if len(nf) != 1:
                await ctx.send("vos rôles de teams ne sont pas corrects !")
                return
            await membre.add_roles(ctx.guild.get_role(nf[0]))
            await ctx.tick()
            await asyncio.sleep(4)
            await ctx.message.delete()
    @checks.mod()
    @commands.command()
    async def addteamrole(self, ctx, role: discord.Role):
        """ajouter un nouveau role de team dans le base de données"""
        liste_roles = await self.config.guild(ctx.guild).list_roles()
        if role.id in liste_roles:
            await ctx.send("la team éxiste déjà !")
            return
        liste_roles.append(role.id)
        await self.config.guild(ctx.guild).list_roles.set(liste_roles)
        await ctx.tick()
    @checks.mod()
    @commands.command()
    async def listteams(self, ctx):
        """donner la liste des roles de teams présents sur le serveur"""
        embed=discord.Embed(title="liste des teams enregistrés :", color=0xe90130)
        liste_roles = await self.config.guild(ctx.guild).list_roles()
        i = 0
        while i != len(liste_roles):
            embed.add_field(name=ctx.guild.get_role(liste_roles[i]), value=liste_roles[i], inline=False)
            i += 1
        embed.set_footer(text="fais avec ❤ par red#4356")
        await ctx.send(embed=embed)
    @checks.mod()
    @commands.command()
    async def removeteamrole(self, ctx, team: discord.Role):
        """retirer un role de team de la base données"""
        liste_roles = await self.config.guild(ctx.guild).list_roles()
        if team.id not in liste_roles:
            await ctx.send("la team n'éxiste pas encore !")
            return
        liste_roles.remove(team.id)
        await self.config.guild(ctx.guild).list_roles.set(liste_roles)
        await ctx.tick()
    @commands.command()
    async def removeteam(self, ctx, membre : discord.Member):
        """enlever un role de team a un membre"""
        # Your code will go here
        leaderrole = ctx.guild.get_role(await self.config.guild(ctx.guild).leader_role())
        if leaderrole == 0:
            await ctx.send("le role team leader n'est pas configuré ou n'est pas valide.\n utilisez `.teamset` pour l'ajouter")
            return
        if leaderrole in [y.id for y in ctx.author.roles]:
            liste_roles = await self.config.guild(ctx.guild).list_roles()
            nouvelle_liste = {v.id for v in ctx.author.roles}
            nf = [x for x in liste_roles if x in nouvelle_liste]
            if len(nf) != 1:
                await ctx.send("vos rôles de teams ne sont pas corrects !")
                return
            await membre.remove_roles(ctx.guild.get_role(nf[0]))
            await ctx.tick()
            await asyncio.sleep(4)
            await ctx.message.delete()