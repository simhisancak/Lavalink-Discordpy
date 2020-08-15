"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.
Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re

import discord
import lavalink
from discord.ext import commands, tasks
import math
import urllib.parse


url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):    # This ensures the client isn't overwritten during cog reloads.
            key = open("lavalink.key", "r")
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('0.0.0.0', 7000,  key.read().replace("\n", ""), 'na', 'music-node') # Host, Port, Password, Region, Name
            key.close()
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #    This is essentially the same as `@commands.guild_only()`
        #    except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #    Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Bir Ses Kanalına Bağlanmalısın!')

        """
        # This check ensures that the bot and command author are in the same voicechannel. 
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play',)
        
        
        if not player.is_connected:
            if not should_connect:
                    raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:    # Check user limit too?
                    raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                    raise commands.CommandInvokeError('You need to be in my voicechannel.')"""

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        try:
            if not url_rx.match(query):
                query = f'ytsearch:{query}'
                results = await player.node.get_tracks(query)
                tracks = results['tracks'][0:10]
                if not results or not results['tracks']:
                    return await ctx.send('Hatalı Kullanım: Müzik Bulunamadı!')
                i = 0
                query_result = ''
                for track in tracks:
                    i = i + 1
                    query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
                embed = discord.Embed(color=discord.Color.blurple())
                embed.description = query_result

                await ctx.channel.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id
                
                response = await self.bot.wait_for('message', check=check)
                track = tracks[int(response.content)-1]

                player.add(requester=ctx.author.id, track=track)
                play_embed = discord.Embed(color=discord.Color.blurple())
                if not player.is_playing:
                    play_embed.title = "Şuan Oynatılan"
                    play_embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                    await player.play()
                else:
                    play_embed.title = "Sıraya Eklendi"
                    play_embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                    
                await ctx.send(embed=play_embed)
            else:
                results = await player.node.get_tracks(query)
                if not results or not results['tracks']:
                    return await ctx.send('Hatalı Kullanım: Müzik Bulunamadı!')

                embed = discord.Embed(color=discord.Color.blurple())

                if results['loadType'] == 'PLAYLIST_LOADED':
                    tracks = results['tracks']

                    for track in tracks:
                        # Add all of the tracks from the playlist to the queue.
                        player.add(requester=ctx.author.id, track=track)

                    embed.title = 'Oynatma Listesi Eklendi!'
                    embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} müzik'
                    if not player.is_playing:
                        await player.play()
                else:
                    track = results['tracks'][0]
                    player.add(requester=ctx.author.id, track=track)
                    if not player.is_playing:
                        embed.title = "Şuan Oynatılan"
                        embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                        await player.play()
                    else:
                        embed.title = "Sıraya Eklendi"
                        embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

                await ctx.send(embed=embed)
            if not player.is_connected:
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        except Exception as error:
            print(error)
    
        
        
    @commands.command(aliases=['crn', 'now'])
    async def current(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if player.is_playing:
            embed.title = 'Şuan Oynatılan'
            embed.description = player.current['title']
        else:
            embed.title = 'Hata'
            embed.description = f'Şuan Müzik Oynatılmıyor'
        await ctx.send(embed=embed)
            

    @commands.command(aliases=['clr'])
    async def clear(self,ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        start = 0
        end = 10
        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'
        if len(queue_list) > 1:
            player.queue.clear()
            await ctx.send("Sıra Temizlendi")
        else:
            await ctx.send("Hata: Sıra Boş")
            
    
    
    @commands.command(aliases=['que'])
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                            description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)
    
    
    @commands.command(aliases=['rsm'])
    async def resume(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        start = 0
        end = 10

        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'
        if not player.is_playing and len(queue_list) > 1:
            if not player.is_connected:
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                await player.play()
                await ctx.send('*⃣ | Bağlanıldı.')
            else:
                await player.play()
                await ctx.send('Devam Ediliyor')
        else:
            await ctx.send('Sıra Boş')

    @commands.command(aliases=['vol'])
    async def volume(self,ctx,*, query: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            if player.is_playing:
                await ctx.send("Ses Ayarlandı: {}".format(str(query)))
                await player.set_volume(query)
        except:
            print("hatalı kullanım volume")
            await ctx.send("Bir Hata Oluştu: Volume")



    @commands.command(aliases=['j'])
    async def join(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            await ctx.send('*⃣ | Bağlanıldı.')
        else:
            await ctx.send('*⃣ | Şuan Başka Bir Kanala Bağlı')


    @commands.command(aliases=['stp'])
    async def stop(self,ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if player.is_playing:
            embed.title = 'Stopped'
            embed.description = f'Oynatıcı Durduruldu.'
            await player.stop()
        else:
            embed.title = 'Fail'
            embed.description = f'Şuan Oynatılmıyor.'
        await ctx.send(embed=embed)


    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if player.is_playing:
            if len(player.queue) > 0:
                embed.title = 'Atlanıldı'
                embed.description = f'Şu Şarkıya Atlanıldı: ' + player.queue[0]['title']
                await player.skip()
            else:
                embed.title = 'Durduruldu'
                embed.description = f'Sıra Boş!'
                await player.stop()
        else:
            embed.title = 'Fail'
            embed.description = f'Şuan Oynatılmıyor.'
        await ctx.send(embed=embed)



    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
            """ Disconnects the player from the voice channel and clears its queue. """
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_connected:
                    # We can't disconnect, if we're not connected.
                    return await ctx.send('Bağlı Değil.')

            if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
                    # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
                    # may not disconnect the bot.
                    return await ctx.send('Şuanda Aynı Kanalda Değilsin!')

            # Clear the queue to ensure old tracks don't start playing
            # when someone else queues something.
            player.queue.clear()
            # Stop the current track so Lavalink consumes less resources.
            await player.stop()
            # Disconnect from the voice channel.
            await self.connect_to(ctx.guild.id, None)
            await ctx.send('*⃣ | Çıkış Yapıldı.')
            
def setup(bot):
    bot.add_cog(MusicCog(bot))
    