import dbdefs as rq
import openf1defs as f1rq
import sqlite3 as sq
from telebot import types
import telebot
from transitions import Machine


token='7344656967:AAEeM-tbuPa4y8jvZ3UmNcUoVF6jsRIRPhk'
bot=telebot.TeleBot(token)

states = ['start', 'my_team', 'myteam_choosing_1_driver', 'myteam_choosing_2_driver', 'myteam_choosing_3_driver', 
          'myteam_choosing_engine', 'myteam_choosing_pit', 'myteam_end_choosing', 'leaderboard', 'profile']

transitions = [
    {'trigger': 'myteam', 'source': 'start', 'dest': 'my_team'},
    {'trigger': 'choosing_1_driver', 'source': 'my_team', 'dest': 'myteam_choosing_1_driver'},
    {'trigger': 'choosing_2_driver', 'source': 'myteam_choosing_1_driver', 'dest': 'myteam_choosing_2_driver'},
    {'trigger': 'choosing_3_driver', 'source': 'myteam_choosing_2_driver', 'dest': 'myteam_choosing_3_driver'},
    {'trigger': 'choosing_engine', 'source': 'myteam_choosing_3_driver', 'dest': 'myteam_choosing_engine'},
    {'trigger': 'choosing_pit', 'source': 'myteam_choosing_engine', 'dest': 'myteam_choosing_pit'},
    {'trigger': 'end_choosing', 'source': 'myteam_choosing_pit', 'dest': 'myteam_end_choosing'},
    {'trigger': 'choosing_1_driver', 'source': 'myteam_end_choosing', 'dest': 'myteam_choosing_1_driver'},
    {'trigger': 'myteam', 'source': 'myteam_end_choosing', 'dest': 'my_team'},
    {'trigger': 'cancel', 'source': '*', 'dest': 'start'},
    {'trigger': 'leader_board', 'source': 'start', 'dest': 'leaderboard'},
    {'trigger': 'go_to_profile', 'source': 'start', 'dest': 'profile'},
]
class ChoosingTeam:
    pass
user = ChoosingTeam()
machine = Machine(user, states=states, transitions=transitions, initial='start')


def sql_start():
    global con, cur
    con = sq.connect("database.db")
    cur = con.cursor()
    if con:
        print("BASE IS OK")

@bot.message_handler(commands=['start'])
def start_message(message):
    user.cancel()
    bot.send_message(message.chat.id,f'Привет, {message.from_user.first_name}!')
    
    markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Моя команда")
    markup1.add(item1)
    item1=types.KeyboardButton("Таблица лидеров")
    markup1.add(item1)
    item1=types.KeyboardButton("Профиль")
    markup1.add(item1)
    bot.send_message(message.chat.id,'Выберите куда перейти:',reply_markup=markup1)
	
    rq.add_user(message.from_user.id, message.from_user.first_name)
	

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Моя команда":
        user.myteam()

    if message.text == "Таблица лидеров":
        user.leader_board()

    if message.text == "Профиль":
        user.go_to_profile()



    if user.state == 'my_team':
        if rq.add_team(message.from_user.id):
            markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Изменить")
            markup1.add(item1)
            item1=types.KeyboardButton("/start")
            markup1.add(item1)

            user.choosing_1_driver()

            team = rq.get_team(message.from_user.id)
            bot.send_message(message.chat.id, f"Твоя команда:\n  Первый пилот: {team[3]}\n  Второй пилот: {team[4]}\n  Третий пилот: {team[5]}\n  Двигатель от {team[6]}\n  Пит-стоп команда: {team[7]}\nСтоимость: ${team[2]}M",reply_markup=markup1)
        else:
            markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Создать")
            markup1.add(item1)
            user.choosing_1_driver()
            bot.send_message(message.chat.id,"У тебя нет команды.\nДавай её создадим!", reply_markup=markup1)
    
    elif user.state == 'myteam_choosing_1_driver':
        rq.set_cost_zero(message.from_user.id)

        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1,20):
            driver = rq.get_driver(i)
            item1 = types.KeyboardButton(f"{driver[0]} - ${driver[1]}M")
            markup1.add(item1)
        cost = rq.get_team_cost(message.from_user.id)
        bot.send_message(message.chat.id,f"Помни, что твоя команда не может стоить больше 60 млн и гонщики в ней не должны повторятся.\nУ вас осталось ${60-cost}M.")
        bot.send_message(message.chat.id,"Выбери первого пилота:", reply_markup=markup1)
        user.choosing_2_driver()

    elif user.state == 'myteam_choosing_2_driver':
        name = rq.get_name_from_msg(message.text)
        cost = rq.get_cost_from_msg(message.text)
        rq.change_1_driver(message.from_user.id, name, cost)

        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1,20):
            driver = rq.get_driver(i)
            item1 = types.KeyboardButton(f"{driver[0]} - ${driver[1]}M")
            markup1.add(item1)
        cost = rq.get_team_cost(message.from_user.id)
        bot.send_message(message.chat.id,f"Помни, что твоя команда не может стоить больше 60 млн и гонщики в ней не должны повторятся.\nУ вас осталось ${60-cost}M.")
        bot.send_message(message.chat.id,"Выбери второго пилота:", reply_markup=markup1)
        user.choosing_3_driver()

    elif user.state == 'myteam_choosing_3_driver':
        name = rq.get_name_from_msg(message.text)
        cost = rq.get_cost_from_msg(message.text)
        rq.change_2_driver(message.from_user.id, name, cost)

        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1,20):
            driver = rq.get_driver(i)
            item1 = types.KeyboardButton(f"{driver[0]} - ${driver[1]}M")
            markup1.add(item1)
        cost = rq.get_team_cost(message.from_user.id)
        bot.send_message(message.chat.id,f"Помни, что твоя команда не может стоить больше 60 млн и гонщики в ней не должны повторятся.\nУ вас осталось ${60-cost}M.")
        bot.send_message(message.chat.id,"Выбери третьего пилота:", reply_markup=markup1)
        user.choosing_engine()

    elif user.state == 'myteam_choosing_engine':
        name = rq.get_name_from_msg(message.text)
        cost = rq.get_cost_from_msg(message.text)
        rq.change_3_driver(message.from_user.id, name, cost)

        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1, 5):
            engine = rq.get_engine(i)
            item1 = types.KeyboardButton(f"{engine[0]} - ${engine[1]}M")
            markup1.add(item1)
        cost = rq.get_team_cost(message.from_user.id)
        bot.send_message(message.chat.id,f"Помни, что твоя команда не может стоить больше 60 млн и гонщики в ней не должны повторятся.\nУ вас осталось ${60-cost}M.")
        bot.send_message(message.chat.id,"Выбери двигатель:", reply_markup=markup1)
        user.choosing_pit()

    elif user.state == 'myteam_choosing_pit':
        name = rq.get_name_from_msg(message.text)
        cost = rq.get_cost_from_msg(message.text)
        rq.change_engine(message.from_user.id, name, cost)

        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1, 11):
            pit_team = rq.get_pit_team(i)
            item1 = types.KeyboardButton(f"{pit_team[0]} - ${pit_team[1]}M")
            markup1.add(item1)
        cost = rq.get_team_cost(message.from_user.id)
        bot.send_message(message.chat.id,f"Помни, что твоя команда не может стоить больше 60 млн и гонщики в ней не должны повторятся.\nУ вас осталось ${60-cost}M.")
        bot.send_message(message.chat.id,"Выбери пит-стоп команду:", reply_markup=markup1)
        user.end_choosing()

    elif user.state == 'myteam_end_choosing':
        name = rq.get_name_from_msg(message.text)
        cost = rq.get_cost_from_msg(message.text)
        rq.change_pit(message.from_user.id, name, cost)
        rq.check_team_composition(message.from_user.id)
        if rq.check_team_cost(message.from_user.id) and rq.check_team_composition(message.from_user.id):
            cost = rq.get_team_cost(message.from_user.id)
            rq.change_user_team_cost(message.from_user.id, cost)
            markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Назад")
            markup1.add(item1)
            bot.send_message(message.chat.id, "Готово!")
            bot.send_message(message.chat.id, 'Для возвращения в "Мою команду" нажми кнопку:', reply_markup=markup1)
            user.myteam()
        elif not rq.check_team_cost(message.from_user.id):
            markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Собрать заново")
            markup1.add(item1)
            bot.send_message(message.chat.id, 'Твоя команда стоит больше 60 млн.')
            bot.send_message(message.chat.id, 'Для того, чтобы её пересобрать нажми кнопку:', reply_markup=markup1)
            user.choosing_1_driver()
        elif not rq.check_team_composition(message.from_user.id):
            markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Собрать заново")
            markup1.add(item1)
            bot.send_message(message.chat.id, 'Некоторые гонщики в твоей команде повторяются.')
            bot.send_message(message.chat.id, 'Для того, чтобы пересобрать команду нажми кнопку:', reply_markup=markup1)
            user.choosing_1_driver()

    elif user.state == 'leaderboard':
        leaderboard = rq.get_leaderboard()
        s = "Таблица лидеров:\n"
        for x in leaderboard:
            s += str(rq.get_profile(x[0])[2]) + ": " + str(rq.get_profile(x[0])[3]) + '\n'
        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("/start")
        markup1.add(item1)
        bot.send_message(message.chat.id, s, reply_markup=markup1)
        
        
    elif user.state == 'profile':
        f1rq.count_user_points(message.from_user.id)

        profile = rq.get_profile(message.from_user.id)
        markup1=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("/start")
        markup1.add(item1)
        bot.send_message(message.chat.id, f"Твой профиль:\n  Имя: {profile[2]}\n  Набрано очков: {profile[3]}\n  Пройдено Гранд-при: {profile[4]}\n  Стоимость команды: {profile[5]}",reply_markup=markup1)


bot.infinity_polling()