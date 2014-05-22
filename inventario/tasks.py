#from bs4 import BeautifulSoup #de|
from inventario.models import Backup, Dispositivo
import paramiko
import telnetlib
import time
import requests
import urllib
import urllib2
import Cookie
import hashlib
from celery import Celery

ruta = '/tmp/backups/'
Atyp = Celery('Atyp')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Atypidae.settings')
#
# CELERY_ACCEPT_CONTENT = ['json']
# Atyp = Celery(
#     'tasks',
#     backend='cache+memcached://127.0.0.1:11211/',
#     broker='amqp://guest@localhost//'
# )
# Atyp.config_from_object('django.conf:settings')
# Atyp.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@Atyp.task
def BrocadeTelnet(ip, puerto, usuario, login, nombrehost, backup):
    tn = telnetlib.Telnet(ip)
    tn.read_until("n: ")
    tn.write(usuario + "\n")
    tn.read_until("d: ")
    tn.write(login + "\n")
    tn.read_until("# ")
    tn.write(
        "copy running-config ftp://" + usuario
        + ":" + login + "@" + backup +
        "/redes/brocade/" + nombrehost +
        time.strftime("_%d_%m_%y")
    )
    print tn.read_all()
    tn.write("exit\n")


@Atyp.task
def CiscorouterSSH(ip, puerto, usuario, login, nombrehost, backup):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip, port=int(puerto),
                    username=usuario, password=login)
        ssh_stdin, ssh_stdout, ssh_stderr =\
            ssh.exec_command("show running-config")
        the_conf = ssh_stdout.read()
    except paramiko.SSHException:
        the_conf = "fallo en la conexion"
    destino = open(
        ruta + nombrehost + time.strftime("_%d_%m_%y-%H:%M") + '.conf',
        'w')
    if the_conf[:1] in ("*", "C", "\r"):
        destino.write(the_conf)
        destino.close()
        veri = hashlib.sha512(the_conf).hexdigest()
        Backup(
            dispositivo=Dispositivo.objects.get(Nombre_de_host=nombrehost),
            verificacion=veri,
            fecha=time.time()
        ).save()
        actualizacion = Dispositivo.objects.get(Nombre_de_host=nombrehost)
        actualizacion.Ultimo_Backup = time.strftime("%Y-%m-%d")
        actualizacion.save()
    else:
        print "falla", "--||| " + str(ord(the_conf[:1])) + "|||--"


@Atyp.task
def ForinetConfb(ip, puerto, usuario, password, nombrehost, backup):
    dire = 'https://' + ip + ':' + puerto + '/'
    url = dire + 'logincheck'
    url2 = dire + 'system/maintenance/backup'
    datos = {"username": usuario, "secretkey": password, "ajax": "1"}
    s = requests.Session()
    try:
        d = s.post(url, params=datos, verify=False, timeout=10)
        opciones = {
            "backup_to": "0",
            'config_type': "0",
            "fname_back_usb": "",
            "backup": "1",
            "CSRF_TOKEN": d.cookies["ccsrftoken"]
        }
        r = s.post(url2, params=opciones, timeout=10)
        the_conf = r.text
    except Exception:
        the_conf = "eRrror" + ip + "\n"
    destino = open(
        ruta + nombrehost + time.strftime("_%d_%m_%y-%H:%M") + '.conf',
        'w'
    )
    if the_conf.encode("utf8")[:4] == "#con":
        destino.write(the_conf.encode("utf8"))
        destino.close()
        veri = hashlib.sha512(the_conf.encode("utf8")).hexdigest()
        Backup(
            dispositivo=Dispositivo.objects.get(Nombre_de_host=nombrehost),
            verificacion=veri,
            fecha=time.time()
        ).save()
        actualizacion = Dispositivo.objects.get(Nombre_de_host=nombrehost)
        actualizacion.Ultimo_Backup = time.strftime("%Y-%m-%d")
        actualizacion.save()
    else:
        print "falla", the_conf[:3]


@Atyp.task
def ForinetConsfb(ip, puerto, usuario, password, nombrehost, backup):
    dire = 'https://' + ip + ':' + puerto + '/'
    url = dire + 'logincheck'
    datos = {"username": usuario, "secretkey": password, "ajax": "1"}
    data = urllib.urlencode(datos)
    req = urllib2.Request(url, data)
    #url2 = dire + 'system/maintenance/backup'
    url3 = dire + 'system/maintenance/backup'
    try:
        response = urllib2.urlopen(req, timeout=10)
        cookie = response.headers.get('Set-Cookie')
        C = Cookie.SimpleCookie()
        C.load(cookie)
        ext = "nada"
    except Exception, ext:
        print ext
    try:
        CSRF_TOKEN = C['ccsrftoken'].value
    except Exception, ex:
        print ex
        CSRF_TOKEN = ""
    opciones = {
        "backup_to": "0",
        'config_type': "0",
        "fname_back_usb": "",
        "backup": "1",
        "CSRF_TOKEN": CSRF_TOKEN
        }
    try:
        data3 = urllib.urlencode(opciones)
        req3 = urllib2.Request(url3, data3)
        req3.add_header('cookie', cookie)
        response = urllib2.urlopen(req3, timeout=10)
        the_conf = response.read()
    except Exception, ex:
        the_conf = """error
        de conexion, verificar por favor estado del dispositivo\n""" +\
            str(ex) + " " + str(ext)
    destino = open(
        ruta + nombrehost + time.strftime("_%d_%m_%y-%H:%M") + '.conf',
        'w'
    )
    if the_conf[:4] == "#con":
        destino.write(the_conf)
        destino.close()
        veri = hashlib.sha512(the_conf).hexdigest()
        Backup(
            dispositivo=Dispositivo.objects.get(Nombre_de_host=nombrehost),
            verificacion=veri,
            fecha=time.time()
            ).save()
        actualizacion = Dispositivo.objects.get(Nombre_de_host=nombrehost)
        actualizacion.Ultimo_Backup = time.strftime("%Y-%m-%d")
        actualizacion.save()
    else:
        print "falla", the_conf[:3]


@Atyp.task
def Eleccion(linea):
    funciones = {
        "Cisco 280022": CiscorouterSSH,
        "Cisco Catalyst 450022": CiscorouterSSH,
        "Fortinet 40C10443": ForinetConfb,
        "Fortinet 50B10443": ForinetConfb,
        "Fortinet 60B10443": ForinetConfb,
        "Fortinet 60C10443": ForinetConfb,
        "Fortinet 80C10443": ForinetConfb,
        "Fortinet 100D10443": ForinetConsfb,
        "Fortinet 110C10443": ForinetConsfb,
        "Fortinet FVM10443": ForinetConfb,
    }
    grabado = funciones[linea[2] + linea[4]].delay(
        linea[1],
        linea[4],
        linea[5],
        linea[6],
        linea[0],
        linea[7]
    )
    return grabado
