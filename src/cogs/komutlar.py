from discord.ext import commands, tasks
import discord


class KomutlarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["del"])
    async def delete(self, ctx, count : int = 1):
        mod_role = discord.utils.get(ctx.guild.roles, name="temp")
        if not mod_role:
            await ctx.send("temp Rolü Açmanız Gerekmekte!")
            return
        if mod_role not in ctx.author.roles:
            await ctx.send("Yetkisiz Kullanım!")
            return
        if count < 500 and count > 0:
            await ctx.channel.purge(limit = count+1)
        else:
            await ctx.send('Kullanım Aralığı 1-500 Arasıdır.')

    
    @commands.command(aliases=['h'])
    async def help(self,ctx):
        info_list = ["join, j: Bulunduğun Kanala Bağlanması İçin Kullanılır.\n",
                    "disconnect, dc: Bulunduğu Kanaldan Çıkarmak ve Listeyi Temizlemek İçin Kullanılır.\n",
                    "play, p: Müzik Oynatmak İçin Kullanılır.\n",
                    "skip, s: Bir Sonraki Müziğe Geçmek İçin Kullanılır.\n",
                    "current, crn, now: Şuan Oynamakta Olan Müzik Bilgisini Getirir.\n",
                    "clear, clr: Oynatma Listesini Temizlemek İçin Kullanılır.\n",
                    "queue, que: Oynatma Listesini Görmek İçin Kullanılır.\n",
                    "resume, rsm: Oynatma Listesine Kaldığı Yerden Devam Etmek İçin Kullanılır.\n",
                    "stop, stp: Oynatıcıyı Durdurur ve Oynamakta Olan Müziği Listeden Siler.\n",
                    "volume, vol: 0-1000 Aralığında Ses Ayarı İçin Kullanılır.\n",
                    ]
        mod_role = discord.utils.get(ctx.guild.roles, name="temp")
        if mod_role:
            if mod_role in ctx.author.roles:
                info_list.append("tempadd, tmpadd: ',tempadd @etiket @Rol 1g' Şeklinde Belirli Süre Rol Eklemek İçin Kullanılır. d:gün, h: saat, m: dakika, s: saniye!\n")
                info_list.append("tempdel, tmpdel: ',tempdel @etiket @Rol' Şeklinde Rol Kaldırmak İçin Kullanılır.\n")
                info_list.append("delete, del: 1-500 Arası Girilen Değer Kadar Mesaj Silmek İçin Kullanılır.\n")
            else:
                info_list.append("Yönetici Komutlarını Görmek İçin temp Rolü Gerekmektedir.\n")
        else:
            await ctx.send("Yönetici Komutlarını Kullanabilmek İçin temp Rolü Açmanız Gerekmekte.")
        info_list.append("\nCoded by Simhi Sancak")
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = "Komut Kullanımları"
        temp = ""
        for i in info_list:
            temp = temp + i + "\n"
        embed.description = temp
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(KomutlarCog(bot))