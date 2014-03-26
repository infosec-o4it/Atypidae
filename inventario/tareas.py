'''
Created on 4/03/2014

@author: arincon
'''
from bs4 import BeautifulSoup
import paramiko
import telnetlib
import time
import urllib
import urllib2


def CiscorouterSSH(ip, puerto, usuario, login, nombrehost):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip, port=int(puerto), \
                    username=usuario, password=login)
        ssh_stdin, ssh_stdout, ssh_stderr = \
        ssh.exec_command("show running-config")
    except paramiko.SSHException:
        print "fallo en la conexion"
    destino = open('/tmp/' + nombrehost, 'w')
    destino.write(ssh_stdout)
    destino.close()


def ForinetConfb(ip, puerto, usuario, password, nombrehost):
    dire = 'https://' + ip + ':' + puerto + '/'
    url = dire + 'logincheck'
    print url, usuario, password, nombrehost
    datos = {"username": usuario, "secretkey": password, "ajax": "1"}
    data = urllib.urlencode(datos)
    req = urllib2.Request(url, data)
    url2 = dire + 'system/maintenance/backup'
    url3 = dire + 'system/maintenance/backup'
    try:
        response = urllib2.urlopen(req, timeout=10)
        cookie = response.headers.get('Set-Cookie')
        req2 = urllib2.Request(url2)
        req2.add_header('cookie', cookie)
        response = urllib2.urlopen(req2, timeout=10)
        the_page = response.read()
        sopa = BeautifulSoup(the_page)
        ext = "nada"
    except Exception, ext:
        print ext
        sopa = "empty"
        cookie = "empty"
    try:
        CSRF_TOKEN = \
        sopa.body.find('input', attrs={'name': 'CSRF_TOKEN'}).attrs['value']
    except Exception, ex:
        print ex
        CSRF_TOKEN = ""
    opciones = {"backup_to": "0",
                "fname_back_usb": "",
                "backup": "1",
                "CSRF_TOKEN": CSRF_TOKEN}
    data3 = urllib.urlencode(opciones)
    req3 = urllib2.Request(url3, data3)
    req3.add_header('cookie', cookie)
    try:
        response = urllib2.urlopen(req3, timeout=10)
        the_conf = response.read()
    except Exception, ex:
        print ex
        the_conf = "error \
        de conexion, verificar por favor estado del dispositivo\n" + \
        str(ex) + " " + str(ext)
    destino = open('/tmp/' + nombrehost, 'w')
    destino.write(the_conf)
    destino.close()


def Eleccion(linea):
    funciones = {"Cisco 280022": CiscorouterSSH, \
                 "Fortinet 60C10443": ForinetConfb,
                 "Fortinet 80C10443": ForinetConfb,
                 "Fortinet 60B10443": ForinetConfb,
                 }
    grabado = funciones[linea[2] + linea[4]](linea[1], \
                linea[4], linea[5], linea[6], linea[0])
    return grabado

if __name__ == '__main__':
    pass
