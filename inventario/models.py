from django.db import models
#from django import forms

# Create your models here.


class Fabricante(models.Model):
    Nombre = models.CharField(max_length=40)

    def __unicode__(self):
        return unicode(self.Nombre)


class Modelo(models.Model):
    Fabricante = models.ForeignKey(Fabricante)
    Serie = models.CharField(max_length=40)

    def __unicode__(self):
        return unicode(str(self.Fabricante) + " " + str(self.Serie))


class Ubicacion(models.Model):
    Nombre = models.CharField(max_length=40)

    def __unicode__(self):
        return unicode(self.Nombre)


class TipoLogin(models.Model):
    Nombre = models.CharField(max_length=40)
    password = models.CharField(max_length=40,)

    def __unicode__(self):
        return unicode(self.Nombre)


class Dispositivo(models.Model):
    Nombre_de_host = models.CharField("Nombre de host", max_length=100)
    Ip = models.IPAddressField()
    Modelo = models.ForeignKey(Modelo)
    Ubicacion = models.ForeignKey(Ubicacion)
    Puerto = models.CharField(max_length=5)
    Tipo_de_Login = models.ForeignKey(TipoLogin, verbose_name="Tipo de login")
