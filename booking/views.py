import json
import datetime
import math
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import timedelta, date
from django.http import HttpResponseBadRequest
from django.db.models import Avg


from .models import User, Hotels, Reservations, Comments

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def index(request):
    if request.method == "POST":
        city = request.POST["city"]
        inn_date = request.POST["calendar"]
        outt_date = request.POST["calend"]
        allhot = Hotels.objects.filter(city=city)

        if not allhot:
            return HttpResponseBadRequest("Bad Request: Sorry, there are no hotels in this city")
        elif not inn_date:
            return HttpResponseBadRequest("Bad Request: Enter Arrival date")
        elif not outt_date:
            return HttpResponseBadRequest("Bad Request: Enter Departure date")
        else:

            start_date = date(int(inn_date[0:4]), int(inn_date[5:7]), int(inn_date[8:10]))
            end_date = date(int(outt_date[0:4]), int(outt_date[5:7]), int(outt_date[8:10]))

            tod = datetime.date.today()
            
            if start_date < tod:
                return HttpResponseBadRequest("Bad Request: Arrival date must be greater or equal today's date")
                
            elif inn_date >= outt_date:
                return HttpResponseBadRequest("Bad Request: Arrival date must be greater than departure date")
                
            else:

                okhot = []
                idhot = []
                for ht1 in allhot:
                    ht2 = Reservations.objects.filter(res_hotel=ht1)
                    if ht2:
                        
                        for dt in daterange(start_date, end_date):
                            nb = ht1.free_place
                            if Reservations.objects.filter(res_hotel=ht1, res_date_in=dt).count() > nb - 1:
                                tt = 1
                                break
                            else:
                                tt = 0
                        if tt != 1:
                            okhot.append(ht1)
                            idhot.append(ht1.id)
                    else:
                        okhot.append(ht1)
                        idhot.append(ht1.id)

                ttdel = end_date - start_date
                numb_days = math.ceil(ttdel.days)

                hot = Hotels.objects.filter(id__in=idhot)

                rat_hot = hot.order_by('-rating')
                inc_price_hot = hot.order_by('price')
                dec_price_hot = hot.order_by('-price')
                
                return render(request, "booking/city_hotels.html", {
                    "rat_hot": rat_hot, "inc_price_hot": inc_price_hot, "dec_price_hot": dec_price_hot,
                    "inn_date": inn_date, "outt_date": outt_date, "numb_days": numb_days
                    })
    else:
        return render(request, "booking/index.html")



def city_hotels(request, item_id):
    if request.method == "POST":
        inn_date = request.POST["inn_date"]
        outt_date = request.POST["outt_date"]
        numb_days = int(request.POST["numb_days"])

        thishot = Hotels.objects.get(id=item_id)
        return render(request, "booking/book.html", {
            "thishot": thishot, "inn_date": inn_date, "outt_date": outt_date, "numb_days": numb_days
            })
    

def book(request, item_id):
    if request.method == "POST":
        inn_date = request.POST["inn_date"]
        outt_date = request.POST["outt_date"]
        numb_days = request.POST["numb_days"]

        start_date = date(int(inn_date[0:4]), int(inn_date[5:7]), int(inn_date[8:10]))
        end_date = date(int(outt_date[0:4]), int(outt_date[5:7]), int(outt_date[8:10]))


        ht1 = Hotels.objects.get(id=item_id)
        nb = ht1.free_place
        for dt in daterange(start_date, end_date):
            if Reservations.objects.filter(res_hotel=ht1, res_date_in=dt).count() > nb - 1:
                tt = 1
                break
            else:
                tt = 0        

        if tt == 0:        
            Reservations.objects.create(res_hotel=Hotels.objects.get(id=item_id), res_date_in=inn_date, res_date_out=outt_date, numb_days=int(numb_days), guest=request.user)
            
            return HttpResponseRedirect(reverse("us_booking"))
            
        else:
            return HttpResponseBadRequest("Bad Request: Unfortunately, there are no more rooms available for the dates you selected.")



@login_required
def create(request):
    if request.method == "POST":
        hot_name = request.POST["hot_name"]
        if not hot_name:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Name")
        description = request.POST["description"]
        if not description:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Description")
        try:
            photo = request.FILES["photo"]
        except:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Photo")
        city = request.POST["city"]
        if not city:
            return HttpResponseBadRequest("Bad Request: You should add City")       
        price = request.POST["price"]
        if not price:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Price")
        free_place = request.POST["free_place"]
        if not free_place:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Number of Rooms")
        
        Hotels.objects.create(city=city, hot_name=hot_name, description=description, owner=request.user, free_place=int(free_place), price=int(price), photo=photo)
        
        return HttpResponseRedirect(reverse("us_hotels"))
    
    else:
        return render(request, "booking/create.html")


@login_required
def us_hotels(request):
    if request.method == "GET":
        return render(request, "booking/us_hotels.html", {
            "us_hotels": Hotels.objects.filter(owner=request.user)
        })


@login_required
def us_booking(request):
    if request.method == "GET":
        reservation = Reservations.objects.filter(guest=request.user, res_date_out__gt=datetime.date.today()).order_by('res_date_in')
        return render(request, "booking/us_booking.html", {
            "us_booking": reservation
        })



@login_required
def us_old_booking(request):
    if request.method == "GET":
        reservation = Reservations.objects.filter(guest=request.user, res_date_out__lte=datetime.date.today()).order_by('res_date_in')
        return render(request, "booking/us_old_booking.html", {
            "us_old_booking": reservation
        })


@csrf_exempt
@login_required
def comment(request, item_id):
    if request.method == "POST":
        comm_body = request.POST["comm-body"]
        reservation = Reservations.objects.get(id=item_id)
        hotel = reservation.res_hotel
        liv_date_in = reservation.res_date_in
        liv_date_out = reservation.res_date_out
        Comments.objects.create(com_hotel=hotel, com_us=request.user, liv_date_in=liv_date_in, liv_date_out=liv_date_out, com_text=comm_body)
        return HttpResponseRedirect(reverse("us_old_booking"))

@csrf_exempt
@login_required
def comm_us(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reserv_id = data["reserv_id"]
        res = Reservations.objects.get(id=reserv_id)
        hot = res.res_hotel
        comments = Comments.objects.filter(com_hotel=hot, com_us=request.user)
        return JsonResponse([comment.serialize() for comment in comments], safe=False)


@csrf_exempt
def all_comm(request):
    if request.method == "POST":
        data = json.loads(request.body)
        hot_id = data["hot_id"]
        hot = Hotels.objects.get(id=hot_id)
        comments = Comments.objects.filter(com_hotel=hot).order_by('-timestamp')
        return JsonResponse([comment.serialize() for comment in comments], safe=False)


    

@csrf_exempt
@login_required
def rat(request, item_id):
    if request.method == "POST":
        rat_body = request.POST["rat-body"]        
        reservation = Reservations.objects.get(id=item_id)
        
        reservation.is_rating = True
        reservation.us_rat = int(rat_body)
        reservation.save()

        hotel = reservation.res_hotel
        rs = Reservations.objects.filter(res_hotel=hotel, is_rating=True).aggregate(av=Avg('us_rat'))
        hotel.rating = rs["av"]
        hotel.save()
        
        return HttpResponseRedirect(reverse("us_old_booking"))

@csrf_exempt
@login_required
def del_book(request, item_id):
    if request.method == "GET":
        return render(request, "booking/del_book.html", {
            "del_book": Reservations.objects.get(id=item_id)
        })


@csrf_exempt
@login_required
def conf_del_book(request, item_id):
    Reservations.objects.get(id=item_id).delete()
    return HttpResponseRedirect(reverse("us_booking"))



@csrf_exempt
@login_required
def edit_hot(request, item_id):
    if request.method == "GET":
        return render(request, "booking/edit_hot.html", {
                "edit_hot": Hotels.objects.get(id=item_id)
            })
    else:
        hot_name = request.POST["hot_name"]
        if not hot_name:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Name")
        description = request.POST["description"]
        if not description:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Description")       
        tt=1
        try:
            photo = request.FILES["photo"]
        except:
            tt=2
        city = request.POST["city"]
        if not city:
            return HttpResponseBadRequest("Bad Request: You should add City")       
        price = request.POST["price"]
        if not price:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Price")
        free_place = request.POST["free_place"]
        if not free_place:
            return HttpResponseBadRequest("Bad Request: You should add Hotel's Number of Rooms")
        

        Hotels.objects.filter(id=item_id).update(city=city, hot_name=hot_name, description=description, owner=request.user,
                                                 free_place=int(free_place), price=int(price))
        
        if tt==1:
            hot = Hotels.objects.get(id=item_id)
            hot.photo = photo
            hot.save()

        return HttpResponseRedirect(reverse("us_hotels"))
    
    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "booking/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "booking/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "booking/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "booking/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "booking/register.html")
