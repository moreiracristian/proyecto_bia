import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import ClientesBia, Certificate
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.staticfiles import finders

# Función link_callback para resolver rutas absolutas
def link_callback(uri, rel):
    """
    Convierte una URI (como /static/images/logo.png) en la ruta absoluta real del archivo.
    """
    # Si la URI empieza con STATIC_URL, elimínala para obtener la ruta relativa
    if uri.startswith(settings.STATIC_URL):
        path_relative = uri.replace(settings.STATIC_URL, '', 1)  # elimina solo la primera ocurrencia
        absolute_path = None
        # Buscar en cada directorio definido en STATICFILES_DIRS
        for static_dir in settings.STATICFILES_DIRS:
            candidate = os.path.join(static_dir, path_relative)
            if os.path.exists(candidate):
                absolute_path = candidate
                break
        if absolute_path:
            return absolute_path
        else:
            raise Exception("No se encontró el archivo estático: {}".format(path_relative))
    elif uri.startswith(settings.MEDIA_URL):
        path_relative = uri.replace(settings.MEDIA_URL, '', 1)
        absolute_path = os.path.join(settings.MEDIA_ROOT, path_relative)
        if os.path.exists(absolute_path):
            return absolute_path
        else:
            raise Exception("No se encontró el archivo media: {}".format(path_relative))
    # Para otras URIs, retornamos la misma URI
    return uri

def generate_pdf(html):
    result = ContentFile(b"")
    pisa_status = pisa.CreatePDF(html, dest=result, link_callback=link_callback)
    if pisa_status.err:
        return None
    return result

def certificate_view(request):
    context = {}
    if request.method == 'POST':
        dni = request.POST.get('dni')
        try:
            cliente = ClientesBia.objects.get(dni=dni)
        except ClientesBia.DoesNotExist:
            context['error'] = "Cliente no encontrado."
            return render(request, 'form.html', context)

        # Verificar que la deuda sea 0 (o la condición que determines)
        if not cliente.estado_leg or cliente.estado_leg.lower() != 'cancelado':
            context['error'] = "El cliente tiene deuda pendiente."
            return render(request, 'form.html', context)

        certificate, created = Certificate.objects.get_or_create(client=cliente)
    
    # Si se creó el objeto o no tiene un archivo asociado, se genera el PDF
        if created or not certificate.pdf_file:
            html = render_to_string('pdf_template.html', {'client': cliente})
            pdf_file = generate_pdf(html)
            if not pdf_file:
                context['error'] = "Error al generar el PDF."
                return render(request, 'form.html', context)
            file_name = f"certificado_{cliente.dni}.pdf"
            certificate.pdf_file.save(file_name, pdf_file)
            
            # Opcionalmente, actualizamos el objeto para asegurarnos de que el archivo se guarde.
            certificate.save()

            # Una vez guardado, lo enviamos para descarga inmediata
            with open(certificate.pdf_file.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="certificado_{cliente.dni}.pdf"'
                return response
        else:
            # Si el PDF ya existe, se informa al usuario y se proporciona el enlace
            context['info'] = "Ya generaste el PDF correspondiente."
            context['download_url'] = certificate.pdf_file.url
            return render(request, 'form.html', context)
    return render(request, 'form.html', context)

