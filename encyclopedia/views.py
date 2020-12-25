from django import forms
from django.shortcuts import render
from django.http import HttpResponse

import numpy
from numpy import random
from random import choice

from markdown2 import Markdown
markdowner = Markdown()

from . import util

class SearchEncyclopedia(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}), label="Search Encyclopedia")

class NewPage(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control col-md-5', 'placeholder': 'title'}), label="")
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8', 'rows' : 8, 'placeholder': 'content'}), label="")

class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8', 'rows' : 8}), label="")

def index(request):
    if request.method == "POST":
        form = SearchEncyclopedia(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            f_text = util.get_entry(search)
            if f_text:
                return render(request, "encyclopedia/wiki.html", {
                    "title": search, "text": Markdown().convert(f_text),
                    "form": SearchEncyclopedia()
                })
            else:
                ls = []
                for it in util.list_entries():
                    if search.lower() in it.lower():
                        ls.append(it)
                if ls:
                    return render(request, "encyclopedia/search.html", {
                    "entries": ls, "form": SearchEncyclopedia()
                    })
                else:
                    return render(request, "encyclopedia/notfound.html",{
                        "form": SearchEncyclopedia()
                    })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(), "form": form
            })
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(), "form": SearchEncyclopedia()
        })


def wiki(request, title):
    f_text = util.get_entry(title)
    if f_text:
        return render(request, "encyclopedia/wiki.html", {
            "title": title, "text": Markdown().convert(f_text),
            "form": SearchEncyclopedia()
        })
    else:
        return render(request, "encyclopedia/notfound.html", {
            "form": SearchEncyclopedia()
        })


def random(request):
    title = choice(util.list_entries())
    f_text = util.get_entry(title)
    return render(request, "encyclopedia/wiki.html", {
        "title": title, "text": Markdown().convert(f_text),
        "form": SearchEncyclopedia()
    }) 

def create(request):
    if request.method == "POST":
        form = NewPage(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title not in util.list_entries():
                util.save_entry(title, content)
                return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries(), "form": SearchEncyclopedia() 
                })
            else:
                return render(request, "encyclopedia/create.html", {
                    "form": SearchEncyclopedia(), "key": 2, "form2": form
                })
    else:
        return render(request, "encyclopedia/create.html", {
            "form": SearchEncyclopedia(), "key": 1, "form2": NewPage()
        })

def edit(request, title):
    if request.method == 'GET':
        f_text = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {"form": SearchEncyclopedia(), 'title': title,
            "form2": EditPage(initial={'content': f_text})
        })
    else:
        form = EditPage(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content) 
            return render(request, "encyclopedia/wiki.html", {
                "title": title, "text": Markdown().convert(util.get_entry(title)),
                "form": SearchEncyclopedia()
            })
            




   
