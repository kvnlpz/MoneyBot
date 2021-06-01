import email
import imaplib
import re
import time
import os
import string
import sys
import os.path
import discord
import asyncio
import requests
import yaml
import os


# TODO() 
# REFACTOR AND CONSOLIDATE CODE, REMOVE REPETETIVE CHUNKS AND CONVERT TO FUNCTIONS
# IMPLEMENT WEBULL FUNCTIONALITY


conf = yaml.load(open('app.yml'))
TOKEN = conf['bot']['token']
someChannelID = int(conf['bot']['channelID'])

channels = []
EMAIL = conf['user']['email']
PASSWORD = conf['user']['password']
SERVER = 'imap.gmail.com'
# someChannel = None

client = discord.Client()
someChannel = client.get_channel(someChannelID)
# ONLY have this line uncommented if on Windows
os.system('color 0f') # sets the background to blue

def analystChanges(subject):
    print()

# courtesy of some SO answer
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

# work in progess, setting it up to make the bot assignable
def set_channel(channel_id):
    f = open("channelList.txt", "r+")
    if str(channel_id) in f.read():
        # dont write to it;
        print("placeholder lol")
    else:
        f.write("\n" + channel_id)
    f.close()
    get_channels()

# work in progess, setting it up to make the bot assignable
def remove_channel(channel_id):
    f = open("channelList.txt", "r+")
    lines = f.read().splitlines()
    channel_list = list(f)
    print(lines)
    try:
        lines.remove(channel_id)
        f.truncate(0)
        f.close()
        f = open("channelList.txt", "r+")
        for x in lines:
            print(x)
            # just checking if it is the first item in the list
            if x == lines[0]:
                f.write(x)
            else:
                f.write("\n" + x)
    except:
        print("that channel is not in the list")
    f.close()
    get_channels()


def get_channels():
    channels.clear()
    f = open("channelList.txt", "r+")
    lines = f.read().splitlines()
    channel_list = list(f)
    f.close()
    for i in lines:
        channels.append(int(i))


async def listener_loop():
    print("looping...")
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    someChannel = client.get_channel(someChannelID)
    # we choose the inbox but you can select others
    mail.select('inbox')
    status, data = mail.search(None, '(UNSEEN)','(FROM "alerts@thinkorswim.com" OR OR (SUBJECT "Analyst Upgrades") (SUBJECT "Analyst Downgrades") (SUBJECT "News alert for all symbols"))')
    mail_ids = []
    for block in data:
        mail_ids += block.split()
    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')
        raw_email = data[0][1]  # here's the body, which is raw text of the whole email
        for response_part in data:
            # so if its a tuple...
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        # if the content type is text/plain we extract it
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    # if the message isn't multipart, just extract it
                    mail_content = message.get_payload(decode=1)
                    if "Analyst Upgrades" not in mail_subject and "Analyst Downgrades" not in mail_subject:
                        # print(mail_subject)
                        html = mail_content.decode('utf-8')
                        x = re.sub("<[^>]*>", " ", html)
                        string_to_keep = "News alert for all symbols"
                        x = re.sub(r'^.*?News alert for all symbols', 'News alert for all symbols', x)
                        index = x.find(string_to_keep)  # stores the index of a substring or char
                        x = x[index:]  # returns the chars before the seen char or substring
                        sub_str = "To view and manage your alerts"
                        sub_str_2 = "News alert for all symbols"
                        res = x[:x.index(sub_str) + len(sub_str)]
                        res = re.sub(sub_str, "", res)
                        res = re.sub(sub_str_2, "", res)
                        print(colored(255, 255, 0,res.strip()))
                        embedVar = discord.Embed(title="Alert System", description="", color=0xFFFFFF)
                        embedVar.add_field(name="Alert", value=res.strip(), inline=False)
                        await someChannel.send(embed=embedVar)
                    else:
                        if "Symbols:" in mail_subject:
                            string_to_keep = "Symbols:"
                            index = mail_subject.find(string_to_keep)  # stores the index of a substring or char
                            mail_subject = mail_subject[index:]  # returns the chars before the seen char or substring
                            mail_subject = re.sub("Symbols:", "", mail_subject)
                            print(colored(255, 0, 0, mail_subject))
                            symbols = mail_subject.split()
                            colorCode = 0x00ff00
                            if "Downgrades" in mail_subject:
                                colorCode = 0xCC0000
                            embed_desc = "[" + symbols[0] + "]" + "(https://robinhood.com/stocks/" + symbols[0] + ")"
                            embedVar = discord.Embed(title="Analyst Changes", description=embed_desc,color=colorCode)
                            embedVar.add_field(name="Changes", value=mail_subject, inline=False)
                            await someChannel.send(embed=embedVar)
                            await asyncio.sleep(3)

                        elif "symbol:" in mail_subject:
                            string_to_keep = "symbol:"
                            index = mail_subject.find(string_to_keep)  # stores the index of a substring or char
                            mail_subject = mail_subject[
                                           index:]  # returns the chars before the seen char or substring
                            mail_subject = re.sub("symbol:", "", mail_subject)
                            print(colored(255, 0, 0, mail_subject))
                            symbols = mail_subject.split()
                            colorCode = 0x00ff00
                            if "Downgrades" in mail_subject:
                                colorCode = 0xCC0000
                            embed_desc = "[" + symbols[0] + "]" + "(https://robinhood.com/stocks/" + symbols[0] + ")"
                            embedVar = discord.Embed(title="Analyst Changes", description=embed_desc,color=colorCode)
                            embedVar.add_field(name="Changes", value=mail_subject, inline=False)
                            await someChannel.send(embed=embedVar)
                            await asyncio.sleep(3)

    mail.logout()
    await asyncio.sleep(5)


async def my_background_task():
    await client.wait_until_ready()
    


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    someChannel = client.get_channel(someChannelID)
    while not client.is_closed():
        await listener_loop()
        while True:
            await listener_loop()
        print("60 Seconds")
        await asyncio.sleep(60)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!p'):
        # templog.write(message.content)
        print("received command")
        await message.channel.send("I'm online")

    if message.content.startswith("!sc"):
        set_channel(str(message.channel.id))
        await message.channel.send("adding this channel to the list")

    if message.content.startswith("!rc"):
        remove_channel(str(message.channel.id))
        await message.channel.send("removing this channel from the list")


# client.loop.create_task(my_background_task())
client.run(TOKEN)
