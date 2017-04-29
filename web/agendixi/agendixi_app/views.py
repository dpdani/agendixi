from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import pymysql
import datetime

from . import forms

# Create your views here.

def index(request):
    con = pymysql.connect(user='agendixi', passwd='fermi', db='agendixi')
    cur = con.cursor()
    cur.execute("SELECT SendAt, Description FROM Events WHERE Sent=0;")
    events = cur.fetchall()
    con.close()
    return render(request, 'index.html', {'events': events})


def add_event(request):
    if request.method == 'POST':
        form = forms.EventForm(request.POST)
        if form.is_valid():
            date = datetime.datetime.strftime(form.cleaned_data['date'], '%Y-%m-%d %H:%M:%S')
            description = form.cleaned_data['description']
            con = pymysql.connect(user='agendixi', passwd='fermi', db='agendixi')
            cur = con.cursor()
            cur.execute("INSERT INTO Events(SendAt, Sent, Description) VALUES ('{}', '0', '{}');".format(date, description))
            con.commit()
            con.close()
            return render(request, 'added.html', {'form': form})
        else:
            print(form._errors)
            return render(request, 'notok.html', {'form': form})
    else:
        form = forms.EventForm()
    return render(request, 'add_event.html', {'form': form})
