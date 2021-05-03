import asyncio
import discord
import json
import psutil
import os
import subprocess
import win32api as api
import win32console as con

from requests import get

# Batch scripts that are being run and their locations
# These files were created before the bot, and allows the
# admin/user to do manually execute them locally

# Add your Dedicate Valheim Server install directory below. The batch files
# are described in the README
SERVER_EXE = 'valheim_server.exe'
SERVER_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Startup.bat'
BACKUP_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Backup.bat'
UPDATE_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Update.bat'

PLAYER_FILE_LOC = r'D:\Dedicated\ValheimServer\InstallDirectory\players.json'
DISCORD_BOT_TOKEN = r'DISCORD_BOT_TOKEN'

class ValheimClient(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, msg):        
        if msg.content.startswith('!') is False:
            return
        
        if msg.content == '!valheim start':
            await self.server_control('start', msg)
            return
        
        if msg.content == '!valheim stop':
            await self.server_control('stop', msg)
            return
        
        if msg.content == '!valheim restart':
            await self.server_control('restart', msg)
            return

        if msg.content == '!valheim status':
            await self.check_active(discord, msg)
            return

        if msg.content == '!valheim ip':
            ip = get('https://checkip.amazonaws.com').text.strip()
            await msg.channel.send(ip)
            return

        if msg.content == '!valheim backup':
            await self.backup_world(msg)
            return
        
        if msg.content == '!valheim update':
            await self.update_server(msg)
            return

        if msg.content == '!valheim players':
            await self.check_players(msg)
            return

        if msg.content == '!help':
            await msg.reply('\ntype `!valheim start` to start the server'
	        + '\ntype `!valheim stop` to stop the server'
            + '\ntype `!valheim restart` to restart the server'
            + '\ntype `!valheim status` to get server status'
            + '\ntype `!valheim ip` to get the server ip address'
            + '\ntype `!valheim backup` to backup the server world'
            + '\ntype `!valheim update` to update the server'
            + '\ntype `!valheim players` to get online status for all players')
            return

    async def server_control(self, direction, msg):

        await msg.add_reaction('⏳')

        p = self.get_process()

        if direction == 'start':
            if p is not None:
                await msg.channel.send("Server is already started!")
            else:
                p = await self.start_server()
                if p is not None:
                    await msg.channel.send("Server is started!")
                else:
                    await msg.channel.send("Server error - could not be started!")
        
        if direction == 'stop':
            if p is not None:
                await self.stop_server(p.pid)
                await msg.channel.send("Server stopped!")
            else:
                await msg.channel.send("Server already stopped!")
    
        if direction == 'restart':
            if p is not None:
                await self.stop_server(p.pid)
                
            p = await self.start_server()
            if p is not None:
                await msg.channel.send("Server is restarted!")
            else:
                await msg.channel.send("Server error - could not be restarted!")

        return

    async def start_server(self):
        os.startfile(SERVER_BAT)
        # Not ideal, but I've found my server takes about this long to load properly
        # Otherwise, checking right away will say it is up, even though it may throw
        # an error and shutdown.
        await asyncio.sleep(15)
        return self.get_process()        

    async def stop_server(self, pid):
        self.send_ctrl_c(pid)

        count = 0
        p = self.get_process()
        # Again, not ideal. But want to make sure the server is actually
        # down before reporting that we were successful. But, don't want to
        # do this forever, so give up after 4 attempts
        while p is not None and count < 4:
            await asyncio.sleep(5)
            count += 1
            p = self.get_process()

        return

    async def check_active(self, discord, msg):

        process = self.get_process()
        
        if process and process.status() == "running":
            embed = discord.Embed(title="Valheim Server Status",
            description="Server is up!",
            color=0x3CB371)

            embed.set_thumbnail(url="https://media1.tenor.com/images/3359b21273025f5dda055af6673e4f67/tenor.gif?itemid=20482717")
            await msg.channel.send(embed = embed)

        else:
            embed = discord.Embed(title="Valheim Server Status",
            description="Server is inactive - try restarting!",
            color=0xFF4500)
            
            embed.set_thumbnail(url="https://media.tenor.com/images/1fd78e320ee2d6266a4a1b894c7a1dbc/tenor.gif")

            await msg.channel.send(embed = embed)

        return

    async def backup_world(self, msg):
         p = subprocess.Popen(BACKUP_BAT)
         p.wait()
         await msg.channel.send("Server World backed up !")

         return


    async def update_server(self, msg):
        await msg.add_reaction('⏳')

        server_was_up = False
        p = self.get_process()
        if p is not None:
            server_was_up = True
            await self.stop_server(p.pid)
            await msg.channel.send("Server has been stopped !")

        update_process = subprocess.Popen(UPDATE_BAT)
        update_process.wait()
        await msg.channel.send("Server has been updated/verified !")

        if server_was_up:
            p = await self.start_server()
            if p is not None:
                await msg.channel.send("Server has been restarted !")
            else:
                await msg.channel.send("Server error - could not be restarted !")
            
        return

    async def check_players(self, msg):
        if not os.path.exists(PLAYER_FILE_LOC):
            await msg.channel.send("Could not find the Players file to check online.")
            return

        player_list = {}        
        with open(PLAYER_FILE_LOC) as json_file:
            player_list = json.load(json_file)
     
        at_least_one = False
        return_msg = r'Player(s) Currently Online: '
        for key, value in player_list.items():
            if value == 'Yes':
                at_least_one = True
                return_msg += '\n'
                return_msg += key
        
        if at_least_one:
            await msg.channel.send(return_msg)
        else:
            return_msg += '\n'
            return_msg += 'None'
            await msg.channel.send(return_msg)           

        return

    # The server could be started/stopped/updated outside of the bot, so
    # we need to find the process via list of Windows processes. 
    def get_process(self):
        process = None
        for p in psutil.process_iter():
            if p.name() == SERVER_EXE:
                process = p
                break
        
        return process
        
    # This is just madness. Needed to send a Ctrl-C to the process that
    # is running the server. To do so on windows, you need to switch the windows console 
    # to that process, send the ctrl-c, wait ( so you don't switch back and potentially
    # send the ctrl-c on the python running console ), then switch back to the console running 
    # the Python script.
    # Why am I not running this on Linux?!    
    def send_ctrl_c(self, pid):
        con.FreeConsole()
        if con.AttachConsole(int(pid)) == None: 
            api.SetConsoleCtrlHandler(None, 1)
            api.GenerateConsoleCtrlEvent(con.CTRL_C_EVENT, 0)
            api.Sleep(2000)
            con.FreeConsole()
            con.AttachConsole(int(os.getppid()))
            api.SetConsoleCtrlHandler(None, 0)



client = ValheimClient()
client.run(DISCORD_BOT_TOKEN)
