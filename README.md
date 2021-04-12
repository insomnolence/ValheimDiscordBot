# ValheimDiscordBot
Discord bot that can manage and get information on a Dedicated Windows Valheim Server

Seen a few bots written for Linux and using Node.js. Haven't seen too many using Python on Windows, so I thought I'd create one to manange my own server. I play on a dedicated Windows server with some friends ( that I trust ) so allowing them to upgrade or start/stop the server is not worrying to me. Being allowed to upgrade the server if I'm not available is a pretty much a neccesity for us.

The script uses a series of Windows Batch files to perform their actions. As the Windows machine this is run on is local, I sometimes want to run these batch files manually. Another reason why instead of running these commands via a subprocess in the Python script, I create separate processes as I don't want them linked to the fact the Bot is running or not. This complicates the script, but was a requirement for me for flexibility.

## Third Party Libraries

The following third party libraries were needed to be installed to get this script to work. They should be easily installed by using the pip install command.

* discord.py
* requests
* psutil
* pywin32

## Script Config

The following variables in the Python script need to point to where your Dedicated Valheim Server Directory is located. The batch files will be discussed below.

* SERVER_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Startup.bat'
* BACKUP_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Backup.bat'
* UPDATE_BAT = r'D:\Dedicated\ValheimServer\InstallDirectory\Update.bat'

The following variable is the Discord Bot Token you obtain when creating the bot in the Discord Developer Application portal. This allows the bot to connect to your Discord Server/Channel.

* DISCORD_BOT_TOKEN = r'DISCORD_BOT_TOKEN'


## Windows Batch Files

These files should be created in your dedicated Valheim Server Directory. You can use them by double clicking on them normally, or by letting the bot use them. 

### Startup.bat

Basic start up script supplied by IronWorks. It's got a couple changes so the window will be destroyed after a Ctrl-C is recieved ( so it doesn't ask if you want to terminate the batch job )

```
@echo off
set SteamAppId=892970

echo "Starting server PRESS CTRL-C to exit"

REM Tip: Make a local copy of this script to avoid it being overwritten by steam.
REM NOTE: Minimum password length is 5 characters & Password cant be in the server name.
REM NOTE: You need to make sure the ports 2456-2458 is being forwarded to your server through your local router & firewall.
start valheim_server -nographics -batchmode -name "SERVER_NAME" -port 2456 -world "WORLD_NAME" -password "YOUR_PASSWORD"
echo
exit /b
```

### Backup.bat

Simple backup script/command to copy the world data to a back up directory that you create.

```
xcopy "C:\Users\YOUR_USER_NAME\AppData\LocalLow\IronGate\Valheim\worlds" "D:\YOUR_BACKUP_DIRECTORY" /s /e /h /y
```

### Update.bat

Update script/command used to install, update, or verify the Valheim dedicated server for Windows in the appropriate install directory

```
D:\STEAMCMD_DIRECTORY\steamcmd.exe +login anonymous +force_install_dir D:\VALHEIM_SERVER_DIR\ +app_update 896660 validate +exit
```
