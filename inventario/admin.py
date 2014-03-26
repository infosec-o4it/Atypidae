from django.contrib import admin
from django import forms
from models import Fabricante, Modelo, Ubicacion, TipoLogin, Dispositivo
from django.http import HttpResponse
from tareas import Eleccion
import csv


def prep_field(obj, field):
    """ Returns the field as a unicode string. If the field is a callable, it
    attempts to call it first, without arguments.
    """
    if '__' in field:
        bits = field.split('__')
        field = bits.pop()

        for bit in bits:
            obj = getattr(obj, bit, None)

            if obj is None:
                return ""

    attr = getattr(obj, field)
    output = attr() if callable(attr) else attr
    return unicode(output).encode('utf-8') if output else ""


def export_csv_action(description="Export as CSV", \
                      fields=None, exclude=None, header=True):
    """ This function returns an export csv action. """
    def export_as_csv(modeladmin, request, queryset):
        """ Generic csv export admin action.
        Based on http://djangosnippets.org/snippets/2712/
        """
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]
        labels = []

        if exclude:
            field_names = [f for f in field_names if f not in exclude]

        elif fields:
            field_names = [field for field, _ in fields]
            labels = [label for _, label in fields]

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % (
                unicode(opts).replace('.', '_')
            )

        writer = csv.writer(response)

        if header:
            writer.writerow(labels if labels else field_names)

        for obj in queryset:
            Eleccion([prep_field(obj, field) for field in field_names])
            writer.writerow([prep_field(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv

# Register your models here.
# Register your models here.


class AdminFabricante(admin.ModelAdmin):
    list_display = ('Nombre',)


class AdminModelo(admin.ModelAdmin):
    list_display = ('Fabricante', 'Serie')


class AdminUbicacion(admin.ModelAdmin):
    list_display = ('Nombre',)


class FormLogin(forms.ModelForm):
    class Meta:
        model = TipoLogin
        widgets = {'password': forms.PasswordInput}


class AdminTipoLogin(admin.ModelAdmin):
    form = FormLogin
    list_display = ('Nombre',)


class AdminDispositivo(admin.ModelAdmin):
    list_display = ('Nombre_de_host', 'Ip', 'Puerto', 'Modelo', 'Ubicacion', \
                    'Tipo_de_Login')
    search_fields = ('Nombre_de_host', 'Modelo__Serie', \
                     'Modelo__Fabricante__Nombre')
    list_filter = ('Ubicacion', 'Puerto', 'Modelo', 'Tipo_de_Login')
    actions = [
        export_csv_action("Backup y reporte",
            fields=[
                ('Nombre_de_host', 'Nombre_de_host'),
                ('Ip', 'Ip'),
                ('Modelo', 'Modelo'),
                ('Ubicacion', 'Ubicacion'),
                ('Puerto', 'Puerto'),
                ('Tipo_de_Login__Nombre', 'Usuario'),
                ('Tipo_de_Login__password', 'Password'),
            ],
            header=False,
        ),
    ]

admin.site.register(Fabricante, AdminFabricante)
admin.site.register(Modelo, AdminModelo)
admin.site.register(Ubicacion, AdminUbicacion)
admin.site.register(TipoLogin, AdminTipoLogin)
admin.site.register(Dispositivo, AdminDispositivo)
