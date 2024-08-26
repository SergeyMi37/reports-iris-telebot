#from datetime import timedelta

from django.utils.timezone import now
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.decorators import admin_only, send_typing_action
from tgbot.handlers.utils.date_utils import tz_to_moscow
from users.models import User
from tgbot.handlers.admin.static_text import BR
import os
from pathlib import Path
from typing import Any
#import datetime
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
import json
from tgbot.handlers.admin import static_text
from openpyxl import Workbook

def get_tele_command(update: Update) -> str:
   #print('---update:---',update)
   try:
      if update.message.text:
         return update.message.text, update.message
      else:
         return update.edited_message.text, update.message
   except Exception as err:
      #print("---err-get_tele_command-",err)
      return update.edited_message.text, update.edited_message

def command_servers(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    telecmd, upms = get_tele_command(update)
    #url = os.getenv('url_test20203')
    result=''
    for key in os.environ:
      if "URL_" in key:
        print(key, '=>', os.environ[key])
        #result += key.split("URL_")[1]
        #Загрузить из сервиса результат
        err, resp = get_open(os.environ[key])
        print(err, resp)
        icon = "😌" if err.find("_OK")!=-1 else "😡"
        result += icon + " /server_" + key.split("URL_")[1] + " " + err.split("_")[2] + BR
    upms.reply_text(
            text=result,
        )


def get_open(url: str
        ) -> tuple[int, Any]:

  o = urlparse(url)
  #print('---',o.netloc,o.username,o.password)

  errno = "code.CODE_GET_OK"
  headers = {
        'Accept': 'application/json;odata=verbose',
        }
  auth=(o.username,o.password)
  _host = o.netloc if o.netloc.find("@")==-1  else  o.netloc.split("@")[-1] #Если не включает @, то взять всю строку, если нет, то Последнее поле по @
  _url = f'{o.scheme}://{_host}{o.path}'
  print(_url,auth)
  try:
      response = requests.get(_url,verify=False,headers=headers,timeout=1,auth=auth)
      if response.status_code == 200:
        answer = json.loads(response.text)
        return "code.CODE_GET_OK", answer
      elif response.status_code == 404:
        return "code.CODE_GET_EMPTY", None
      else:
        errno = "code.CODE_GET_FAIL"
        answer = {
          "errno": errno,
          'err_message': '{0:s}:{1:s}'.format(errno, response.text)
        }
        raise Exception(answer.get('err_message'))
  except Exception as e:
    errno = "code.CODE_GET_FAIL"
    answer = {
      "errno": errno,
      'err_message': '{0}:{1}'.format(errno, e.args.__repr__())
    }
    return errno, answer

