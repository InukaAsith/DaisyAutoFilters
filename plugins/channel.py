#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import re
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions

from bot import Bot
from config import AUTH_USERS, DOC_SEARCH, VID_SEARCH, MUSIC_SEARCH
from database.mdb import (
    savefiles,
    deletefiles,
    deletegroupcol,
    channelgroup,
    ifexists,
    deletealldetails,
    findgroupid,
    channeldetails,
    countfilters
)



@Client.on_message(filters.group & filters.command(["autofilter"]))
async def addchannel(client: Bot, message: Message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator":


        try:
            cmd, text = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<i>Please enter in the corrent manner!\n\n<code>/autofilter channelid</code>  or\n"
                "<code>/autofilter @channelusername</code></i>"
                "\n\nGet Channel id from @ShowJsonBot",
            )
            return
        try:
            if not text.startswith("@"):
                chid = int(text)
                if not len(text) == 14:
                    await message.reply_text(
                        "Enter valid channel ID"
                    )
                    return
            elif text.startswith("@"):
                chid = text
                if not len(chid) > 2:
                    await message.reply_text(
                        "Enter valid channel username"
                    )
                    return
        except Exception:
            await message.reply_text(
                "Enter a valid ID\n"
                "Correct syntax : <b>-100xxxxxxxxxx</b>\n"
                "Or use @Username of Channel",
            )
            return

        try:
            invitelink = await client.export_chat_invite_link(chid)
        except:
            await message.reply_text(
                "<b>Add me as admin of yor channel first</b>",
            )
            return

        try:
            user = await client.USER.get_me()
        except:
            user.first_name =  " "

        try:
            await client.USER.join_chat(invitelink)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            print(e)
            await message.reply_text(
                f"<b>User {user.first_name} couldn't join your channel! Make sure user is not banned in channel."
                "\n\nOr manually add the user to your channel and try again</b>",
            )
            return

        try:
            chatdetails = await client.USER.get_chat(chid)
        except:
            await message.reply_text(
                "<i>Send a message to your channel and try again</i>"
            )
            return

        intmsg = await message.reply_text(
            "<b>Please wait while I'm adding your channel files to DB"
            "\n\nTime may vary according to files present in the channel"
            "\nSay Hi to the support @DaisySupport_Official!!</b> \n"
        )

        channel_id = chatdetails.id
        channel_name = chatdetails.title
        group_id = message.chat.id
        group_name = message.chat.title

        already_added = await ifexists(channel_id, group_id)
        if already_added:
            await intmsg.edit_text("I'm already filtering it!")
            return

        docs = []

        if DOC_SEARCH == "yes":
            try:
                async for msg in client.USER.search_messages(channel_id,filter='document'):
                    try:
                        file_name = msg.document.file_name
                        file_id = msg.document.file_id                    
                        link = msg.link
                        data = {
                            '_id': file_id,
                            'channel_id' : channel_id,
                            'file_name': file_name,
                            'link': link
                        }
                        docs.append(data)
                    except:
                        pass
            except:
                pass

            await asyncio.sleep(5)

        if VID_SEARCH == "yes":
            try:
                async for msg in client.USER.search_messages(channel_id,filter='video'):
                    try:
                        file_name = msg.video.file_name
                        file_id = msg.video.file_id                    
                        link = msg.link
                        data = {
                            '_id': file_id,
                            'channel_id' : channel_id,
                            'file_name': file_name,
                            'link': link
                        }
                        docs.append(data)
                    except:
                        pass
            except:
                pass

            await asyncio.sleep(5)

        if MUSIC_SEARCH == "yes":
            try:
                async for msg in client.USER.search_messages(channel_id,filter='audio'):
                    try:
                        file_name = msg.audio.file_name
                        file_id = msg.audio.file_id                    
                        link = msg.link
                        data = {
                            '_id': file_id,
                            'channel_id' : channel_id,
                            'file_name': file_name,
                            'link': link
                        }
                        docs.append(data)
                    except:
                        pass
            except:
                pass

        if docs:
            await savefiles(docs, group_id)
        else:
            await intmsg.edit_text("Channel couldn't be added. Try after some time!")
            return

        await channelgroup(channel_id, channel_name, group_id, group_name)

        await intmsg.edit_text("Channel added successfully!")
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )

@Client.on_message(filters.group & filters.command(["autofilterdel"]))
async def deletechannelfilters(client: Bot, message: Message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator":
        try:
            cmd, text = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<i>Please enter in the corrent manner!\n\n<code>/autofilterdel channelid</code>  or\n"
                "<code>/autofilterdel @channelusername</code></i>"
                "\n\nrun /autofilterstats to see connected channels",
            )
            return
        try:
            if not text.startswith("@"):
                chid = int(text)
                if not len(text) == 14:
                    await message.reply_text(
                        "Enter valid channel ID\n\nrun /autofilterstats to see connected channels"
                    )
                    return
            elif text.startswith("@"):
                chid = text
                if not len(chid) > 2:
                    await message.reply_text(
                        "Enter valid channel username"
                    )
                    return
        except Exception:
            await message.reply_text(
                "Enter a valid ID\n"
                "run /autofilterstats to see connected channels\n"
                "Or enter channel @Username",
            )
            return

        try:
            chatdetails = await client.USER.get_chat(chid)
        except:
            await message.reply_text(
                "<b>User must be present in given channel.\n\n"
                "If user is already present, send a message to your channel and try again</b>"
            )
            return

        intmsg = await message.reply_text(
            "<b>Removing from Daisy's autofilter db"
            "\n\nSay Hi to the support @DaisySupport_Official!</i>"
        )

        channel_id = chatdetails.id
        channel_name = chatdetails.title
        group_id = message.chat.id
        group_name = message.chat.title

        already_added = await ifexists(channel_id, group_id)
        if not already_added:
            await intmsg.edit_text("That channel is not currently added in db!")
            return

        delete_files = await deletefiles(channel_id, channel_name, group_id, group_name)

        if delete_files:
            await intmsg.edit_text(
                "Channel deleted successfully!"
            )
        else:
            await intmsg.edit_text(
                "Couldn't delete Channel"
            )
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )

@Client.on_message(filters.group & filters.command(["autofilterdelall"]))
async def delallconfirm(client: Bot, message: Message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator":
        await message.reply_text(
            "Are you sure?? This will disconnect all connected channels and deletes all filters in group",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="YES",callback_data="delallconfirm")],
                [InlineKeyboardButton(text="CANCEL",callback_data="delallcancel")]
            ])
        )
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )

async def deleteallfilters(client: Bot, message: Message):

    intmsg = await message.reply_to_message.reply_text(
        "<i>Please wait while I'm deleteing your channel.</i>"
        "\n\nDon't give any other commands now!</i>"
    )

    group_id = message.reply_to_message.chat.id

    await deletealldetails(group_id)

    delete_all = await deletegroupcol(group_id)

    if delete_all == 0:
        await intmsg.edit_text(
            "All filters from group deleted successfully!"
        )
    elif delete_all == 1:
        await intmsg.edit_text(
            "Nothing to delete!!"
        )
    elif delete_all == 2:
        await intmsg.edit_text(
            "Couldn't delete filters. Try again after sometime.."
        )  


@Client.on_message(filters.group & filters.command(["autofilterstats"]))
async def stats(client: Bot, message: Message):
    if (client.get_chat_member(chat_id, (client.get_me()).id).status == "administrator"):         
        group_id = message.chat.id
        group_name = message.chat.title

        stats = f"Daisy's autofilter stats for {group_name}\n\n<b>Connected channels ;</b>"

        chdetails = await channeldetails(group_id)
        if chdetails:
            n = 0
            for eachdetail in chdetails:
                details = f"\n{n+1} : {eachdetail}"
                stats += details
                n = n + 1
        else:
            stats += "\nNo channels connected vro. Add one by /autofilter @Username!!"
            await message.reply_text(stats)
            return

        total = await countfilters(group_id)
        if total:
            stats += f"\n\n<b>Total number of autofilters</b> : {total}"

        await message.reply_text(stats)
    else:
        message.reply_text(
            " Sorry that cmd is only for Admins"
        )


@Client.on_message(filters.channel & (filters.document | filters.video | filters.audio))
async def addnewfiles(client: Bot, message: Message):

    media = message.document or message.video or message.audio

    channel_id = message.chat.id
    file_name = media.file_name
    file_id = media.file_id
    link = message.link

    docs = []
    data = {
        '_id': file_id,
        'channel_id' : channel_id,
        'file_name': file_name,
        'link': link
    }
    docs.append(data)

    groupids = await findgroupid(channel_id)
    if groupids:
        for group_id in groupids:
            await savefiles(docs, group_id)
