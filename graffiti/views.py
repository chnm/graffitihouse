from django.shortcuts import render

from .forms import GraffitiForm


def create_graffiti(request):
    template_name = "templates/create_graffiti.html"
    form = GraffitiForm(request.GET)

    return render(request, template_name, {"form": form})
