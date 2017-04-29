from django import forms
import datetime

class EventForm(forms.Form):
    description = forms.CharField(label='Event description', max_length=1000)
    date = forms.DateTimeField(label='Event date', initial=datetime.date.today)
