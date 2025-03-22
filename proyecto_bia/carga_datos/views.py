import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import ExcelUploadForm
from .models import ClientesBia

@login_required
def cargar_excel(request):
    mensaje = ""
    
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)

                # Validación básica de columnas
                columnas_requeridas = [f.name for f in ClientesBia._meta.fields if f.name != 'id']
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    mensaje = f"Faltan columnas obligatorias: {faltantes}"
                    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

                # Limpiar y convertir tipos de datos
                df = df.where(pd.notnull(df), None)  # Reemplaza NaN con None

                registros = []
                for _, fila in df.iterrows():
                    registro = ClientesBia(
                        **{col: fila.get(col) for col in columnas_requeridas}
                    )
                    registros.append(registro)

                ClientesBIA.objects.bulk_create(registros, batch_size=100)

                mensaje = "Archivo cargado correctamente."

            except Exception as e:
                mensaje = f"Error al procesar el archivo: {e}"
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_form.html', {'form': form, 'mensaje': mensaje})

