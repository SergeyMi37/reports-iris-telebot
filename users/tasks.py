"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import time
from typing import Union, List, Optional, Dict

import telegram

from dtb.celery import app
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import send_one_message, from_celery_entities_to_entities, \
    from_celery_markup_to_markup
from users.models import User
from tgbot.handlers.admin.servers_iris import command_server

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.4,
    parse_mode=telegram.ParseMode.HTML,
) -> None:
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{text}' to {len(user_ids)} users")

    entities_ = from_celery_entities_to_entities(entities)
    reply_markup_ = from_celery_markup_to_markup(reply_markup)
    for user_id in user_ids:
        try:
            send_one_message(
                user_id=user_id,
                text=text,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")

@app.task(ignore_result=True)
def broadcast_custom_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.4,
    parse_mode=telegram.ParseMode.HTML,
) -> None:
    """ Используется для трансляции сообщений большому количеству пользователей. """
    logger.info(f"Собираюсь отправить сообщение: '{text}' для {len(user_ids)} пользователейusers")

    entities_ = from_celery_entities_to_entities(entities)
    reply_markup_ = from_celery_markup_to_markup(reply_markup)
    print('--- user_ids ',type(user_ids),user_ids[0])
    res = ''
    if 'Condition(' in user_ids[0]: # Получение условия
        cond = user_ids[0].split('Condition(')[1].split(')')[0]
        res = command_server(cond)
        print('--== res =',res)
        if '<b>Err</b>' in res: # Нужно послать сообщение пользователям
            pass
        else:
            logger.info("Сообщение не послано пользователям")
            return
    if 'Roles(' in user_ids[0]: # Получение пользователей по ролям
        roles = user_ids[0].split('Roles(')[1].split(')')[0].split(",")
        print('--- Роли, которые должны быть у пользователей, которым посылать сообщения ',roles)
        _user_ids = list(User.objects.all().values_list('user_id', flat=True))
        for id in _user_ids:
            u = User.get_user_by_username_or_user_id(id)
            _roles = u.roles
            if _roles:
                _rol = _roles.split(",")
                if set(roles).intersection(_rol): # Пересечение списков ролей должно быть не пустым
                    if id not in user_ids:
                        user_ids.append(id)
    print('--==-',user_ids)
    for user_id in user_ids:
        try:
            if not isinstance(user_id, int):
                continue
            send_one_message(
                user_id=user_id,
                text=text + '\n' + res,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f"Широковещательное сообщение было отправлено {user_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение {user_id}, причина: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Трансляция завершена!")



