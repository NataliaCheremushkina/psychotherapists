from django.shortcuts import render
from .models import Therapist


def frontend(request, id=None):
    therapists = Therapist.objects.all()
    return render(request, 'therapists/template.html',
                  {'therapists': therapists})
