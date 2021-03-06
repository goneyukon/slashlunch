# -*- coding: utf-8 -*-

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseForbidden
import foursquare
from django.conf import settings
import random
import time

from .models import Company

@require_http_methods(["POST",])
@csrf_exempt

def lunch(request):

    client = foursquare.Foursquare(client_id=settings.FS_CLIENT_ID, client_secret=settings.FS_CLIENT_SECRET)

    slacktoken = request.POST.get('token')
    slackcopy = request.POST.get('text')

    company = Company.objects.get(key__exact=slacktoken)

    if "cheap" in slackcopy and "close" in slackcopy:
        recs = "Hi there! :wave: Here are some cheap and close lunch options:\n"
        venues = client.venues.explore(params={
        'll': company.office,
        'radius': '485',
        'section': 'food',
        'price': '1',
        'openNow': '1'})
    elif "cheap" in slackcopy:
        recs = "Hi there! :wave: Here are some cheap lunch options:\n"
        venues = client.venues.explore(params={
        'll': company.office,
        'radius': company.radius,
        'section': 'food',
        'price': '1',
        'openNow': '1'})
    elif "close" in slackcopy:
        recs = "Hi there! :wave: Here are some close lunch options:\n"
        venues = client.venues.explore(params={
        'll': company.office,
        'radius': '485',
        'section': 'food',
        'price': '1,2',
        'openNow': '1'})
    elif not slackcopy:
        recs = "Hi there! :wave: Here are some lunch options:\n"
        venues = client.venues.explore(params={
        'll': company.office,
        'radius': company.radius,
        'section': 'food',
        'price': '1,2',
        'openNow': '1'})
    else:
        recs = "Hi there! :wave: Here are some options with %s:\n" % (slackcopy)
        venues = client.venues.explore(params={
        'll': company.office,
        'radius': '2900',
        'query': slackcopy,
        'price': '1,2',
        'openNow': '1'})

    places = []

    for groups in venues['groups']:
        for items in groups['items']:

            try:
                url = items['venue']['menu']['url']
            except KeyError:
                url = items['venue'].get('url', '')
            except IndexError:
                pass

            places.append([items['venue']['name'],url])

    if len(places) >= 5: choices = random.sample(places, 5)
    else: choices = random.sample(places, len(places))

    for index, name in enumerate(choices):
        if index == 0: emoji = ":one: "
        if index == 1: emoji = ":two: "
        if index == 2: emoji = ":three: "
        if index == 3: emoji = ":four: "
        if index == 4: emoji = ":five: "
        recs += '%s %s \n%s \n' % (emoji, name[0], name[1])

    if company is None: return HttpResponseForbidden()
    else:
        with open('lunchbot.log', 'a') as f:
            f.write('%s %s %s: %s requested %s in #%s\n' % (time.strftime("%m/%d/%Y"), time.strftime("%I:%M:%S"), request.POST.get('team_domain'), request.POST.get('user_name'), slackcopy, request.POST.get('channel_name')))
            return JsonResponse({"response_type": "in_channel", "text": recs})

@require_http_methods(["POST",])
@csrf_exempt

def AddCompany(request):

    if settings.DEBUG or request.META['HTTP_REFERER'] is u'powerful-anchorage-82986.herokuapp.com':

        cokey = request.POST.get('token')
        coname = request.POST.get('name')
        coradius = request.POST.get('radius')
        cooffice = request.POST.get('ll')

        co = Company(name=coname,key=cokey,office=cooffice,radius=coradius)
        co.save()

        return HttpResponse(status=204)

    else: return HttpResponseForbidden()
