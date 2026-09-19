from django.db import models


class Arquivo(models.Model):
    titulo = models.CharField(max_length=120)
    arquivo = models.FileField(upload_to="arquivos/")
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
