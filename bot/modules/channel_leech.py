from asyncio import sleep
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, PeerIdInvalid

# Импортируем основного бота, user-сессию и логгер
from bot import bot, user, LOGGER, DOWNLOAD_DIR, task_dict, task_dict_lock
# Импортируем наш listener и хелперы
from bot.modules.mirror_leech import Mirror
from bot.helper.task_utils.download_utils.telegram_download import TelegramDownloadHelper
# Вспомогательные утилиты бота
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import send_message
# Импортируем обработчики для регистрации команд
from nekozee.filters import command
from nekozee.handlers import MessageHandler

# Глобальный словарь для управления активными задачами парсинга {user_id: boolean}
channel_leech_tasks = {}

async def _initiate_task_for_msg(user_cmd_msg, target_msg):
    """
    Создает и запускает ОДНУ задачу для ОДНОГО сообщения.
    """
    listener = Mirror(client=user_cmd_msg._client, message=user_cmd_msg, is_leech=True)
    await listener.get_id()
    await listener.get_tag(user_cmd_msg.text.split('\n'))
    
    # Отключаем все лишние операции, чтобы просто скачать-загрузить
    listener.split_size = 0
    listener.compress = False
    listener.extract = False
    listener.join = False

    # Передаем управление в TelegramDownloadHelper
    path = f"{DOWNLOAD_DIR}{listener.mid}/"
    helper = TelegramDownloadHelper(listener)
    await helper.add_download(target_msg, path, "user")


@new_task
async def channelleech(client, message):
    user_id = message.from_user.id
    if channel_leech_tasks.get(user_id):
        await send_message(message, "У вас уже запущен парсинг. Остановите его: /stopchannelleech")
        return

    args = message.text.split()
    if len(args) < 2:
        await send_message(message, f"<b>Использование:</b> <code>/{BotCommands.ChannelLeechCommand[0]} <ID/@username> [ID стартового сообщения]</code>")
        return

    try:
        channel_id_str = args[1]
        start_message_id = int(args[2]) if len(args) > 2 else 1

        try:
            if channel_id_str.startswith(("-", "@")):
                if channel_id_str.startswith('@'):
                    chat = await user.get_chat(channel_id_str)
                    channel_id = chat.id
                else:
                    channel_id = int(channel_id_str)
            else:
                await send_message(message, "Неверный формат ID/Username. Он должен начинаться с @ или -100.")
                return
        except Exception as e:
            await send_message(message, f"Не могу найти канал/группу: {e}")
            return
            
        status_msg = await send_message(message, "Подготовка...")
        channel_leech_tasks[user_id] = True

        await status_msg.edit_text(f"<b>Этап 1/2:</b> Сбор ID сообщений из <code>{channel_id}</code>. Это может занять время...")
        message_ids = []
        try:
            total_count = await user.get_chat_history_count(channel_id)
            async for msg in user.get_chat_history(channel_id):
                if not channel_leech_tasks.get(user_id): break
                message_ids.append(msg.id)
                if len(message_ids) % 2000 == 0:
                     await status_msg.edit_text(f"<b>Этап 1/2:</b> Собрано {len(message_ids)} из ~{total_count} ID...")
        except FloodWait as fw:
            await sleep(fw.value + 5)
        
        if not channel_leech_tasks.get(user_id):
            await status_msg.edit_text("Парсинг остановлен на этапе сбора ID.")
            return

        message_ids.reverse()

        if start_message_id > 1:
            try:
                start_index = message_ids.index(start_message_id)
                message_ids = message_ids[start_index:]
            except ValueError:
                await status_msg.edit_text(f"Стартовый ID <code>{start_message_id}</code> не найден.")
                channel_leech_tasks[user_id] = False
                return

        await status_msg.edit_text(f"<b>Этап 2/2:</b> Начинаю обработку {len(message_ids)} постов. Для остановки: /stopchannelleech")
        
        processed_media_groups = set()
        
        for msg_id in message_ids:
            if not channel_leech_tasks.get(user_id):
                await status_msg.edit_text("Парсинг остановлен.")
                break

            try:
                single_message = await user.get_messages(channel_id, msg_id)
                if not single_message: continue

                media_group_id = getattr(single_message, 'media_group_id', None)
                
                # Если это медиа-группа
                if media_group_id:
                    if media_group_id in processed_media_groups:
                        continue
                    processed_media_groups.add(media_group_id)
                    
                    media_group_msgs = await user.get_media_group(channel_id, single_message.id)
                    
                    # Создаем одну общую задачу для всего альбома
                    listener = Mirror(client=message._client, message=message, is_leech=True)
                    await listener.get_id()
                    await listener.get_tag(message.text.split('\n'))
                    listener.split_size = 0 # Отключаем нарезку

                    # Скачиваем все файлы из альбома ПОСЛЕДОВАТЕЛЬНО в одну папку
                    for item_msg in media_group_msgs:
                         if not channel_leech_tasks.get(user_id): break
                         dl_helper = TelegramDownloadHelper(listener)
                         path = f"{DOWNLOAD_DIR}{listener.mid}/"
                         # Важно: мы не используем await здесь, чтобы не блокировать,
                         # но логика внутри add_download сама ждет завершения.
                         # Мы добавляем их в очередь существующей системы.
                         await dl_helper.add_download(item_msg, path, "user")
                         # Ждем пока задача не появится в словаре активных
                         while listener.mid not in task_dict: await sleep(0.5)
                         # Ждем пока задача не завершится
                         while listener.mid in task_dict: await sleep(1)

                # Если это одиночное сообщение
                elif single_message.media:
                    await _initiate_task_for_msg(message, single_message)

                await sleep(2) # Задержка между постами
            
            except FloodWait as fw:
                await sleep(fw.value + 5)
            except Exception as e:
                LOGGER.error(f"Ошибка при обработке сообщения {msg_id}: {e}")
                await sleep(2)

        if channel_leech_tasks.get(user_id):
            await status_msg.edit_text(f"✅ Парсинг канала <code>{channel_id}</code> завершен.")
        
    except Exception as e:
        LOGGER.error(f"Критическая ошибка в Channel Leech: {e}")
        await message.reply(f"Критическая ошибка: {e}")
    finally:
        channel_leech_tasks[user_id] = False


@new_task
async def stopchannelleech(client, message):
    user_id = message.from_user.id
    if channel_leech_tasks.get(user_id):
        channel_leech_tasks[user_id] = False
        await send_message(message, "Команда на остановку отправлена. Процесс остановится после текущего поста.")
    else:
        await send_message(message, "Нет активных задач для остановки.")

bot.add_handler(MessageHandler(channelleech, filters=command(BotCommands.ChannelLeechCommand) & CustomFilters.authorized))
bot.add_handler(MessageHandler(stopchannelleech, filters=command(BotCommands.StopChannelLeechCommand) & CustomFilters.authorized))
