# coding=utf-8
# cat sitecustomize.py
# encoding=utf8
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
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

pstep = 0

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
    try:
        cognome = msg['chat']['last_name']
    except:
        cognome = "Default"
    chatid = msg['chat']['id']
    step = -1

    db.execute('INSERT INTO Persone (ID, nome, cognome, Step) VALUES (?, ?, ?, ?)',(chatid, nome, cognome, step))
    db.execute('INSERT INTO AnimaGemella (ID) VALUES (?)', (chatid,))
    db.execute('UPDATE AnimaGemella SET IDAG = ? WHERE ID = ?', (chatid, chatid,))
    conn.commit()
    bot.sendMessage(chatid,'Ciao %s, benvenuto in AnimaGemellaBot!' % nome)

def menu(msg, chatid):
    pass

#MAIN
def main(msg):
    global pstep
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
            db.execute('DELETE FROM Persone WHERE ID = ?', (chatid,))
            db.execute('DELETE FROM AnimaGemella WHERE ID = ?', (chatid,))
            conn.commit()
            bot.sendMessage(chatid, 'Non fare troppo lo sborone e clicca /start')
        elif (chatid == 409317117 or chatid == 423869824) and text == '/delete':
            bot.sendMessage(chatid,'Cognome: ')
            step=1000
            updateStep(step, chatid)
        elif step == 1000:
            cognome = msg['text']
            db.execute('SELECT ID FROM Persone WHERE Cognome = ?', (cognome,))
            id = db.fetchone()[0]
            db.execute('DELETE FROM Persone WHERE Cognome = ?', (cognome,))
            db.execute('DELETE FROM AnimaGemella WHERE ID = ?', (id,))
            conn.commit()
            bot.sendMessage(chatid, 'Sborrami in faccia')
            #step
            try:
                step = readStep(chatid)
            except:
                step = None
        elif (chatid == 409317117 or chatid == 423869824) and text == '/broadcast':
            bot.sendMessage(chatid,'Scrivi il messaggio broadcast: ')
            pstep = step
            step = 1810
            updateStep(step,chatid)
        elif step == 1810 and text != '/menu':
            db.execute('SELECT N ORDER BY N ASC LIMIT 1 FROM Persone')
            N = db.fetchone()[0]
            for people in range(N):
                db.execute('SELECT ID WHERE N = ? FROM Persone', people)
                id = db.fetchone()[0]
                bot.sendMessage(id,'*_<<News dallo staff: \n' + text + '>>_*')
            updateStep(pstep,chatid)
        if text == '/menu':
            if step < 9:
                bot.sendMessage(chatid,'Devi prima registrarti.')
            elif (step > 8 and step < 113) or step == 200 or step == 115:
                if step == 115 or (step >=111 and step <113):
                    db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
                    idAnimaGemella = db.fetchone()[0]
                    bot.sendMessage(idAnimaGemella,"La persona ha cancellato la richiesta. Vuoi cercare un'altra persona?", reply_markup = ReplyKeyboardMarkup(keyboard = keybSiNo))
                    bot.sendMessage(chatid,"Hai cancellato la richiesta.", reply_markup = ReplyKeyboardMarkup(keyboard = keybSiNo))
                    step = 114
                    updateStep(step,idAnimaGemella)
                db.execute('DELETE FROM AnimaGemella WHERE ID = ?', (chatid,))
                db.execute('INSERT INTO AnimaGemella (ID) VALUES (?)', (chatid,))
                db.execute('UPDATE AnimaGemella SET IDAG = ? WHERE ID = ?', (chatid, chatid,))
                conn.commit()
                step = 9
                updateStep(step,chatid)
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
        if text == 'Trova Anima Gemella' and (step == 9 or step == 999):
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
            if text != 'Per Regione' and text != 'Per Provincia' and text != "Per Citta'" and text != "Italia":
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
            elif text == "Italia":
                db.execute('UPDATE AnimaGemella SET Ricerca = "Italia" WHERE ID = ?', (chatid,))
                step = 110
                updateStep(step, chatid)

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
                bot.sendMessage(chatid,'%s non valida! Riprova.' % ricerca)
            else:
                db.execute('UPDATE AnimaGemella SET Luogo = ? WHERE ID = ?', (infoluogo, chatid,))
                conn.commit()
                bot.sendMessage(chatid,'%s inserita correttamente!' % ricerca)
                step += 1
                updateStep(step, chatid)
        elif step == 111:
            if text == 'Info':
                db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
                idAnimaGemella = db.fetchone()[0]
                db.execute('SELECT * FROM Persone WHERE ID = ?',(idAnimaGemella,))
                infoAnima = db.fetchone()
                bot.sendMessage(chatid,'Nome: %s\nSesso: %s\nEtà: %d\nCittà: %s(%s)\nCapelli: %s' % (infoAnima[4].encode('utf-8'), infoAnima[3].encode('utf-8'), infoAnima[6], infoAnima[7].encode('utf-8'), infoAnima[8].encode('utf-8'), infoAnima[10].encode('utf-8')))
                bot.sendMessage(chatid,'Vuoi parlarci?', reply_markup = ReplyKeyboardMarkup(keyboard = keybSiNo))
                step += 1
                updateStep(step,chatid)
        elif step == 112:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?',(chatid,))
            idAnimaGemella = db.fetchone()[0]
            if text == '/Si':
                db.execute('SELECT Nome FROM Persone WHERE ID = ?', (idAnimaGemella,))
                nome = db.fetchone()[0]
                bot.sendMessage(chatid,'Hai accettato la richiesta!\nOra stai parlando con %s!\n\n- Per vedere le informazioni della tua anima gemella scrivi /info\n- Per terminare la conversione scrivi /end' % nome,reply_markup = ReplyKeyboardRemove())
                db.execute('SELECT * FROM Persone WHERE ID = ?', (chatid,))
                infoAnima = db.fetchone()
                bot.sendMessage(idAnimaGemella,'La richiesta è stata accettata!\nOra stai parlando con %s\nSesso: %s\nEtà: %d\nCittà: %s (%s)\nCapelli: %s\n\n- Per vedere le informazioni della tua anima gemella scrivi /info\n- Per terminare la conversione scrivi /end' % (infoAnima[4].encode('utf-8'), infoAnima[3].encode('utf-8'), infoAnima[6], infoAnima[7].encode('utf-8'), infoAnima[8].encode('utf-8'), infoAnima[10].encode('utf-8')))
                step += 1
                updateStep(step,chatid)
                updateStep(step,idAnimaGemella)
            elif text == '/No':
                bot.sendMessage(idAnimaGemella,"La richiesta non è stata accettata.\nVuoi cercare un'altra persona?.", reply_markup = ReplyKeyboardMarkup(keyboard = keybSiNo))
                bot.sendMessage(chatid,"Hai rifiutato la richiesta.\nVuoi cercare un'altra persona?.", reply_markup = ReplyKeyboardMarkup(keyboard = keybSiNo))
                step = 114
                updateStep(step, idAnimaGemella)
                updateStep(step, chatid)
        elif step == 114:
            if text == '/Si':
                step = 110
                updateStep(step,chatid)
            elif text == '/No':
                step = 9
                updateStep(step,chatid)
        #ricerca
        if step == 110:
            bot.sendMessage(chatid,'Sto cercando la tua Anima Gemella...')
            db.execute('SELECT * FROM AnimaGemella WHERE ID = ?', (chatid,))
            infoPref = db.fetchone()
            if infoPref[4] == 'Citta':
                db.execute('SELECT ID FROM Persone WHERE ID != ? AND Sesso = ? AND Eta >= ? AND Eta <= ? AND Citta = ? AND Step = 110 AND ID != ?', (chatid, infoPref[1], infoPref[2], infoPref[3], infoPref[5], infoPref[6],))
            elif infoPref[4] == 'Provincia':
                db.execute('SELECT ID FROM Persone WHERE ID != ? AND Sesso = ? AND Eta >= ? AND Eta <= ? AND Provincia = ? AND Step = 110 AND ID != ?', (chatid, infoPref[1], infoPref[2], infoPref[3], infoPref[5], infoPref[6],))
            elif infoPref[4] == 'Regione':
                db.execute('SELECT ID FROM Persone WHERE ID != ? AND Sesso = ? AND Eta >= ? AND Eta <= ? AND Regione = ? AND Step = 110 AND ID != ?', (chatid, infoPref[1], infoPref[2], infoPref[3], infoPref[5], infoPref[6],))
            elif infoPref[4] == 'Italia':
                db.execute('SELECT ID FROM Persone WHERE ID != ? AND Sesso = ? AND Eta >= ? AND Eta <= ? AND Step = 110 AND ID != ?', (chatid, infoPref[1], infoPref[2], infoPref[3], infoPref[6],))
            try:
                idAnimaGemella = db.fetchone()[0]
            except:
                idAnimaGemella = db.fetchone()
            if idAnimaGemella != None:
                db.execute('UPDATE AnimaGemella SET IDAG = ? WHERE ID = ?', (idAnimaGemella, chatid,))
                db.execute('UPDATE AnimaGemella SET IDAG = ? WHERE ID = ?', (chatid, idAnimaGemella,))
                conn.commit()
                bot.sendMessage(idAnimaGemella, 'Qualcuno ti ha trovato!\nClicca su Info per vedere chi è!', reply_markup = ReplyKeyboardMarkup(keyboard = keybInfo))
                db.execute('SELECT Nome FROM Persone WHERE ID = ?', (idAnimaGemella,))
                nome = db.fetchone()[0]
                bot.sendMessage(chatid,'Hai trovato una persona, attendi che accetti o rifiuti la richiesta...', reply_markup = ReplyKeyboardRemove())
                step += 1
                updateStep(step, idAnimaGemella)
                step = 115
                updateStep(step, chatid)
            else:
                bot.sendMessage(chatid,'La ricerca non ha prodotto risultati, attendi che qualcuno cerchi una persona con le tue caratteristiche oppure clicca Riprova per fare un altro tentativo oppure clicca /menu per tornare al menù.', reply_markup = ReplyKeyboardMarkup(keyboard = keybRiprova))
        #chat anima gemella
        elif step == 113:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?',(chatid,))
            idAnimaGemella = db.fetchone()[0]
            if text == '/end':
                db.execute('SELECT Nome FROM Persone WHERE ID = ?', (chatid,))
                nome = db.fetchone()[0]
                db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
                idAnimaGemella = db.fetchone()[0]
                bot.sendMessage(chatid,'Hai terminato la conversazione!')
                bot.sendMessage(idAnimaGemella,nome + ' ha terminato la conversazione!')
                step = 999
                updateStep(step,chatid)
                updateStep(step,idAnimaGemella)
            elif text == '/info':
                db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
                idAnimaGemella = db.fetchone()[0]
                db.execute('SELECT * FROM Persone WHERE ID = ?',(idAnimaGemella,))
                infoAnima = db.fetchone()
                bot.sendMessage(chatid,'Nome: %s\nSesso: %s\nEtà: %d\nCittà: %s(%s)\nCapelli: %s' % (infoAnima[4].encode('utf-8'), infoAnima[3].encode('utf-8'), infoAnima[6], infoAnima[7].encode('utf-8'), infoAnima[8].encode('utf-8'), infoAnima[10].encode('utf-8')))
            elif text == '/menu':
                bot.sendMessage(chatid,'Per terminare la conversazione ed andare al menù scrivi /end!')
            else:
                if text != '/Si' and text != '/No':
                    bot.sendMessage(idAnimaGemella,text)
        if text == 'Invia una segnalazione' and (step == 9 or step == 999):
            bot.sendMessage(chatid,'Adesso puoi segnalare un bug o inviare un feedback!\nScrivilo qui oppure torna al menu scrivendo /menu.', reply_markup = ReplyKeyboardRemove())
            step = 200
            updateStep(step, chatid)
        elif text == 'Lista dei Comandi' and (step == 9 or step == 999):
            bot.sendMessage(chatid, '/menu - Torna al menù principale\n/end - Termina una conversazione')
            step = 300
        elif step == 200:
            if text != '/menu':
                file = open("feedback.txt", "a")
                nome = msg['chat']['first_name']
                try:
                    cognome = msg['chat']['last_name']
                except:
                    cognome = "Default"
                data = msg['date']
                file.write(nome.encode('utf-8') + ' ' + cognome.encode('utf-8') + ' ' +str(data).encode('utf-8')+' '+str(chatid).encode('utf-8')+'\nFeedback:\n'+text.encode('utf-8')+'\n-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\n\n')
                file.close()
                bot.sendMessage(chatid,'Grazie mille per la segnalazione!')
                bot.sendMessage(409317117,'<<NUOVA SEGNALAZIONE INVIATA DA ' + nome.encode('utf-8') + ' ' + cognome.encode('utf-8') + '>>\n\n' + text.encode('utf-8'))
                bot.sendMessage(423869824,'<<NUOVA SEGNALAZIONE INVIATA DA ' + nome.encode('utf-8') + ' ' + cognome.encode('utf-8') + '>>\n\n' + text.encode('utf-8'))
                step = 9
                updateStep(step, chatid)
        elif text == 'About' and (step == 9 or step == 999):
            bot.sendMessage(chatid,'Bot sviluppato da:')
            bot.sendMessage(chatid,'Davide Gilè: https://www.instagram.com/davide_gile/')
            bot.sendMessage(chatid,'Giuseppe Lepore: https://www.instagram.com/syejoe/')
            db.execute('SELECT N ORDER BY N ASC LIMIT 1 FROM Persone')
            N = db.fetchone()[0]
            bot.sendMessage(chatid,N + 'persone utilizzano questo bot!')
        if step == 9:
            bot.sendMessage(chatid, 'Adesso scegli cosa fare:', reply_markup = ReplyKeyboardMarkup(keyboard = keybMenu, resize_keyboard = True))
        if step == 999:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
            idAnimaGemella = db.fetchone()[0]
            bot.sendMessage(chatid, 'Adesso scegli cosa fare:', reply_markup = ReplyKeyboardMarkup(keyboard = keybMenu))
            bot.sendMessage(idAnimaGemella, 'Adesso scegli cosa fare:', reply_markup = ReplyKeyboardMarkup(keyboard = keybMenu))
            step = 9
            updateStep(step, idAnimaGemella)
    elif content_type == 'photo':
        if step == 113:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
            idAnimaGemella = db.fetchone()[0]
            fileid = msg['photo'][0]['file_id']
            bot.sendPhoto(idAnimaGemella,fileid)
            bot.sendMessage(409317117,'<<NUOVA FOTO INVIATA DA ' + msg['chat']['first_name'] + msg['chat']['last_name'] + '>>')
            bot.sendPhoto(409317117,fileid)
            bot.sendMessage(423869824,'<<NUOVA FOTO INVIATA DA ' + msg['chat']['first_name'] + ' ' +msg['chat']['last_name'] +  '>>')
            bot.sendPhoto(423869824,fileid)
            strphoto = str(chatid)+'_'+str(msg['date'])
            bot.download_file(fileid, '/Immagini')
    elif content_type == 'audio':
        if step == 113:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
            idAnimaGemella = db.fetchone()[0]
            fileid = msg['audio']['file_id']
            bot.sendAudio(idAnimaGemella,fileid)
    elif content_type == 'voice':
        if step == 113:
            db.execute('SELECT IDAG FROM AnimaGemella WHERE ID = ?', (chatid,))
            idAnimaGemella = db.fetchone()[0]
            fileid = msg['voice']['file_id']
            bot.sendVoice(idAnimaGemella,fileid)

MessageLoop(bot,main).run_as_thread()

while(1):
    time.sleep(2)
