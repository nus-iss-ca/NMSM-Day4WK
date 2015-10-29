# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 21:02:49 2015

@author: aditya
"""
import re
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from operator import itemgetter

# Create a list of food items from wordnet
food_list = []
for synset in wn.all_synsets():
    if synset.lexname == "noun.food":
        food_list.append(re.findall(r"[\w']+", synset.name)[0])

# Addding some which I found missing. You can add more.
food_list.extend(["burger", "fry"])

# Create a list which will have some words associated with general ambience and feel of the restaurant
ambience_list = ['yard','bar','patio','corridor','table','experience', 'romantic', 'restaurant', 'thing','hotel', 'fake', 'wall', 'chair', 'location', 'theme', 'place', 'decor']

# Create a list which will have some words associated with general service of the restaurant
service_list = ['owner','skill','courteous', 'warm', 'friendly', 'staff', 'service', 'skillful', 'waiter', 'waitress', 'manager', 'quality', 'cook', 'chef', 'bartender','hostess', 'server', 'patience', 'behavior', 'asshole']

# Create a list which will have some words associated with general price-offerings of the restaurant
price_list = ['value', 'money', 'dollar', 'price', 'overprice', 'bargain']

"""Function which will take all extracted aspects and categorize them into "food",
"ambience", "price", "service" and "others" """

def get_aspect_categories(aspects):
    wm = WordNetLemmatizer()
    categories = []
    for a in aspects:
        asp_lem = wm.lemmatize(a)
        if asp_lem in food_list:
            categories.append('food')
        elif asp_lem in ambience_list:
            categories.append('ambience')
        elif asp_lem in price_list:
            categories.append('price')
        elif asp_lem in service_list:
            categories.append('service')
        else:
            categories.append('others')
    return list(set(categories))

def get_dictionary_by_category(category):
    if category == 'food':
        return food_list
    elif category == 'ambience':
        return ambience_list
    elif category == 'price':
        return price_list
    elif category == 'service':
        return service_list
    else:
        return []

def get_aspect_by_category(aspects, category):
    wm = WordNetLemmatizer()
    aspects_result = []
    category_list = get_dictionary_by_category(category)
    for a in aspects:
        asp_lem = wm.lemmatize(a)
        if asp_lem in category_list:
            aspects_result.append(a)
    return list(set(aspects_result))

"""Function definition for categorizing aspect categories as Positive or Negative.
To be called from aspect_sentiments module"""

def get_aspect_cat_senti(aspects, aspect_senti_list):
    wm = WordNetLemmatizer()
    food_senti, ambience_senti, price_senti, service_senti, others_senti=0,0,0,0,0
    categories = []
    for a in aspects:
        asp_lem = wm.lemmatize(a)
        if asp_lem in food_list:
            for asl in aspect_senti_list:
                if a == asl[0]:
                    food_senti+=asl[1]
            categories.append(['food', food_senti])

        elif asp_lem in ambience_list:
            for asl in aspect_senti_list:
                if a == asl[0]:
                    ambience_senti+=asl[1]
            categories.append(['ambience', ambience_senti])

        elif asp_lem in price_list:
            for asl in aspect_senti_list:
                if a == asl[0]:
                    price_senti+=asl[1]
            categories.append(['price', price_senti])

        elif asp_lem in service_list:
            for asl in aspect_senti_list:
                if a == asl[0]:
                    service_senti+=asl[1]
            categories.append(['service', service_senti])

        else:
            for asl in aspect_senti_list:
                if a == asl[0]:
                    others_senti+=asl[1]
            categories.append(['others', others_senti])

    d = defaultdict(int)
    for item in categories:
        d[item[0]] += item[1]
    d1 = dict(d)
    d2 = {k:'Positive' if v > 0 else 'Negative' for (k,v) in d1.items()}
    return d2
