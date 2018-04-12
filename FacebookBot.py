from facepy import GraphAPI
from settings import token, start_msg, client_file, token_file
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
import os
import sys
import telepot

# State for user
user_state = {}
privacy = {}
caption = {}

menu = [
    ["Testo", "Foto", "Video"]
]

choose = {
    "Tutti": "EVERYONE", "Solo amici": "ALL_FRIENDS",
    "Amici di amici": "FRIENDS_OF_FRIENDS", "Personalizzato": "CUSTOM",
    "Solo io": "SELF"
}

menu1 = [
    ["Tutti", "Solo amici"],
    ["Amici di amici", "Personalizzato"],
    ["Solo io"]
]

markup = ReplyKeyboardMarkup(keyboard=menu)
markup1 = ReplyKeyboardMarkup(keyboard=menu1)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Check user state
    try:
        user_state[chat_id] = user_state[chat_id]
    except:
        user_state[chat_id] = 0

    # start command
    if content_type == 'text' and msg['text'] == '/start':
        if register_user(chat_id):
            bot.sendMessage(chat_id, start_msg, parse_mode='Markdown')
            msg['text'] = '/token'

    if content_type == 'text' and msg['text'] == '/token':
        bot.sendMessage(
            chat_id, "Inserisci il tuo token\nPer generare il token clicca [qui](https://developers.facebook.com/tools/explorer/145634995501895/)",  parse_mode='Markdown')
        bot.sendPhoto(chat_id, 'https://github.com/Fast0n/FacebookBot/raw/master/img/sample_token.png')
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        register_token_user(chat_id, msg['text'])
        user_state[chat_id] = 0

    if content_type == 'text' and msg['text'] == '/publish':
        f = open(token_file, "r")
        for user in f.readlines():
            if user.replace('\n', '').split(":")[0] == str(chat_id):
                try:
                    graph = GraphAPI(user.replace('\n', '').split(":")[1])
                    graph.get('me/posts')
                    bot.sendMessage(
                        chat_id, "Seleziona la privacy", reply_markup=markup1)
                    user_state[chat_id] = 2
                except:
                    bot.sendMessage(chat_id, "Token errato ❌")
                    user_state[chat_id] = 0

    elif user_state[chat_id] == 2:
        privacy[chat_id] = choose[msg['text']]
        msg = "Seleziona un campo"
        bot.sendMessage(chat_id, msg, reply_markup=markup)
        user_state[chat_id] = 3

    elif user_state[chat_id] == 3:
        if msg['text'] in menu[0]:
            if content_type == 'text' and msg['text'] == 'Testo':
                bot.sendMessage(chat_id, "Inserisci il testo",
                                reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                user_state[chat_id] = 4

            elif content_type == 'text' and msg['text'] == 'Foto':
                bot.sendMessage(chat_id, "Inserisci caption (Opzionale)[Se non vuoi scrivere niente, scrivi null]", reply_markup=ReplyKeyboardRemove(
                    remove_keyboard=True))
                user_state[chat_id] = 5

            elif content_type == 'text' and msg['text'] == 'Video':
                bot.sendMessage(chat_id, "Inserisci caption (Opzionale)[Se non vuoi scrivere niente, scrivi null]", reply_markup=ReplyKeyboardRemove(
                    remove_keyboard=True))
                user_state[chat_id] = 6

    elif user_state[chat_id] == 5:
        if msg['text'].lower() == 'null':
            caption[chat_id] = ''
        else:
            caption[chat_id] = msg['text']
        bot.sendMessage(chat_id, "Invia una foto")
        user_state[chat_id] = 7

    elif user_state[chat_id] == 6:
        if msg['text'].lower() == 'null':
            caption[chat_id] = ''
        else:
            caption[chat_id] = msg['text']
        bot.sendMessage(chat_id, "Invia un video")
        user_state[chat_id] = 8

    elif user_state[chat_id] == 4:
        f = open(token_file, "r")
        for user in f.readlines():
            if user.replace('\n', '').split(":")[0] == str(chat_id):
                try:
                    graph = GraphAPI(user.replace('\n', '').split(":")[1])
                    graph.post(
                        path='me/feed',
                        message=msg['text'],
                        privacy={"value": privacy[chat_id]},
                        retry=0
                    )
                    bot.sendMessage(chat_id, "Operazione completata ✔️")
                except:
                    bot.sendMessage(chat_id, "Token errato ❌")
                user_state[chat_id] = 0

    elif user_state[chat_id] == 7:
        f = open(token_file, "r")
        for user in f.readlines():
            if user.replace('\n', '').split(":")[0] == str(chat_id):
                try:
                    try:
                        # estrae il nome dell'immagine inviata
                        name = msg['photo'][0]['file_path']
                        name = name.replace("photos/", "")
                        # estrae l'id dell'immagine inviata
                        photo = msg['photo'][-1]['file_id']
                    except KeyError:
                        # estrae il nome dell'immagine inviata
                        name = "__pycache__/" + str(chat_id) + "_tmp.jpg"
                        # estrae l'id dell'immagine inviata
                        photo = msg['photo'][-1]['file_id']

                    bot.download_file(photo, './' + name)

                    try:
                        graph = GraphAPI(user.replace('\n', '').split(":")[1])
                        graph.post(
                            caption=caption[chat_id],
                            path='me/photos',
                            privacy={"value": privacy[chat_id]},
                            source=open(name, 'rb')
                        )
                        bot.sendMessage(chat_id, "Operazione completata ✔️")
                        user_state[chat_id] = 0
                    except:
                        bot.sendMessage(chat_id, "Token errato ❌")
                        user_state[chat_id] = 0

                except:
                    bot.sendMessage(chat_id, "Solo foto, riprova...")

    elif user_state[chat_id] == 8:
        f = open(token_file, "r")
        for user in f.readlines():
            if user.replace('\n', '').split(":")[0] == str(chat_id):
                try:
                    name = "__pycache__/" + str(chat_id) + "_tmp.mp4"
                    # estrae il video inviata
                    video = msg['video']['file_id']
                    bot.download_file(video, './' + name)
                    try:
                        graph = GraphAPI(user.replace('\n', '').split(":")[1])
                        graph.post(
                            caption=caption[chat_id],
                            path='me/videos',
                            privacy={"value": privacy[chat_id]},
                            source=open(name, 'rb')
                        )
                        bot.sendMessage(chat_id, "Operazione completata ✔️")
                        user_state[chat_id] = 0
                    except:
                        bot.sendMessage(chat_id, "Token errato ❌")
                        user_state[chat_id] = 0
                except:
                    bot.sendMessage(chat_id, "Solo video, riprova...")

    # donate command
    if content_type == 'text' and msg['text'] == '/dona':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Dona", url='https://paypal.me/Fast0n/')],
        ])
        bot.sendMessage(chat_id, "Codice sorgente: \n" +
                        "[FacebookBot](https://github.com/Fast0n/facebookbot)\n\n" +
                        "Sviluppato da: \n" +
                        "[Fast0n](https://github.com/Fast0n)\n\n" +
                        "🍺 Se sei soddisFatto  ✔️ offri una birra allo sviluppatore 🍺", parse_mode='Markdown', reply_markup=keyboard)
        user_state[chat_id] = 0


def register_token_user(chat_id, token):
    """
    Register given token user
    """
    insert = 1

    try:
        f = open(token_file, "r")
        for user in f.readlines():
            if user.replace('\n', '').split(":")[0] == str(chat_id):
                if user.replace('\n', '').split(":")[1] != str(token):
                    update_user(chat_id, token)
                    insert = 0
                    break

            if user.replace('\n', '').split(":")[1] == str(token):
                bot.sendMessage(chat_id, "Token esistente riprova")
                insert = 0
    except:
        f = open(token_file, "a")

    if insert:
        f = open(token_file, "a")
        f.write(str(chat_id) + ":" + str(token) + '\n')
        bot.sendMessage(chat_id, "Fatto  ✔️")
        insert = 1

    f.close()

    return insert


def update_user(chat_id, token):
    """
    Update token user
    """
    try:
        tmp = ''

        f = open(token_file, "r+")

        for user in f.read().splitlines():

            if user.replace('\n', '').split(":")[0] != str(chat_id):
                tmp = tmp + user + '\n'

        # Rewrite the file
        f = open(token_file, "w")

        for user in tmp:
            f.write(user)

        f.close()
        if register_token_user(chat_id, token):
            bot.sendMessage(chat_id, "Token aggiornato")
        else:
            bot.sendMessage(chat_id, "Fatto  ✔️")

        return 1

    except IOError:
        return 0


def register_user(chat_id):
    """
    Register given user
    """
    insert = 1

    try:
        f = open(client_file, "r+")

        for user in f.readlines():
            if user.replace('\n', '') == str(chat_id):
                insert = 0

    except IOError:
        f = open(client_file, "w")

    if insert:
        f.write(str(chat_id) + '\n')

    f.close()

    return insert


# Main
print("Avvio FacebookBot")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/FacebookBot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working
try:
    bot = telepot.Bot(token)
    bot.message_loop(on_chat_message)
    while(1):
        sleep(10)
finally:
    os.unlink(pidfile)
