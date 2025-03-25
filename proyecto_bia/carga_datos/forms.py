from django import forms

class ExcelUploadForm(forms.Form):
    archivo = forms.FileField(label="Seleccionar archivo Excel")

def clean_archivo(self):
    archivo = self.cleaned_data['archivo']
    if archivo.size > 5*1024*1024:
        raise forms.ValidationError("El archivo no puede superar los 5MB.")
    return archivo