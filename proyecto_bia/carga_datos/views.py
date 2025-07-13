import pandas as pd
from datetime import datetime, date
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ExcelUploadForm
from .models import ClientesBia
from django.http import HttpResponse
from io import StringIO

# DRF imports for API endpoints
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Función auxiliar para limpiar valores

def limpiar_valor(valor):
    if pd.isna(valor):  # NaN de pandas
        return None
    return valor  # deja fechas como date, y números como están

@login_required
def cargar_excel(request):
    mensaje = ""
    vista_previa = None

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                nombre_archivo = archivo.name
                extension = os.path.splitext(nombre_archivo)[1].lower()

                # Leer archivo
                if extension == '.csv':
                    try:
                        df = pd.read_csv(archivo)
                    except UnicodeDecodeError:
                        archivo.seek(0)
                        try:
                            df = pd.read_csv(archivo, encoding='latin1')
                            mensaje = "⚠️ El archivo no estaba en UTF-8. Se cargó con codificación Latin-1 (Windows)."
                        except Exception as e:
                            mensaje = f"Error al leer el archivo: {e}"
                            return render(request, 'upload_form.html', {
                                'form': form,
                                'mensaje': mensaje
                            })
                elif extension in ['.xls', '.xlsx']:
                    df = pd.read_excel(archivo)
                else:
                    mensaje = "Formato de archivo no soportado. Subí un archivo .csv o .xlsx"
                    return render(request, 'upload_form.html', {
                        'form': form,
                        'mensaje': mensaje
                    })

                # Validar columnas obligatorias
                columnas_requeridas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    mensaje = f"Faltan columnas obligatorias: {faltantes}"
                    return render(request, 'upload_form.html', {
                        'form': form,
                        'mensaje': mensaje
                    })

                df = df.where(pd.notnull(df), None)  # Reemplaza NaN con None

                errores_tipo = []
                columnas_fecha = ['fecha_carga', 'f_caida_real', 'f_caida', 'f_operacion', 'fecha_vto']

                # Procesar fechas
                for col in columnas_fecha:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col].astype(str).str.strip(), errors='coerce', dayfirst=True)
                        df[col] = df[col].dt.date

                # Validar tipos numéricos
                for col in ['deuda_o', 'deuda', 'promesa', 'valor_cuota']:
                    if col in df.columns:
                        try:
                            df[col].astype(float)
                        except Exception:
                            errores_tipo.append(f"Columna '{col}' debe contener valores numéricos")

                # Validar DNIs duplicados contra la base
                dnis_existentes = set(ClientesBia.objects.values_list('dni', flat=True))
                dnis_nuevos = set(df['dni'].dropna().astype(str))
                duplicados = dnis_nuevos.intersection(dnis_existentes)
                if duplicados:
                    errores_tipo.append(
                        f"❌ Ya existe registro en la base con los DNI: {', '.join(duplicados)}"
                    )

                if errores_tipo:
                    request.session['errores_validacion'] = errores_tipo
                    return redirect('errores_validacion')

                # Generar vista previa con marcas de error en fechas
                df_mostrar = df.copy()
                for col in columnas_fecha:
                    if col in df_mostrar.columns:
                        df_mostrar[col] = df_mostrar[col].apply(
                            lambda x: '<span style="color:red;">⚠ Formato de fecha inválida</span>' if x is None else x
                        )

                vista_previa = df_mostrar.head(5).to_html(classes="table table-bordered", escape=False, index=False)
                datos_serializables = df.astype(str).where(pd.notnull(df), None).to_dict(orient='records')
                request.session['datos_cargados'] = datos_serializables
                return render(request, 'confirmar_carga.html', {'vista_previa': vista_previa})

            except Exception as e:
                mensaje = f"Error al procesar el archivo: {e}"
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

@login_required
def confirmar_carga(request):
    datos = request.session.get('datos_cargados', [])
    if not datos:
        return redirect('cargar_excel')

    try:
        columnas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
        registros = [ClientesBia(**{col: limpiar_valor(fila.get(col)) for col in columnas}) for fila in datos]
        ClientesBia.objects.bulk_create(registros, batch_size=100)
        mensaje = f"✅ Se cargaron {len(registros)} registros correctamente."
    except Exception as e:
        mensaje = f"❌ Error al guardar los datos: {e}"

    request.session.pop('datos_cargados', None)
    form = ExcelUploadForm()
    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

@login_required
def errores_validacion(request):
    errores = request.session.get('errores_validacion', [])
    if not errores:
        return redirect('cargar_excel')

    if request.GET.get('exportar') == 'txt':
        buffer = StringIO()
        for err in errores:
            buffer.write(f"{err}\n")
        response = HttpResponse(buffer.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="errores_validacion.txt"'
        return response

    return render(request, 'errores_validacion.html', {'errores': errores})


# ---- Nuevas vistas API para consumo desde React con JWT ----

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cargar_excel(request):
    form = ExcelUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return Response({'success': False, 'errors': ['Formulario inválido']}, status=400)

    archivo = request.FILES['archivo']
    # Reutilizar la lógica de lectura y validaciones (similar a cargar_excel)
    try:
        # Leer y procesar dataframe
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension == '.csv':
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        df = df.where(pd.notnull(df), None)
        errores_tipo = []
        columnas_fecha = ['fecha_carga', 'f_caida_real', 'f_caida', 'f_operacion', 'fecha_vto']
        for col in columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col].astype(str).str.strip(), errors='coerce', dayfirst=True).dt.date
        for col in ['deuda_o','deuda','promesa','valor_cuota']:
            if col in df.columns:
                try: df[col].astype(float)
                except: errores_tipo.append(f"Columna '{col}' debe ser numérica")
        dnis_existentes = set(ClientesBia.objects.values_list('dni', flat=True))
        dnis_nuevos = set(df['dni'].dropna().astype(str))
        inter = dnis_nuevos.intersection(dnis_existentes)
        if inter:
            errores_tipo.append(f"DNIs ya existentes: {', '.join(inter)}")

        if errores_tipo:
            return Response({'success': False, 'errors': errores_tipo}, status=400)

        # Generar vista previa
        df_preview = df.copy()
        for col in columnas_fecha:
            if col in df_preview.columns:
                df_preview[col] = df_preview[col].apply(
                    lambda x: None if x is None else x
                )
        preview_html = df_preview.head(5).to_html(escape=False, index=False)
        data = df.astype(str).where(pd.notnull(df), None).to_dict(orient='records')

        # Guardar datos en sesión para confirmar luego
        request.session['datos_cargados'] = data

        return Response({
            'success': True,
            'preview': preview_html,
            'data': data
        })

    except Exception as e:
        return Response({'success': False, 'errors': [str(e)]}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_confirmar_carga(request):
    datos = request.session.get('datos_cargados', [])
    if not datos:
        return Response({'success': False, 'error': 'No hay datos para confirmar'}, status=400)
    try:
        columnas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
        registros = [ClientesBia(**{col: limpiar_valor(item.get(col)) for col in columnas}) for item in datos]
        ClientesBia.objects.bulk_create(registros, batch_size=100)
        request.session.pop('datos_cargados', None)
        return Response({'success': True, 'created_count': len(registros)})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_errores_validacion(request):
    errores = request.session.get('errores_validacion', [])
    if not errores:
        return Response({'success': False, 'error': 'Sin errores'}, status=404)
    # Exportar como texto si se pide
    if request.GET.get('exportar') == 'txt':
        txt = "\n".join(errores)
        return HttpResponse(txt, content_type='text/plain')
    return Response({'success': True, 'errors': errores})