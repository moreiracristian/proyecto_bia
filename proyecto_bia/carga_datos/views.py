import pandas as pd
from datetime import datetime, date
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ExcelUploadForm
from .models import ClientesBia
from django.http import HttpResponse
from io import StringIO

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
                            return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje}) # Alternativa compatible con Excel en Windows
                elif extension in ['.xls', '.xlsx']:
                    df = pd.read_excel(archivo)
                else:
                    mensaje = "Formato de archivo no soportado. Subí un archivo .csv o .xlsx"
                    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

                columnas_requeridas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    mensaje = f"Faltan columnas obligatorias: {faltantes}"
                    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

                df = df.where(pd.notnull(df), None)  # Reemplaza NaN con None

                errores_tipo = []  # Asegurate de tener esto definido antes del bucle

                columnas_fecha = ['fecha_carga', 'f_caida_real', 'f_caida', 'f_operacion', 'fecha_vto']

                for col in columnas_fecha:
                    if col in df.columns:
                        try:
                            # Convertir a string para limpiar espacios
                            df[col] = df[col].astype(str).str.strip()

                            # Intentar conversión automática (más tolerante)
                            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

                            # Convertir a tipo date
                            df[col] = df[col].dt.date

                        except Exception as e:
                            print(f"⚠️ Error al procesar {col}: {e}")

                for col in ['deuda_o', 'deuda', 'promesa', 'valor_cuota']:
                    if col in df.columns:
                        try:
                            df[col].astype(float)
                        except Exception:
                            columnas_fecha.append(f"Columna '{col}' debe contener valores numéricos")


                # Validar si algún DNI del archivo ya existe en la base de datos
                dnis_existentes = set(ClientesBia.objects.values_list('dni', flat=True))
                dnis_nuevos = set(df['dni'].dropna().astype(str))

                dnis_repetidos = dnis_nuevos.intersection(dnis_existentes)
                if dnis_repetidos:
                    errores_tipo.append(
                        f"❌ Ya existe registro en la base de datos con los DNI: {', '.join(dnis_repetidos)}"
                    )
                    
                if errores_tipo:
                    request.session['errores_validacion'] = errores_tipo
                    return redirect('errores_validacion')

                # Marcar visualmente fechas vacías con un estilo HTML
                df_mostrar = df.copy()
                for col in columnas_fecha:
                    if col in df_mostrar.columns:
                        df_mostrar[col] = df_mostrar[col].apply(
                            lambda x: '<span style="color:red;">⚠ Formato de fecha invalida, se guarda la celda vacia</span>' if pd.isna(x) else x
                        )

                vista_previa = df_mostrar.head(5).to_html(classes="table table-bordered", escape=False, index=False)
                datos_serializables = df.astype(str).where(pd.notnull(df), None).to_dict(orient='records')   # Convertir todos los valores a strings y eliminar valores no serializables como Timestamp
                request.session['datos_cargados'] = datos_serializables     # Guardar los datos en sesión                
                return render(request, 'confirmar_carga.html', {'vista_previa': vista_previa})

            except Exception as e:
                mensaje = f"Error al procesar el archivo: {e}"
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})


def limpiar_valor(valor):
    if pd.isna(valor):  # NaN de pandas
        return None
    return valor  # deja fechas como date, y números como están

@login_required
def confirmar_carga(request):
    datos = request.session.get('datos_cargados', [])
    if not datos:
        return redirect('cargar_excel')

    try:
        columnas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
        registros = []

        for fila in datos:
            registro_data = {
                col: limpiar_valor(fila.get(col)) for col in columnas
            }
            registros.append(ClientesBia(**registro_data))

        ClientesBia.objects.bulk_create(registros, batch_size=100)
        mensaje = f"✅ Se cargaron {len(registros)} registros correctamente."

    except Exception as e:
        mensaje = f"❌ Error al guardar los datos: {e}"

    # Limpiar sesión
    request.session.pop('datos_cargados', None)
    return render(request, 'upload_form.html', {
        'form': ExcelUploadForm(),
        'mensaje': mensaje
    })


@login_required
def errores_validacion(request):
    errores = request.session.get('errores_validacion', [])
    if not errores:
        return redirect('cargar_excel')

    if request.GET.get('exportar') == 'txt':
        buffer = StringIO()
        for error in errores:
            buffer.write(f"{error}\n")
        response = HttpResponse(buffer.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="errores_validacion.txt"'
        return response

    return render(request, 'errores_validacion.html', {'errores': errores})