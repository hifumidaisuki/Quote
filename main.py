

import os
import textwrap
from io import BytesIO

import sys
import discord
import requests
from dotenv import load_dotenv

from PIL import Image, ImageDraw, ImageFont

fonts = [
    ImageFont.truetype("resources/mplus-1p-medium.ttf", 50),
    ImageFont.truetype("resources/SourceHanCodeJP.ttc", 40)
   ]

background = Image.open('resources/background.png')
load_dotenv()

murl = 'https://discord.com/api/v9/channels/{channelid}/messages/{messageid}'
aurl = 'https://cdn.discordapp.com/avatars/{userid}/{hash}?size=512'



client = discord.Client(intents=discord.Intents.all())



@client.event
async def on_ready():

    print('ログインしました')
    for index,guilds in enumerate(client.guilds):
        print(str(index) + ' : ' + guilds.name + ' : ' + str(guilds.id))



@client.event
async def on_message(message):

    if message.author.bot:
        return
    if str(client.user.id) in message.content:
        try:
            data = requests.get(murl.format(channelid=message.channel.id, messageid=message.reference.message_id),
                            headers=({'Content-Type': 'application/json', 'Authorization': 'Bot ' + os.getenv("TOKEN")})).json()
        except:
            await message.channel.send('殺す')
            return
        pic = BytesIO()
        generateimage(data, message.channel.guild.members).save(fp=pic, format='PNG')
        pic.seek(0)



        if data.get('content'):

            await message.reply(file=discord.File(fp=pic, filename='quote.png'))
        else:
            await message.reply('読めねーよ死ね')

        print('done!')






def generateimage(data, memberlist):
    content = data.get('content')
    for member in memberlist:
        if str(member.id) in content:
            content = content.replace('<@{}>'.format(str(member.id)), '@{}'.format(member.name))
    author = data.get('author')

    temp = Image.new("RGBA", background.size, (255, 255, 255, 0))
    temp.paste(Image.open(BytesIO(
        requests.get(aurl.format(userid=author.get('id'), hash=author.get('avatar'))).content)).resize(
        (background.height, background.height)).convert(mode="L"), (-100, 0))
    final = Image.alpha_composite(temp, background)

    ttfontname = "mplus-1p-medium.ttf"
    fontsize = 50

    text = textwrap.wrap(content, width=12)



    textRGB = (255, 255, 255)


    note = Image.new('RGB', (630, 630), (0, 0, 0))


    draw = ImageDraw.Draw(note)
#    font = ImageFont.truetype(ttfontname, fontsize)
#    font_family = ImageFont.FreeTypeFontFamily(fonts[0], fonts[1])
    textWidth, textHeight = draw.textsize(content, font=fonts[0])
    cursorh, padding = note.height / 2 - len(text) * 25, 10

    for line in text:
        textWidth, textHeight = draw.textsize(line, font=fonts[0])
        draw.text(((note.width - textWidth) / 2, cursorh - 50), line, font=fonts[0])
        cursorh += textHeight + padding
        print(textHeight)

    ttfontname = "SourceHanCodeJP.ttc"
    fontsize = 40
#    font = ImageFont.truetype(ttfontname, fontsize)
    textWidth, textHeight = draw.textsize('- ' + author.get('username') + "#" + author.get('discriminator'), font=fonts[1])
    draw.text(((note.width - textWidth) / 2, cursorh - 25), '- ' + author.get('username') + "#" + author.get('discriminator'), fill=textRGB,font=fonts[1])
    final.paste(note, (530, 0))

    return final


client.run(os.getenv("TOKEN"))