import PySimpleGUI as sg
import sys, os, time
from threading import Timer  #ustawienie by program wykonywał się jakoby z folderu w którym jest skrypt
import PGbrowser as pg                                      #pozwala to na zaimportowanie drugiego pliku z jego folderu (webhandler(3).py) bez podawania do niego ścieżki
import mailing as mailer
import notification as notif
import winsound
import yaml
import crypter

# def resource_path(relative_path):
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)

def log(event):
    time1 = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    with open('logs.txt','a') as logs:
        logs.write(time1 + str(event) + '\n')
        logs.close()

class Settings():
    def __init__(self):
        self.status = False
        self.send_email = False
        self.sound = True
        self.sound_running = False
        self.interval = 15
        self.send_notification = False
        self.minimized = False
        self.sound_timer = None
        self.timer = None

        with open('loginDetails.yml') as file1:
            self.config_file = yaml.safe_load(file1 )
        self.login = self.config_file['pg_user']['login']
        self.password = crypter.decrypt(self.config_file['pg_user']['password'])
        self.link = self.config_file['pg_user']['link']
        self.whole_look_for = self.config_file['pg_user']['look_for']
        self.look_for = self.whole_look_for.split(';')
        self.where_to_email = self.config_file['settings']['where_to_send_email']
        self.send_email = self.config_file['settings']['send_email']
        self.sound = self.config_file['settings']['sound']
        self.send_notification = self.config_file['settings']['notification']['send_notification']
        self.interval = self.config_file['settings']['interval']
        self.number_of_exercises = self.config_file['settings']['number_of_exercises']
        #self.private_key = self.config_file['settings']['notification']['private_key']
        self.private_key = crypter.decrypt(self.config_file['settings']['notification']['private_key'])
        self.device_ID = self.config_file['settings']['notification']['device_ID']

    def saveAppSettings(self):
        self.config_file['settings']['sound'] = self.sound
        self.config_file['settings']['send_email'] = self.send_email
        self.config_file['settings']['notification']['send_notification'] = self.send_notification
        self.config_file['settings']['interval'] = self.interval
        self.config_file['settings']['number_of_exercises'] = self.number_of_exercises
        with open('loginDetails.yml','w') as file_to_get_updated:
            yaml.safe_dump(self.config_file, file_to_get_updated, default_flow_style=False)

    def changeSettings(self,val):
        self.config_file['pg_user']['login'] = self.login = val['_LOG_']
        self.password = val['_PAS_']
        self.config_file['pg_user']['password']  = crypter.encrypt(val['_PAS_'])
        self.config_file['pg_user']['link'] = self.link = val['_LIN_']
        self.look_for = self.whole_look_for.split(';')
        self.config_file['pg_user']['look_for'] = self.whole_look_for = val['_LFO_']
        self.private_key = val['_KEY_']  
        self.config_file['settings']['notification']['private_key'] = crypter.encrypt(val['_KEY_'])
        self.config_file['settings']['notification']['device_ID'] = self.device_ID = val['_DEV_']
        self.config_file['settings']['where_to_send_email'] = self.where_to_email = val['_EMA_']
        with open('loginDetails.yml','w') as file_to_get_updated:
            yaml.safe_dump(self.config_file, file_to_get_updated, default_flow_style=False)

s = Settings()
tries = 0
spiner = sg.Spin(values = list(range(31)), size = (3,10), key = '_SPIN_', initial_value = s.number_of_exercises, enable_events=True)
przycisk = sg.Button(button_text='START',size=(20,2))
layout = [
          [sg.Checkbox('Dźwięk powiadomienia', default = s.sound, enable_events=True, key = '_SOUND_')], 
          [sg.Checkbox('Powiadomienie na telefon', default = s.send_notification, enable_events=True, key = '_NOTIFY_')],
          [sg.Checkbox('Wiadomość email', default = s.send_email, enable_events=True, key = '_EMAIL_')],
          [sg.Text('Ostatnia ilość zadań'), spiner], 
          [sg.Text(text = 'Co ile minut sprawdzać:')],
          [sg.Slider(range=(1,120), orientation='horizontal', default_value=s.interval, key='_SLIDER_', enable_events=True)], 
          [sg.Text(text = 'Sprawdzanie wyłączone', key = '_STATUS_', font = '30', justification = 'right')],
          [przycisk],
          [sg.Button(button_text='Minimalizuj',size=(9,1), key='_MIN_'),sg.Button(button_text='Ustawienia',size=(9,1), key='_SET_')]
          ]
layout2 = layout
ctr = sg.Window('Wyscig Szczurow',layout, icon = 'icon.ico', finalize = True)
logo= b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAaVBMVEUAAADi4+Tw8PDt7e3R1tksU3oSPmzR1dj////DzddYc5Dz8fL////+/f7n5+png58AKF4EN2kBMmUtU3z6+fqInbPX2+FKa46qkaAfSXW1ws/wl5rlHSXxv8DlOkHjDhedrb7oeH3oYmjBq4IXAAAAC3RSTlMA0tLS0tLS0v7+0vVPMicAAAEpSURBVDjL3VPbboMwDA3d6ELj3Ck0kBbo/3/kbAMFKu1t0qQdCQU7B/v4ghD/AsXpA3H6LM/lDufya/YXQgFBg7HO+cDwzlmDLoISSmpJ0LKKzjNcrF5OJCxUraG+eqQ4f63JmgMr0awGnaYNoTV7TyOi3fi1htuNjzWmjSK52OG7BJDo6HPu8QO2NHTRJZF8YM0IuD+GnIfHXbKFdQWPhEC6xhormga8R8YwYe31SIrDTMAgseozXzMl91gzXywE71J3JHSJmxLWFFg6mOea4mlgaUqYRbbUDOzdSySphKadRbo0cs30qClnVLhYgHmQYNXPjVI2vbXaem/fWr0blh5JOqbU+2Ft42ZR3JS2OYybIDF62BYm7BZmWbnicly5y+r/61/id/AN7EImXQp7VPoAAAAASUVORK5CYII='
logo_off= b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAUCAYAAADskT9PAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAANASURBVEhLrZZtSFNRGMf/d5vlexaKGjGNXpRKEEMkM1AkyhVhiX7I+lCZklKEqURJiJWJlEhFpAgGaX0Qa0FZEVKU2LcwsjQsxAW5aeLrrHTzdp+jZ95dtzZXPzjs3HPO83+ePfc55x5hwGgS/f18YbVaIUetVuP74DDO3nyEoREzQlb6zc+4B7epLNiH1aHBDvUnzVMQJsbGRf/AgPnhBcRZEYJKgNE4hLL6J6htesnGNSv8YJ2xsL4StZcGljEz6+dlp6AsZw/CwkJsWkomxycWAnC2iI+3v+tBfkUTPnw0sCAcQc5jNmtx61w2kuKiXWq6HQBBczPTM6hufI7SulbmjAfC+5dydSg8tAtey7zs7JTIA0B3b79IzFpnWXOGfH5gYFDUFVSLQtxx1qhPY8RSdMi3EJNRKibGrsONkmy3IrdYLNBoNGyeXgvB0y2fUyLXpUyerGpCR+dXqH0iE8raXndB/6YTEeGrsDEyXFpNFtJiwV6Inql6LVIR0q82PJg1gsboDziykztvlfxkldxGa9t7+Ph7Qx20YXuZWZo3DU+g6UE7jKNjiI9ag4AAvzlDslWIknMlfIzWye2YreTYZPqBoppmFFbcx5D5FzS+3gj0WQYhIq1YNJhG2RYieEHVlmTi8N6kuX/1D1C67z5uR15Vs13h0lbWhgZBxZ5k0AKaPHb+DrYeLLe9Z08gW9IgLdLkzuUsCoDg2Rif+o1xKV2eQrakQXBNJYsCoDQRlcWZ6NVfhm5HLHv2BLIlDdIiuLYcVoST0xaWotnJn9ClxkJflYv01HioBCk+XkiKynYFL0SVSiVt0yhkJcegb3AEn7u/QVSrWEZsRdjfZ0LE2lBcyEnD0QMpCwISfE8rn53hyo62Yf6Ve+A+WQC7Ezfh6qkM8COZcOSI5v7HQURHcNH1Fjzr+OT5UZx3sUHUJJxgjfoeH8VL+RhRv0H/CuX1T1kK+bai4uKv8Eh6sm0t4UyTZ8Ltz3HPFwPO1LRIR2gnBN/li7YVFbEobTkq4munMxC9XutS0y4AZ/ALSd3DDuaAH1SOoKAoGxRg7v5E9y4kf7uS0ZWpuvEF3nYZPLqSbduile4HO+Fcfwp/AEnfxtVrAzf3AAAAAElFTkSuQmCC'
tray_menu_start = [ 'Otwórz', ['Otwórz','Start','Wyjdź']]
tray_menu_stop = [ 'Otwórz', ['Otwórz','Stop','Wyjdź']]
tray = sg.SystemTray(menu = tray_menu_start, data_base64=logo_off)
tray.hide()


def alarmSound():
    winsound.PlaySound('sound.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
    if s.status and s.sound:
        s.sound_timer = Timer(7, alarmSound)
        s.sound_timer.start()

'''
def openPopUp(nowe):
    print('opening popup')
    alarmSound()
    ctr.close()
    popUp = sg.Window('Znaleziono', [ [sg.Text('Nowe zadania ({})'.format(nowe))], [sg.Button(button_text = 'OK')] ], disable_minimize = True )
    popUpOpen = True
    while True:
        
        event, values = popUp.read()
        print(event)
        if sg.WIN_CLOSED in [event]:
            popUp.close()
            popUpOpen = False
            break
    '''

def check():
    global tries
    output = None
    try:
        output = pg.checkPG(s.login, s.password, s.link, s.look_for)
        if output > s.number_of_exercises and s.status:
            log('{} nowe zadania'.format(output))
            spiner.Update(value = output)
            s.number_of_exercises = output
            ctr['_STATUS_'].Update(value = 'Nowe zadania! ({})'
                           .format(s.number_of_exercises), text_color = 'red')
            przycisk.Update(button_color=('white', 'red'))
            if s.minimized:
                s.minimized = False
                tray.hide()
                ctr.un_hide()
            ctr.bring_to_front()
            if s.sound:
                alarmSound()
            if s.send_email:
                mailer.send_mail(s.where_to_email)
            if s.send_notification:
                notif.send_notification(s.private_key, s.device_ID,output - s.number_of_exercises)
        elif output == s.number_of_exercises:
            log('Brak nowych zadan')
        else:
            raise Exception(output)
    except Exception as err:
        log(err)
        if output == 'Failed to log: incorrect password':
            stop_checking()
            ctr.Element('_STATUS_').Update('Błędny login/hasło', text_color='red')
            winsound.PlaySound('SystemQuestion', winsound.SND_ALIAS | winsound.SND_ASYNC)
            tries = 0
            return
        elif tries < 5:
            s.timer = Timer(10, check)
            tries += 1
        else:
            ctr.Element('_STATUS_').Update('Błąd sprawdzania', text_color='red')
            s.timer = Timer(s.interval*60, check)
    else:
        tries = 0
        s.timer = Timer(s.interval*60, check)
    finally:
        if s.status and not s.timer.is_alive():
            #s.timer.cancel()
            s.timer.start()


def start_checking():
    s.status = True
    przycisk.Update(text = 'STOP', button_color=('white', 'royalblue4'))
    tray.Update(menu = tray_menu_stop, data_base64= logo)
    ctr['_STATUS_'].Update('Sprawdzanie aktywne', text_color='lime')
    s.timer = Timer(1, check) 
    s.timer.start()

if len(sys.argv) > 1:
    if sys.argv[1]=="start":
        start_checking()

def stop_checking():
    s.status = False
    przycisk.Update(text = 'START', button_color=('white', '#274873'))
    tray.Update(menu = tray_menu_start, data_base64= logo_off)
    ctr.Element('_STATUS_').Update('Sprawdzanie wyłączone', text_color='white')
    if s.timer is not None:
        s.timer.cancel()
    if s.sound_timer is not None:
        s.sound_timer.cancel()

def ustawienia():
    ctr.hide()
    width = (37, 1)
    layout = [
        [sg.Text('Login do enauczania:')],
        [sg.InputText(default_text= s.login, key='_LOG_', size= width)],
        [sg.Text('Hasło do enauczania:')],
        [sg.InputText(default_text= s.password, password_char= '*', key='_PAS_', size= width)],
        [sg.Text('Link do kursu:')],
        [sg.InputText(default_text= s.link, key='_LIN_', size= width)],
        [sg.Text('Email na który mają trafiać powiadomienia:')],
        [sg.InputText(default_text= s.where_to_email, key='_EMA_', size= width)],
        [sg.Text('Elementy do wyszukiwania\n(tekst na stronie np: \"Zadanie konkursowe\")\nw przypadku kilku oddziel je średnikiem:')],
        [sg.InputText(default_text= s.whole_look_for, key='_LFO_', size= width)],
        [sg.Text('Klucz pushsafer (private key):')],
        [sg.InputText(default_text= s.private_key, key='_KEY_', password_char= '*', size= width)],
        [sg.Text('Numer urządzenia (device_id):')],
        [sg.InputText(default_text= s.device_ID, key='_DEV_', size= width)],
        [sg.Button(button_text='Zapisz',size=(15,1), key='_SAV_'),sg.Button(button_text='Anuluj',size=(15,1), key='_CAN_')]
        ]
    settings_win = sg.Window('Ustawienia',layout, icon = 'icon.ico')
    while True:
        event, values = settings_win.read()
        print(event,values)
        if event == '_SAV_':
            s.changeSettings(values)
            event = '_CAN_'
        if sg.WIN_CLOSED == event or event == 'Exit' or event == '_CAN_':
            settings_win.close()
            ctr.un_hide()
            break
            

while True:
    event, values = ctr.read()
    if sg.WIN_CLOSED == event or event == 'Exit':
        s.status = False
        if s.timer is not None:
            s.timer.cancel()
        if s.sound_timer is not None:
            s.sound_timer.cancel()
        s.saveAppSettings()
        tray.close()
        ctr.close()
        break
    elif '_SLIDER_' == event:
        s.interval = values['_SLIDER_']
        if s.status:
            event = 'START'
    elif '_SPIN_' == event:
        s.number_of_exercises = values['_SPIN_']
        if s.status:
            event = 'START'
    if 'START' == event:
        if s.status == False:
            start_checking()
        else:
            stop_checking()
    elif '_SET_' == event:
        stop_checking()
        ustawienia()
    elif '_NOTIFY_' == event:
        s.send_notification = values['_NOTIFY_']
    elif '_SOUND_' == event:
        s.sound = values['_SOUND_']
    elif '_EMAIL_' == event:
        s.send_email = values['_EMAIL_']
    elif '_MIN_' == event:
        s.minimized = True
        ctr.hide()
        tray.un_hide()
        while True:
            event = tray.read(timeout = 100)
            if event in ('Otwórz', '__DOUBLE_CLICKED__') or s.minimized == False:
                s.minimized = False
                tray.hide()
                ctr.un_hide()
                break
            elif event == 'Start':
                start_checking()
            elif event == 'Stop':
                stop_checking()
            elif event == 'Wyjdź':
                ctr.close()
                tray.close()
                sys.exit(0)
        




