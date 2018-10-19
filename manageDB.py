# coding=utf-8
import sqlite3

conn = sqlite3.connect('anima_gemella.db', check_same_thread=False)
db = conn.cursor()

def updateStep(step, chatid):
    db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
    conn.commit()

def readStep(chatid):
    db.execute('SELECT Step FROM Persone WHERE ID = ?', (chatid,))
    try:
        app = db.fetchone()[0]
    except:
        app = db.fetchone()
    return app
