import smtplib as smtp
import ssl
from threading import Timer
def send_mail(adres):
    try:
        context = ssl.create_default_context()
        server = smtp.SMTP_SSL('smtp.gmail.com', 465, context=context) 
        server.login('wyscig.szczurow.pg@gmail.com', 'W1y8S7c5I8g1SzCzUrOw')
        server.sendmail('wyscig.szczurow.pg@gmail.com', adres, '''Subject: Znaleziono nowe wpisy na enauczaniu! \nWyscig Szczurow znalazl nowe wpisy na platformie enauczanie.''')
        return True
    except Exception as err:
        tim = Timer(10, send_mail)
        tim.start()
        return err

if __name__ == '__main__':
    send_mail('ddworakaw@gmail.com')