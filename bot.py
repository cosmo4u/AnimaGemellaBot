# coding=utf-8
import unicodedata
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
import time
import sqlite3
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from customKeyb import *
from manageDB import *

bot = telepot.Bot('566265514:AAEaFer_TjG2QM7BLTiGnK-5wsnVE9Y_WyE')

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

def checkEtaMax(text, etaMin):
    try:
        etaMax = int(text)
    except:
        return 1
    else:
        if etaMax < 10 or etaMax > 50:
            return 2
        elif etaMax < etaMin:
            return 3
        else:
            return 0


def register(msg):
    nome = msg['chat']['first_name']
    cognome = msg['chat']['last_name']
    chatid = msg['chat']['id']
    step = -1

    db.execute('INSERT INTO Persone (ID, nome, cognome, Step) VALUES (?, ?, ?, ?)',(chatid, nome, cognome, step))
    db.execute('INSERT INTO AnimaGemella (ID) VALUES (?)', (chatid,))
    conn.commit()
    bot.sendMessage(chatid,'Ciao %s, benvenuto in AnimaGemellaBot!' % nome)

# def randomChat():

def menu(msg, chatid):
    pass

#MAIN
def main(msg):
    chatid = msg['chat']['id']
    content_type, chat_type, chat_id = telepot.glance(msg)
    #step
    try:
        step = readStep(chatid)
    except:
        step = None
    if content_type == 'text':
        text = msg['text']
        if (chatid == 409317117 or chatid == 423869824) and text == '/deleteme':
            stepp = step
            db.execute('DELETE FROM Persone WHERE ID = ?', (chatid,))
            db.execute('DELETE FROM AnimaGemella WHERE ID = ?', (chatid,))
            conn.commit()
            bot.sendMessage(chatid, 'Non fare troppo lo sborone')
            step = stepp
        if (chatid == 409317117 or chatid == 423869824) and text == '/delete':
            bot.sendMessage(chatid,'Cognome: ')
            stepp = step
            step=1000
            updateStep(step, chatid)
        elif step == 1000:
            cognome = msg['text']
            print(cognome)
            db.execute('SELECT ID FROM Persone WHERE Cognome = ?', (cognome,))
            id = db.fetchone()[0]
            db.execute('DELETE FROM Persone WHERE Cognome = ?', (cognome,))
            db.execute('DELETE FROM AnimaGemella WHERE ID = ?', (id,))
            conn.commit()
            bot.sendMessage(chatid, 'Sborrami in faccia')
            step = stepp
        #acquisizione dati base
        if step == None and text == '/start':
            register(msg)
        #------------------------------------------------------------
        elif text == '/start' and step >= 9:
            bot.sendMessage(chatid,'Sei già registrato!')
        #----_-_-approfondire step locali/database-_-_----
        #aggiorna step dopo il register
        step = readStep(chatid)
        #domanda sesso
        if step == -1:
            bot.sendMessage(chatid,'Scegli il tuo sesso:', reply_markup = ReplyKeyboardMarkup(keyboard = keybSesso))
            step += 1
            updateStep(step, chatid)
        #acquisizione sesso
        elif step == 0:
            if msg['text'] != 'Maschio' and msg['text'] != 'Femmina':
                bot.sendMessage(chatid,'Usa i pulsanti!')
            else:
                step += 1
                db.execute('UPDATE Persone SET Step = ?, Sesso = ? WHERE ID = ?', (step, msg['text'], chatid,))
                conn.commit()
                bot.sendMessage(chatid,'Perfetto.', reply_markup = ReplyKeyboardRemove())
        #domanda età
        if step == 1:
            bot.sendMessage(chatid,'Quanti anni hai?')
            step += 1
            updateStep(step, chatid)
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
        if step == 3:
            bot.sendMessage(chatid,"Inserisci la tua città:")
            step += 1
            updateStep(step, chatid)
        #acquisizione età
        elif step == 4:
            citta = msg['text']
            db.execute('SELECT Citta, Provincia, Regione FROM comuni WHERE UPPER(Citta) = UPPER(?)', (citta,))
            infocitta = db.fetchone()
            if infocitta == None:
                bot.sendMessage(chatid,"Città non valida. Riprova.")
            else:
                citta = infocitta[0]
                provincia = infocitta[1]
                regione = infocitta[2]
                db.execute('UPDATE Persone SET Citta = ?, Provincia = ?, Regione = ? WHERE ID = ?', (citta, provincia, regione, chatid,))
                bot.sendMessage(chatid,"Città inserita correttamente!")
                step += 1
                db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
                conn.commit()
        #domanda capelli
        if step == 5:
            bot.sendMessage(chatid, 'Scegli il colore dei tuoi capelli (se il colore non esiste scegli altro):',
                            reply_markup = ReplyKeyboardMarkup(keyboard = keybCapelli))
            step += 1
            updateStep(step, chatid)
        #acquisizione capelli
        elif step == 6:
            capelli = msg['text']
            if capelli == 'Altro':
                bot.sendMessage(chatid, 'Digita il colore dei tuoi capelli: ', reply_markup = ReplyKeyboardRemove())
            else:
                step += 1
        if step == 7:
            step += 1
            bot.sendMessage(chatid, 'Capelli inseriti!', reply_markup = ReplyKeyboardRemove())
        #registrazione completata
        if step == 8:
            step += 1
            bot.sendMessage(chatid, 'Congratulazioni! Registrazione completata!')
            db.execute('UPDATE Persone SET Capelli = ?, STEP = ? WHERE ID = ?', (capelli, step, chatid,))
            conn.commit()
        #domanda preferenze - sesso
        #aggiorna step dopo menu
        step = readStep(chatid)
        if text == 'Trova Anima Gemella' and step > 8:
            step = 100
            updateStep(step, chatid)
        if step == 100:
            bot.sendMessage(chatid,'Inserisci le tue preferenze:')
            bot.sendMessage(chatid,'Scegli il sesso della tua anima gemella:', reply_markup = ReplyKeyboardMarkup(keyboard = keybSesso))
            step += 1
            updateStep(step, chatid)
        #acquisizione sesso
        elif step == 101:
            sesso = msg['text']
            if sesso != 'Maschio' and sesso != 'Femmina':
                bot.sendMessage(chatid,'Usa i pulsanti!')
            else:
                step += 1
                db.execute('UPDATE AnimaGemella SET Sesso = ? WHERE ID = ? ', (sesso, chatid,))
                conn.commit()
                bot.sendMessage(chatid,'Perfetto.', reply_markup = ReplyKeyboardRemove())
        #domanda età minima
        if step == 102:
            bot.sendMessage(chatid,"Inserisci l'età minima della tua anima gemella:")
            step += 1
            updateStep(step, chatid)
        #acquisizione età minima
        elif step == 103:
            check = checkEta(text)
            if check == 0:
                step += 1
                etaMin = text
                db.execute('UPDATE AnimaGemella SET EtaMin = ? WHERE ID = ?', (etaMin, chatid,))
                conn.commit()
                bot.sendMessage(chatid,"Età inserita correttamente!")
            elif check == 1:
                bot.sendMessage(chatid,"L'età deve essere un numero. Riprova.")
            elif check == 2:
                bot.sendMessage(chatid,"Età non valida. Inserisci un'età reale.")
        if step == 104:
            bot.sendMessage(chatid,"Inserisci l'età massima della tua anima gemella:")
            step += 1
            updateStep(step, chatid)
        #acquisizione etamax
        elif step == 105:
            db.execute('SELECT EtaMin FROM AnimaGemella WHERE ID = ?', (chatid,))
            etaMin = db.fetchone()[0]
            check = checkEtaMax(text, etaMin)
            if check == 0:
                step += 1
                etaMax = text
                db.execute('UPDATE AnimaGemella SET EtaMax = ? WHERE ID = ?', (etaMax, chatid,))
                conn.commit()
                bot.sendMessage(chatid,"Età inserita correttamente!")
            elif check == 1:
                bot.sendMessage(chatid,"L'età deve essere un numero. Riprova.")
            elif check == 2:
                bot.sendMessage(chatid,"Età non valida. Inserisci un'età reale.")
            elif check == 3:
                bot.sendMessage(chatid,"L'età massima non può essere minore dell'età minima! Riprova:")
        #domanda ricerca
        if step == 106:
            bot.sendMessage(chatid,'Adesso scegli come trovare la tua Anima Gemella!',reply_markup = ReplyKeyboardMarkup(keyboard = keybLuogo))
            step += 1
            updateStep(step, chatid)
        #acquisizione ricerca
        elif step == 107:
            text = msg['text']
            if text != 'Per Regione' and text != 'Per Provincia' and text != "Per Citta'":
                bot.sendMessage(chatid,'Usa i pulsanti!')
            elif text == 'Per Regione':
                db.execute('UPDATE AnimaGemella SET Ricerca = "Regione" WHERE ID = ?', (chatid,))
                step += 1
            elif text == 'Per Provincia':
                db.execute('UPDATE AnimaGemella SET Ricerca = "Provincia" WHERE ID = ?', (chatid,))
                step += 1
            elif text == "Per Citta'":
                db.execute('UPDATE AnimaGemella SET Ricerca = "Citta" WHERE ID = ?', (chatid,))
                step += 1
            conn.commit()
        #domanda luogo
        if step == 108:
            db.execute('SELECT Ricerca FROM AnimaGemella WHERE ID = ?',(chatid,))
            ricerca = db.fetchone()[0]
            bot.sendMessage(chatid,"Inserisci la %s della tua anima gemella:" % ricerca, reply_markup = ReplyKeyboardRemove())
            step += 1
            updateStep(step, chatid)
        #acquisizione luogo
        elif step == 109:
            db.execute('SELECT Ricerca FROM AnimaGemella WHERE ID = ?',(chatid,))
            ricerca = db.fetchone()[0]
            if ricerca == 'Regione':
                db.execute('SELECT Regione FROM comuni WHERE UPPER(Regione) = UPPER(?)', (text,))
            elif ricerca == 'Citta':
                db.execute('SELECT Citta FROM comuni WHERE UPPER(Citta) = UPPER(?)', (text,))
            elif ricerca == 'Provincia':
                db.execute('SELECT Provincia FROM comuni WHERE UPPER(Provincia) = UPPER(?)', (text,))
            try:
                infoluogo = db.fetchone()[0]
            except:
                bot.sendMessage(chatid,'%s non valida!' % ricerca)
            else:
                db.execute('UPDATE AnimaGemella SET Luogo = ? WHERE ID = ?', (infoluogo, chatid,))
                conn.commit()
                bot.sendMessage(chatid,'%s inserita correttamente!' % ricerca)
                step = 9
                updateStep(step, chatid)
        if text == 'Random Chat':
            step = 200
            updateStep(step, chatid)
        elif text == 'Lista dei Comandi':
            bot.sendMessage(chatid, 'listadeicomandi')
        elif step == 200:
            # randomChat()
            step = 9
            db.execute('UPDATE Persone SET STEP = ? WHERE ID = ?', (step, chatid,))
            conn.commit()
        if step == 9:
            bot.sendMessage(chatid, 'Adesso scegli cosa fare:', reply_markup = ReplyKeyboardMarkup(keyboard = keybMenu))


MessageLoop(bot,main).run_as_thread()

while(1):
    time.sleep(1)
