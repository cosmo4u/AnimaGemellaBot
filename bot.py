# coding=utf-8
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
import time
import sqlite3
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

conn = sqlite3.connect('lovebot.db', check_same_thread=False)
db = conn.cursor()
bot = telepot.Bot('566265514:AAEaFer_TjG2QM7BLTiGnK-5wsnVE9Y_WyE')

def checkID():
    db.execute('SELECT nome FROM Persone WHERE ID = ?',())

def checkEta(text):
    try:
        eta = int(text)
    except:
        return 1
    else:
        if eta < 10 or eta > 50:
            return 2
        else:
            return 0

def register(msg):
    nome = msg['chat']['first_name']
    cognome = msg['chat']['last_name']
    chatid = msg['chat']['id']
    step = 1

    db.execute('INSERT INTO Persone (ID, nome, cognome, Step) VALUES (?, ?, ?, ?)',(chatid, nome, cognome, step))
    conn.commit()
    bot.sendMessage(chatid,'Ciao %s, benvenuto in LoveBot!' % nome)

def main(msg):
    chatid = msg['chat']['id']
    content_type, chat_type, chat_id = telepot.glance(msg)
    #step
    db.execute('SELECT * FROM Persone WHERE ID = ?', (chatid,))
    app = db.fetchone()
    if content_type == 'text':
        text = msg['text']
        try:
            step = app[3]
        except:
            step = app
        #acquisizione dati base
        if step == None and text == '/start':
            register(msg)
        #------------------------------------------------------------
        elif text == '/start' and step == 8:
            bot.sendMessage(chatid,'Sei già registrato!')
        #domanda
        #----_-_-approfondire step locali/database-_-_----
        db.execute('SELECT Step FROM Persone WHERE ID = ?', (chatid,))
        app = db.fetchone()
        step = app[0]
        if step == 1:
            bot.sendMessage(chatid,'Quanti anni hai?')
            step += 1
            db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
            conn.commit()
        #acquisizione età
        elif step == 2:
            check = checkEta(text)
            if check == 0:
                step += 1
                db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
                eta = text
                db.execute('UPDATE Persone SET Eta = ? WHERE ID = ?', (eta, chatid,))
                conn.commit()
                bot.sendMessage(chatid,"Età inserita correttamente!")
            elif check == 1:
                bot.sendMessage(chatid,"L'età deve essere un numero. Riprova.")
            elif check == 2:
                bot.sendMessage(chatid,"Età non valida. Inserisci la tua età reale.")
        #domanda città
        elif step == 3:
                    bot.sendMessage(chatid,"Inserisci la tua città.")
                    step += 1
                    db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
                    conn.commit()
        #acquisizione età
        elif step == 4:
            citta = msg['text']
            db.execute('SELECT * FROM comuni WHERE UPPER(nome) = UPPER(?)', (citta,))
            if db.fetchone() == None:
                bot.sendMessage(chatid,"Città non valida. Riprova.")
            else:
                db.execute('UPDATE Persone SET Citta = ? WHERE ID = ?', (citta, chatid,))
                bot.sendMessage(chatid,"Città inserita correttamente!")
                step += 1
                db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
                conn.commit()
        #domanda capelli
        elif step == 5:
            bot.sendMessage(chatid, 'Scegli il colore dei tuoi capelli (se il colore non esiste scegli altro):',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Biondi"), KeyboardButton(text="Neri"),
                                     KeyboardButton(text="Rossi"),  KeyboardButton(text="Castani"),
                                     KeyboardButton(text="Verdi"),  KeyboardButton(text="Grigi"),
                                     KeyboardButton(text="Viola"),  KeyboardButton(text="Blu"),
                                     KeyboardButton(text="Altro")]
                                ], resize_keyboard = True
                            ))
            step += 1
            db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
            conn.commit()
        #acquisizione capelli
        elif step == 6:
            capelli = msg['text']
            if capelli == 'Altro':
                bot.sendMessage(chatid, 'Digita il colore dei tuoi capelli: ')
            else:
                step += 1
                db.execute('UPDATE Persone SET Capelli = ?, STEP = ? WHERE ID = ?', (capelli, step, chatid,))
                conn.commit()
            # db.execute('SELECT colore from Capelli WHERE UPPER(colore) = UPPER(?)', (capelli,))
            # if db.fetchone() == None:
            #     bot.sendMessage(chatid,'Colore non valido. Riprova')
            # else:
            #     db.execute('UPDATE Persone SET Capelli = ? WHERE ID = ?', (capelli, chatid,))
            #     bot.sendMessage(chatid, 'Colore dei capelli inserito correttamente!')
            #     conn.commit()


MessageLoop(bot,main).run_as_thread()

while(1):
    time.sleep(3)
