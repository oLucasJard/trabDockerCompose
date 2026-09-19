from django.shortcuts import redirect, render

from .forms import ArquivoForm
from .models import Arquivo


def upload(request):
    if request.method == "POST":
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("upload")
    else:
        form = ArquivoForm()

    return render(
        request,
        "uploads/upload.html",
        {"form": form, "arquivos": Arquivo.objects.order_by("-enviado_em")},
    )
