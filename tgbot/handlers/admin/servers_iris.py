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

import requests
import json
from tgbot.handlers.admin import static_text
from openpyxl import Workbook

url = os.getenv('url_test20203')
for key in os.environ:
    print(key, '=>', os.environ[key])

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
    #lab = "Рейтинг" if upms.text=='/daily_rating_noname' else 'ВПР'
    #put_report(update=update, fromDate=fromDate,label=labels,mode="noname")
    upms.reply_text(
            text='!!!',
        )

def get_open_issues(url: str,
                    labels: str = 'Табель',
                    scope: str = 'all',
                    state: str = 'opened',
                    due_date: str = 'month') -> tuple[int, Any]:
  ret=""
  errno = "code.CODE_GITLAB_GET_ISSUE_OK"
  _url='{0:s}?labels={1:s}&scope={2:s}&state={3:s}&due_date={4:s}&per_page=100'.format(GITLAB_URL, labels, scope, state, due_date)
  headers = {
        #'Authorization': 'Bearer {0:s}'.format(ACCESS_TOKEN),
        'PRIVATE-TOKEN': ACCESS_TOKEN,
        'Accept': 'application/json;odata=verbose'
        }
  #print('---',_url,headers)
  try:
      response = requests.get(_url,verify=False,headers=headers)
      if response.status_code == 200:
        answer = json.loads(response.text)
        return "code.CODE_GITLAB_GET_ISSUE_OK", answer
      elif response.status_code == 404:
        return "code.CODE_GITLAB_ISSUE_EMPTY", None
      else:
        errno = "code.CODE_GITLAB_GET_ISSUE_FAIL"
        answer = {
          "errno": errno,
          'err_message': '{0:s}:{1:s}'.format(errno, response.text)
        }
        raise Exception(answer.get('err_message'))
  except Exception as e:
    errno = "code.CODE_GITLAB_GET_ISSUE_FAIL"
    answer = {
      "errno": errno,
      'err_message': '{0}:{1}'.format(errno, e.args.__repr__())
    }
    return errno, answer


def put_report(update: Update, label: str = "", fromDate: datetime="", toDate: datetime="", mode: str='name'):

    #txt, pref, week = get_report(fromDate=fromDate,toDate=toDate,label=label,mode=mode)
    telecmd, upms = get_tele_command(update)
    CONST = 4090
    ot=0
    do=CONST
    
    if mode == 'weekly':
      text = pref +BR+ "<b>Недельная сводка</b>" + BR + BR
      for key in week:
         text += key + BR + BR
    else:
      text = pref +BR+ txt 

    media_dir = Path(__file__).resolve().parent.parent.parent.parent.joinpath('downloads')
    if not os.path.exists(media_dir):
      os.mkdir(media_dir)
    # Вывод в файл XLSX -----------------------------------------
    if mode=='xlsx':
      wb = Workbook() # creates a workbook object.
      ws = wb.active # creates a worksheet object.
      #_out=[[f"{pref}"],["Дата","ФИО", "Дата UTC", "Мероприятия"]]
      outlist = text.split(BR)
      #ws.append([f"{pref}"])
      ws.append([f"{outlist[2]}"])
      
      ws.append(["Дата","ФИО", "Дата UTC", "Мероприятия"])
      head = ""
      for row in outlist[3:-1]:
        if row !='':
          if head=="":
             head=row
             continue
          else:
            ws.append([f'{head.split(" ")[1]}',f'{head.split(" ")[0]}',f'{head.split(" ")[2]}',row])
            head=""

      ws.column_dimensions.__getitem__("A").width = "15"
      ws.column_dimensions.__getitem__("B").width = "20"
      ws.column_dimensions.__getitem__("C").width = "20"
      ws.column_dimensions.__getitem__("D").width = "90"
      ws.freeze_panes="B3"
      _file = os.path.join(media_dir, f'{telecmd[1:-1]}_{upms.chat.id}.xlsx')
      wb.save(_file) # save to excel file.
      upms.reply_document(open(_file, 'rb'))
    
    # Вывод в текстовый файл -----------------------------------------
    elif mode=='txt':
      lines = text.split(BR)
      _file = os.path.join(media_dir, f'{telecmd[1:-1]}_{upms.chat.id}.txt')
      with open(_file, "w") as file:
        for  line in lines:
          if line !='':
            file.write(line + '\n')
      upms.reply_document(open(_file, 'rb'))
      #for row in txt.split(BR):
      #  print(row)

    # вывод в цикле текстом  -----------------------------------------
    else:
      while True:
        upms.reply_text(
          text = text[ot:do],
          parse_mode=ParseMode.HTML,
          disable_web_page_preview=True,
          )
        ot=ot+CONST
        do=do+CONST
        if text[ot:do]=='':
          break
    
