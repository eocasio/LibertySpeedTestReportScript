# encoding: utf-8
#!/usr/bin/python
#adaptado por Moisés Cardona http://moisescardona.net
#trabajo original: http://thenextweb.com/shareables/2016/01/31/frustrated-comcast-customer-sets-up-bot-to-tweet-complaints-every-time-internet-speed-drops/
#codigo del trabajo original: http://pastebin.com/WMEh802V

########################################################################
# Modificado por Edwood Ocasio (edwood.ocasio@gmail.com)
# Cambios:
#   1. Añadí variables para facilitar configuración de los mensajes y
#   comparaciones.
#
#   2. Añadí variable SEND_FACEBOOK para declara si queremos enviar
#   mensajes o no.
#
#   3. Removí la necesidad de usar "eval"
#
#   4. Utilicé módulo "subprocess" para compatibilidad con Python 2.7
#
#   5. Convertí a "float" en lugar de "int" valores de "bandwidth" y 
#   "ping" 
# 
#   6. Cambié la forma de hacer el "parsing" de los valores de speedtest.

import os
import sys
import csv
import datetime
import time
import requests

# Para uso con Python 2.7
import subprocess

########################################################################
# CONFIGURACION
########################################################################

SEND_FACEBOOK = False

SPEEDTEST_CLI = "speedtest-cli --simple".split()
DATA_FILE = "data.csv"
EXPECTED_DOWNLOAD = 40.0
EXPECTED_UPLOAD = 4.0
SERVICE_CITY = 'Carolina'

# Límite de ancho de banda considerado "bueno"
BANDWIDTH_THRESHOLD = EXPECTED_DOWNLOAD * 0.75 # 75%

CANNOT_CONNECT_MESSAGE = 'Hola Liberty, por que no tengo internet %s? Pago por %s down\\%s up en %s... Por favor resuelvanme!!'

LOW_BANDWIDTH_MESSAGE = 'Hola Liberty, por que mi velocidad de internet es %s down\\%s up cuando pago por %s down\\%s up en %s (%s) ... Por favor resuelvanme!!'

GOOD_BANDWIDTH_MESSAGE = 'Hola Liberty, Gracias por ofrecerme un servicio de excelencia. Pago por %s down\\%s up en %s y estoy recibiendo la velocidad completa.'

# Configuration to connect to facebook
face_token = 'YOUR_ID' #Sustituye YOUR_ID por el ID del app que debes crear en https://developers.facebook.com/ 
libertypageid = '155802867766659' #este es el ID de la pagina de liberty, pero puedes cambiarlo al ID de Claro o cualquier otro proveedor. Puedes conseguir el ID de la pagina en http://findmyfbid.com/

########################################################################

"""
Sample output:

Ping: 143.505 ms
Download: 0.57 Mbit/s
Upload: 0.00 Mbit/s

"""
def test():
 
    #run speedtest-cli
    print 'running test'
    
    #~ a = os.popen().read(SPEEDTEST_CLI)
    a = subprocess.check_output(SPEEDTEST_CLI)
    print 'ran'
    #split the 3 line result (ping,down,up)
    lines = a.split('\n')
    
    #~ print lines
    #~ sys.exit()
    
    ts = time.time()
    date =datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    #if speedtest could not connect set the speeds to 0
    if "Cannot" in a:
        p = 100.0
        d = 0.0
        u = 0.0
    #extract the values for ping down and up values
    else:
        try:
            p = float(lines[0].split()[1])
            d = float(lines[1].split()[1])
            u = float(lines[2].split()[1])

        except ValueError:
            print "Cannot parse bandwidth values."
            sys.exit()
            
            
    print date,p, d, u
    #save the data to file for local network plotting
    out_file = open(DATA_FILE, 'a')
    writer = csv.writer(out_file)
    writer.writerow((ts*1000,p,d,u))
    out_file.close()


    #try to post to Liberty Page if speedtest couldnt even connet. Probably wont work if the internet is down
    if "Cannot" in a:
        try:
            post = (CANNOT_CONNECT_MESSAGE % (datetime.datetime.now().strftime('%d/%m/%Y %I:%M'), EXPECTED_DOWNLOAD, EXPECTED_UPLOAD, SERVICE_CITY)).replace(' ', '+')
            
            print post
            
            if SEND_FACEBOOK:
                requests.post("https://graph.facebook.com/" + libertypageid + "/feed/?message=" + post + "&access_token=" + face_token)
                
        except Exception, e:
            print str(e)
 
    # post to Liberty Page if down speed is less than whatever I set
    elif d < BANDWIDTH_THRESHOLD:
        try:
            post = (LOW_BANDWIDTH_MESSAGE % (d, u, EXPECTED_DOWNLOAD, EXPECTED_UPLOAD, SERVICE_CITY, datetime.datetime.now().strftime('%d/%m/%Y %I:%M'))).replace(' ', '+')

            print post
            
            if SEND_FACEBOOK:
                print "trying to Post to Facebook Page"
                requests.post("https://graph.facebook.com/" + libertypageid + "/feed/?message=" + post + "&access_token=" + face_token)
                
        except Exception,e:
            print str(e)
            pass
            
    elif d >= BANDWIDTH_THRESHOLD:
        
        try:
            post = (GOOD_BANDWIDTH_MESSAGE % (EXPECTED_DOWNLOAD, EXPECTED_UPLOAD, SERVICE_CITY,datetime.datetime.now().strftime('%d/%m/%Y %I:%M'))).replace(' ', '+')

            print post
            
            if SEND_FACEBOOK:
                print "trying to Post to Facebook Page"
                requests.post("https://graph.facebook.com/" + libertypageid + "/feed/?message=" + post + "&access_token=" + face_token)
                
        except Exception,e:
            print str(e)
            pass
                
    return
       
if __name__ == '__main__':
        test()
        print 'completed'
