from discord.ext import commands, tasks
import discord
import asyncio
import sqlite3 as lite
import time

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vt = lite.connect("role.sqlite")
        self.im = self.vt.cursor()
        self.role_check.start()
        
        
        
    """@commands.command(aliases=["mute"])
    async def temp_mute(self, ctx, member: discord.Member, mute_time : str = ""):
        if not member:
            await ctx.send("Kimi Susturmamı İstiyorsun?")
            return
        temp_time = 0
        temp_text = ""
        if len(mute_time) < 2:
            await ctx.send(f'Lütfen Süre Giriniz Kullanım.')
            return
        try:
            if mute_time[-1] == "d":
                temp = mute_time[0:-1]
                temp = int(temp)
                temp = temp * 60 * 60 * 24
                temp_time = temp
                temp_text = mute_time[0:-1] + " Gün "
            elif mute_time[-1] == "h":
                temp = mute_time[0:-1]
                temp = int(temp)
                temp = temp * 60 * 60
                temp_time = temp
                temp_text = mute_time[0:-1] + " Saat "
            elif mute_time[-1] == "m":
                temp = mute_time[0:-1]
                temp = int(temp)
                temp = temp * 60
                temp_time = temp
                temp_text = mute_time[0:-1] + " Dakika "
            elif mute_time[-1] == "s":
                temp = mute_time[0:-1]
                temp = int(temp)
                temp_time = temp
                temp_text = mute_time[0:-1] + " Saniye "
            if temp_time > 0:
                role = discord.utils.get(ctx.guild.roles, name="Muted")
                await member.add_roles(role)
                await ctx.send(temp_text + f'{member.mention} Mute Atıldı.')

                await asyncio.sleep(temp_time)
                await member.remove_roles(role)
                await ctx.send(f'Zaman Doldu: {member.mention} Mute Açıldı.')
            else:
                await ctx.send(f'Hatalı Kullanım.')
                return
        except:
            await ctx.send(f'Hata: Hatalı Kullanım.')
            return
        
        
    @commands.command(aliases=["unmute"])
    async def untemp_mute(self, ctx, member: discord.Member):
        if not member:
            await ctx.send("Kimi Susturmamı İstiyorsun?")
            return
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} Mute Açıldı.')"""

        
    @commands.command(aliases=["tmpadd"])    
    async def tempadd(self,ctx,member: discord.Member, role: discord.Role, süre: str = ""):
        if not member:
            await ctx.send("Kime Rol Vermemi İstiyorsun?")
            return
        if not role:
            await ctx.send("Hangi Rolü Vermemi İstiyorsun?")
            return
        if len(süre) < 1:
            await ctx.send("Ne Kadar Süre Vermemi İstiyorsun?")
            return
        mod_role = discord.utils.get(ctx.guild.roles, name="temp")
        if not mod_role:
            await ctx.send("temp Rolü Açmanız Gerekmekte!")
            return
        if mod_role not in ctx.author.roles:
            await ctx.send("Yetkisiz Kullanım!")
            return
        
        temp_time = 0
        try:
            if süre[-1] == "d":
                temp = süre[0:-1]
                temp = int(temp)
                temp = temp * 60 * 60 * 24
                temp_time = temp
                temp_text = süre[0:-1] + " Gün "
            elif süre[-1] == "h":
                temp = süre[0:-1]
                temp = int(temp)
                temp = temp * 60 * 60
                temp_time = temp
                temp_text = süre[0:-1] + " Saat "
            elif süre[-1] == "m":
                temp = süre[0:-1]
                temp = int(temp)
                temp = temp * 60
                temp_time = temp
                temp_text = süre[0:-1] + " Dakika "
            elif süre[-1] == "s":
                temp = süre[0:-1]
                temp = int(temp)
                temp_time = temp
                temp_text = süre[0:-1] + " Saniye "
            if temp_time > 0:
                #role = discord.utils.get(ctx.guild.roles, name=role)
                await member.add_roles(role)
                
                sorgu2 = """SELECT * FROM role_table"""
                self.im.execute(sorgu2)
                veriler = self.im.fetchall()
                for k in veriler:
                    if k[1] == str(ctx.guild.id) and k[2] == str(member.id) and k[4] == str(role.id):
                        print("selam")
                        del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(k[0])} """)
                        self.im.execute(del_sorgu)
                        self.vt.commit()
                        await ctx.send("Üye Güncelleniyor")
                    
                sorgu = ("""INSERT INTO role_table values ( NULL, "%s", "%s", "%s", "%s", "%s", "%s")""" % (ctx.guild.id, member.id, ctx.author.id, role.id, str(int(time.time())), str(int(time.time()) + temp_time)) )
                self.im.execute(sorgu)
                self.vt.commit()
                await ctx.send(f'{temp_text} {member.mention} {role} Rolü Eklendi. Ekleyen: {ctx.author.mention}')
            else:
                await ctx.send(f'Hatalı Kullanım.')
                return
        except:
            await ctx.send(f'Hata: Hatalı Kullanım.')
            return
    
    
    @commands.command(aliases=["tmpdel"])   
    async def tempdel(self,ctx,member: discord.Member, role: discord.Role):
        if not member:
            await ctx.send("Kimin Rolünü Silmemi İstiyorsun?")
            return
        if not role:
            await ctx.send("Hangi Rolü Silmemi İstiyorsun?")
            return
        mod_role = discord.utils.get(ctx.guild.roles, name="temp")
        if not mod_role:
            await ctx.send("temp Rolü Açmanız Gerekmekte!")
            return
        if mod_role not in ctx.author.roles:
            await ctx.send("Yetkisiz Kullanım!")
            return
        try:
            #role = discord.utils.get(ctx.guild.roles, name=role)
            sorgu2 = """SELECT * FROM role_table"""
            self.im.execute(sorgu2)
            veriler = self.im.fetchall()
            for k in veriler:
                if k[1] == str(ctx.guild.id) and k[2] == str(member.id) and k[4] == str(role.id):
                    del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(k[0])} """)
                    self.im.execute(del_sorgu)
                    self.vt.commit()
                    await ctx.send("Üye Güncelleniyor")
            await member.remove_roles(role)
            await ctx.send(f'{member.mention} {role} Rolü Kaldırıldı.')
        except:
            await ctx.send(f'Rol Kaldırırken Bir Hata Oluştu')

            
            
                
    @tasks.loop(seconds=5)
    async def role_check(self):
        try:
            sorgu2 = """SELECT * FROM role_table"""
            self.im.execute(sorgu2)
            veriler = self.im.fetchall()
            for veri in veriler:
                if int(veri[6]) <= int(time.time()):
                    guild = self.bot.get_guild(id = int(veri[1]))
                    if guild is not None:
                        user = guild.get_member(int(veri[2]))
                        if user is not None:
                            role = guild.get_role(int(veri[4]))
                            if role is not None:
                                await user.remove_roles(role)
                                del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(veri[0])} """)
                                self.im.execute(del_sorgu)
                                self.vt.commit()
                                print(f"silindi {user.name}")
                            else:
                                del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(veri[0])} """)
                                self.im.execute(del_sorgu)
                                self.vt.commit()     
                        else:
                            del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(veri[0])} """)
                            self.im.execute(del_sorgu)
                            self.vt.commit()     
                    else:
                        del_sorgu = (f"""DELETE FROM role_table WHERE id = {int(veri[0])} """)
                        self.im.execute(del_sorgu)
                        self.vt.commit()        
        except:
            print("Rol Silinirken Hata Oluştu")
            
        
def setup(bot):
    bot.add_cog(RoleCog(bot))