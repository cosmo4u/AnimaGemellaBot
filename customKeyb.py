# coding=utf-8
from telepot.namedtuple import KeyboardButton

keybMenu = [[KeyboardButton(text = 'Trova Anima Gemella')],
            [KeyboardButton(text = 'Invia una segnalazione')],
            [KeyboardButton(text = 'Lista dei Comandi')],
            [KeyboardButton(text = 'About')]
           ]

keybSesso = [[KeyboardButton(text = 'Maschio'), KeyboardButton(text = 'Femmina')]]

keybCapelli = [[KeyboardButton(text="Biondi"), KeyboardButton(text="Neri")],
               [KeyboardButton(text="Rossi"),  KeyboardButton(text="Castani")],
               [KeyboardButton(text="Verdi"),  KeyboardButton(text="Grigi")],
               [KeyboardButton(text="Viola"),  KeyboardButton(text="Blu")],
               [KeyboardButton(text="Altro")]
              ]

keybLuogo = [[KeyboardButton(text="Per Regione")],
             [KeyboardButton(text="Per Provincia")],
             [KeyboardButton(text="Per Citta'")],
             [KeyboardButton(text="Italia")]]

keybRiprova = [[KeyboardButton(text="Riprova")],
               [KeyboardButton(text="/menu")]]

keybInfo = [[KeyboardButton(text="Info")]]

keybSiNo = [[KeyboardButton(text="/Si"), KeyboardButton(text="/No")]]
