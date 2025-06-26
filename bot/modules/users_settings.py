# bot/modules/users_settings.py

from aiofiles.os import remove
from nekozee.filters import (
    command,
    regex,
    user
)
from nekozee.handlers import (
    MessageHandler,
    CallbackQueryHandler
)
from os import (
    path as ospath,
    remove as osremove
)
from secrets import token_urlsafe
from time import time

from bot import (
    LOGGER,
    OWNER_ID,
    bot,
    bot_loop,
    bot_name,
    config_dict,
    shorteneres_list,
    user_data
)
from ..helper.ext_utils.bot_utils import (
    # get_template, # <<< ЭТА СТРОКА УДАЛЕНА
    new_task,
    sync_to_async,
    update_user_ldata,
)
from ..helper.ext_utils.db_handler import database
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.message_utils import (
    anno_checker,
    auto_delete_message,
    delete_message,
    edit_message,
    send_message,
)


@new_task
async def user_settings(_, message):
    from_user = message.from_user
    if not from_user:
        from_user = await anno_checker(message)
    user_id = from_user.id
    buttons = ButtonMaker()
    user_dict = user_data.get(user_id, {})
    thumb_path = f"Thumbnails/{user_id}.jpg"
    rclone_path = f"rclone/{user_id}.conf"
    buttons.data_button(
        "Leech",
        f"uset leech {user_id}"
    )
    buttons.data_button(
        "Mirror",
        f"uset mirror {user_id}"
    )
    if user_dict.get("yt_opt"):
        buttons.data_button(
            "YT-DLP Options",
            f"uset yt_opt {user_id}"
        )
    else:
        buttons.data_button(
            "YT-DLP Options",
            f"uset yt_opt {user_id}",
            "header"
        )
    thumb = "Exists" if await sync_to_async(
        ospath.exists,
        thumb_path
    ) else "Not Exists"
    buttons.data_button(
        f"Thumbnail: {thumb}",
        f"uset thumb {user_id}",
        "header"
    )
    rcc = (
        "Exists"
        if await sync_to_async(
            ospath.exists,
            rclone_path
        )
        else "Not Exists"
    )
    buttons.data_button(
        f"Rclone: {rcc}",
        f"uset rclone {user_id}",
        "header"
    )
    if shorteneres_list:
        shortener = (
            "Enabled"
            if user_dict.get("shortener")
            else "Disabled"
        )
        buttons.data_button(
            f"Shortener: {shortener}",
            f"uset shortener {user_id}",
            "header"
        )
    buttons.data_button(
        "Close",
        f"uset close {user_id}"
    )
    msg = f"<b>User Settings for {from_user.mention}</b>"
    if user_id != OWNER_ID and user_data.get(user_id):
        user_time = user_dict.get("time")
        if user_time:
            exp_time = (
                (user_time - time())
                / 86400
            )
            msg += f"\n\n<b>Your Subscription will expire in <i>{exp_time:.2f}</i> day(s).</b>"
    text = msg
    await send_message(
        message,
        text,
        buttons.build_menu(2)
    )


async def leech_set(query, user_id):
    buttons = ButtonMaker()
    user_dict = user_data.get(user_id, {})
    u_as_doc = (
        "Enabled"
        if user_dict.get(
            "as_doc",
            False
        )
        else "Disabled"
    )
    u_as_med = (
        "Enabled"
        if user_dict.get(
            "as_media",
            False
        )
        else "Disabled"
    )
    u_equal_splits = "Enabled" if user_dict.get("equal_splits") else "Disabled"
    u_media_group = "Enabled" if user_dict.get("media_group") else "Disabled"
    u_leech_split_size = (
        f"{user_dict.get('split_size')}GB"
        if user_dict.get("split_size")
        else "Default"
    )
    u_mixed_leech = "Enabled" if user_dict.get("mixed_leech") else "Disabled"
    u_leech_dest = "Not Exists" if not user_dict.get("leech_dest") else "Exists"
    u_leech_prefix = (
        "Exists" if user_dict.get("lprefix") else "Not Exists"
    )
    u_leech_suffix = (
        "Exists" if user_dict.get("lsuffix") else "Not Exists"
    )
    u_leech_caption = (
        "Enabled"
        if user_dict.get(
            "leech_caption",
            False
        )
        else "Disabled"
    )
    u_leech_thumb = (
        "Exists"
        if user_dict.get(
            "thumb",
            False
        )
        else "Not Exists"
    )
    u_leech_dump = (
        "Exists"
        if user_dict.get(
            "dump",
            False
        )
        else "Not Exists"
    )
    u_leech_cap_font = (
        user_dict.get("lcapfont")
        if user_dict.get("lcapfont")
        else "Default"
    )
    u_leech_sample_video = (
        f'{user_dict.get("sv_ss")}s'
        if user_dict.get(
            "sv_ss",
            False
        )
        else "Disabled"
    )
    u_leech_screenshots = (
        f'{user_dict.get("ss")} no.'
        if user_dict.get(
            "ss",
            False
        )
        else "Disabled"
    )
    u_convert_audio = (
        user_dict.get("ca")
        if user_dict.get(
            "ca",
            False
        )
        else "Disabled"
    )
    u_convert_video = (
        user_dict.get("cv")
        if user_dict.get(
            "cv",
            False
        )
        else "Disabled"
    )
    u_name_sub = (
        user_dict.get("ns")
        if user_dict.get(
            "ns",
            False
        )
        else "Disabled"
    )

    buttons.data_button(
        f"AS DOC: {u_as_doc}",
        f"uset as_doc {user_id}"
    )
    buttons.data_button(
        f"AS MEDIA: {u_as_med}",
        f"uset as_media {user_id}"
    )
    buttons.data_button(
        f"Equal Splits: {u_equal_splits}",
        f"uset equal_splits {user_id}"
    )
    buttons.data_button(
        f"Media Group: {u_media_group}",
        f"uset media_group {user_id}"
    )
    buttons.data_button(
        f"Leech Caption: {u_leech_caption}",
        f"uset leech_caption {user_id}"
    )
    buttons.data_button(
        f"Split Size: {u_leech_split_size}",
        f"uset split_size {user_id}"
    )
    buttons.data_button(
        f"Leech Prefix: {u_leech_prefix}",
        f"uset lprefix {user_id}"
    )
    buttons.data_button(
        f"Leech Suffix: {u_leech_suffix}",
        f"uset lsuffix {user_id}"
    )
    buttons.data_button(
        f"Caption Font: {u_leech_cap_font}",
        f"uset lcapfont {user_id}"
    )
    buttons.data_button(
        f"Thumbnail: {u_leech_thumb}",
        f"uset thumb {user_id}"
    )
    buttons.data_button(
        "Leech Destination",
        f"uset leech_dest {user_id}"
    )
    buttons.data_button(
        f"Mixed Leech: {u_mixed_leech}",
        f"uset mixed_leech {user_id}"
    )
    buttons.data_button(
        f"Sample Video: {u_leech_sample_video}",
        f"uset sv_ss {user_id}"
    )
    buttons.data_button(
        f"Screenshots: {u_leech_screenshots}",
        f"uset ss {user_id}"
    )
    buttons.data_button(
        f"Convert Audio: {u_convert_audio}",
        f"uset ca {user_id}"
    )
    buttons.data_button(
        f"Convert Video: {u_convert_video}",
        f"uset cv {user_id}"
    )
    buttons.data_button(
        f"Name Substitute: {u_name_sub}",
        f"uset ns {user_id}"
    )
    buttons.data_button(
        "Back",
        f"uset back {user_id}",
        "footer"
    )
    buttons.data_button(
        "Close",
        f"uset close {user_id}",
        "footer"
    )
    await edit_message(
        query.message,
        "Leech Settings:",
        buttons.build_menu(2)
    )


async def mirror_set(query, user_id):
    buttons = ButtonMaker()
    user_dict = user_data.get(user_id, {})
    m_rem = "Exists" if user_dict.get("m_remname") else "Not Exists"
    m_suf = "Exists" if user_dict.get("m_suffix") else "Not Exists"
    m_pre = "Exists" if user_dict.get("m_prefix") else "Not Exists"
    m_rcc = (
        "Exists" if await sync_to_async(
            ospath.exists,
            f"rclone/{user_id}.conf"
        ) else "Not Exists"
    )
    m_gdid = (
        "Exists"
        if user_dict.get("gdrive_id")
        else "Not Exists"
    )
    m_index = (
        "Exists"
        if user_dict.get("index_url")
        else "Not Exists"
    )
    buttons.data_button(
        f"Rclone: {m_rcc}",
        f"uset rclone {user_id}"
    )
    buttons.data_button(
        f"Gdrive ID: {m_gdid}",
        f"uset gdrive_id {user_id}"
    )
    buttons.data_button(
        f"Index URL: {m_index}",
        f"uset index {user_id}"
    )
    buttons.data_button(
        f"Mirror Prefix: {m_pre}",
        f"uset m_prefix {user_id}"
    )
    buttons.data_button(
        f"Mirror Suffix: {m_suf}",
        f"uset m_suffix {user_id}"
    )
    buttons.data_button(
        f"Remname: {m_rem}",
        f"uset m_remname {user_id}"
    )
    buttons.data_button(
        "Back",
        f"uset back {user_id}",
        "footer"
    )
    buttons.data_button(
        "Close",
        f"uset close {user_id}",
        "footer"
    )
    await edit_message(
        query.message,
        "Mirror Settings:",
        buttons.build_menu(2)
    )


@new_task
async def edit_user_settings(client, query):
    from_user = query.from_user
    user_id = from_user.id
    message = query.message
    data = query.data.split()
    if user_id != int(data[-1]):
        await query.answer(
            "Not Yours!",
            show_alert=True
        )
    elif data[1] == "leech":
        await query.answer()
        await leech_set(
            query,
            user_id
        )
    elif data[1] == "mirror":
        await query.answer()
        await mirror_set(
            query,
            user_id
        )
    elif data[1] in [
        "as_doc",
        "as_media",
        "equal_splits",
        "media_group",
        "mixed_leech",
        "leech_caption",
    ]:
        await query.answer()
        update_user_ldata(
            user_id,
            data[1],
            not user_data.get(
                user_id,
                {}
            ).get(
                data[1],
                False
            )
        )
        await leech_set(
            query,
            user_id
        )
    elif data[1] == "shortener":
        await query.answer()
        update_user_ldata(
            user_id,
            "shortener",
            not user_data.get(
                user_id,
                {}
            ).get("shortener")
        )
        await user_settings(
            client,
            message
        )
    elif data[1] == "thumb":
        await query.answer()
        update_user_ldata(
            user_id,
            "thumb",
            not user_data.get(
                user_id,
                {}
            ).get("thumb")
        )
        await user_settings(
            client,
            message
        )
        thumb_path = f"Thumbnails/{user_id}.jpg"
        if await sync_to_async(
            ospath.exists,
            thumb_path
        ):
            await remove(thumb_path)
    elif data[1] == "yt_opt":
        await query.answer()
        update_user_ldata(
            user_id,
            "yt_opt",
            not user_data.get(
                user_id,
                {}
            ).get("yt_opt")
        )
        await user_settings(
            client,
            message
        )
    elif data[1] == "back":
        await query.answer()
        await user_settings(
            client,
            message
        )
    elif data[1] == "close":
        await query.answer()
        await delete_message(message)
    if config_dict["DATABASE_URL"]:
        await database.update_user_data(user_id)


async def send_users_settings(_, message):
    text = message.text.split()
    if len(text) > 1:
        user_id = int(text[1])
        if user_data.get(user_id):
            user_dict = user_data[user_id]
        else:
            await message.reply(
                "No data found for this user",
                quote=True
            )
            return
    else:
        user_id = message.from_user.id
        user_dict = user_data.get(
            user_id,
            {}
        )
    msg = f"<b>Settings for user:</b> <code>{user_id}</code>\n"
    if (st := user_dict.get("shortener_api")) and (sh := user_dict.get("shortener")):
        msg += f"\n<b>Shortener:</b> {sh}"
        msg += f"\n<b>Shortener API:</b> <code>{st}</code>"
    if nsfw := user_dict.get("nsfw"):
        msg += f"\n<b>NSFW Allowed:</b> {nsfw}"
    if uti := user_dict.get("user_token_id"):
        msg += f"\n<b>User Token ID:</b> <code>{uti}</code>"
    if rcc := user_dict.get("rclone"):
        msg += f"\n<b>Rclone:</b> {rcc}"
    if gdid := user_dict.get("gdrive_id"):
        msg += f"\n<b>Gdrive ID:</b> <code>{gdid}</code>"
    if index := user_dict.get("index_url"):
        msg += f"\n<b>Index URL:</b> <code>{index}</code>"
    if user_dict.get("yt_opt"):
        msg += f"\n<b>YT-DLP Options:</b> <code>{user_dict.get('yt_opt')}</code>"
    if asdoc := user_dict.get("as_doc"):
        msg += f"\n<b>Leech as Document:</b> {asdoc}"
    if asmedia := user_dict.get("as_media"):
        msg += f"\n<b>Leech as Media:</b> {asmedia}"
    if esplt := user_dict.get("equal_splits"):
        msg += f"\n<b>Equal Splits:</b> {esplt}"
    if mgrp := user_dict.get("media_group"):
        msg += f"\n<b>Media Group:</b> {mgrp}"
    if ssv := user_dict.get("sv_ss"):
        msg += f"\n<b>Sample Video:</b> {ssv}"
    if ss := user_dict.get("ss"):
        msg += f"\n<b>Screenshots:</b> {ss}"
    if ml := user_dict.get("mixed_leech"):
        msg += f"\n<b>Mixed Leech:</b> {ml}"
    if ldest := user_dict.get("leech_dest"):
        msg += f"\n<b>Leech Destination:</b> {ldest}"
    if lpre := user_dict.get("lprefix"):
        msg += f"\n<b>Leech Prefix:</b> {lpre}"
    if lsuf := user_dict.get("lsuffix"):
        msg += f"\n<b>Leech Suffix:</b> {lsuf}"
    if lcfont := user_dict.get("lcapfont"):
        msg += f"\n<b>Leech Caption Font:</b> {lcfont}"
    if ca := user_dict.get("ca"):
        msg += f"\n<b>Convert Audio:</b> {ca}"
    if cv := user_dict.get("cv"):
        msg += f"\n<b>Convert Video:</b> {cv}"
    if lcap := user_dict.get("leech_caption"):
        msg += f"\n<b>Leech Caption:</b> {lcap}"
    if ldump := user_dict.get("dump"):
        msg += f"\n<b>Leech Dump:</b> {ldump}"
    if lthumb := user_dict.get("thumb"):
        msg += f"\n<b>Leech Thumbnail:</b> {lthumb}"
    if mpre := user_dict.get("m_prefix"):
        msg += f"\n<b>Mirror Prefix:</b> {mpre}"
    if msuf := user_dict.get("m_suffix"):
        msg += f"\n<b>Mirror Suffix:</b> {msuf}"
    if mrem := user_dict.get("m_remname"):
        msg += f"\n<b>Mirror Remname:</b> {mrem}"
    await send_message(
        message,
        msg
    )


bot.add_handler( # type: ignore
    MessageHandler(
        user_settings,
        filters=command(
            BotCommands.UserSetCommand,
            case_sensitive=True
        ) & CustomFilters.authorized
    )
)
bot.add_handler( # type: ignore
    MessageHandler(
        send_users_settings,
        filters=command(
            BotCommands.UsersCommand,
            case_sensitive=True
        ) & CustomFilters.sudo,
    )
)
bot.add_handler( # type: ignore
    CallbackQueryHandler(
        edit_user_settings,
        filters=regex("^uset")
    )
)
