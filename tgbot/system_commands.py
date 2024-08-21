from typing import Dict

from telegram import Bot, BotCommand

from tgbot.main import bot


def set_up_commands(bot_instance: Bot) -> None:

    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'help': 'Help',
            'start': 'Start django bot 🚀',
            'stats': 'Statistics of bot 📊',
            'admin': 'Show admin info ℹ️',
            #'ask_location': 'Send location 📍',
            'broadcast': 'Broadcast message 📨',
            #'export_users': 'Export users.csv 👥',
        },
        'es': {
            'help': 'Help',
            'start': 'Iniciar el bot de django 🚀',
            'stats': 'Estadísticas de bot 📊',
            'admin': 'Mostrar información de administrador ℹ️',
            #'ask_location': 'Enviar ubicación 📍',
            'broadcast': 'Mensaje de difusión 📨',
            #'export_users': 'Exportar users.csv 👥',
        },
        'fr': {
            'help': 'Help',
            'start': 'Démarrer le bot Django 🚀',
            'stats': 'Statistiques du bot 📊',
            'admin': "Afficher les informations d'administrateur ℹ️",
            #'ask_location': 'Envoyer emplacement 📍',
            'broadcast': 'Message de diffusion 📨',
            #"export_users": 'Exporter users.csv 👥',
        },
        'ru': {
            'help': 'Помощь',
            'start': 'Запустить django бота 🚀',
            'stats': 'Статистика бота 📊',
            'admin': 'Показать информацию для админов ℹ️',
            'broadcast': 'Отправить сообщение 📨',
            #'ask_location': 'Отправить локацию 📍',
            #'export_users': 'Экспорт users.csv 👥',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


set_up_commands(bot)
