import sqlite3

conn = sqlite3.connect('anima_gemella.db', check_same_thread=False)
db = conn.cursor()

def updateStep(step, chatid):
    db.execute('UPDATE Persone SET Step = ? WHERE ID = ?', (step, chatid,))
    conn.commit()
