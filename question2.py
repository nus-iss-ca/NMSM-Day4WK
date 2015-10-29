# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 23:27:28 2015

@author: Canh Tran
"""

# Visualizing aspects

import os
import aspect as asp
import aspect_categories as aspc
import aspect_sentiments as asps
import pandas as pd

# Some checking functions
def check(t, f):
        try:
            return(t[5][f])
        except KeyError:
            return ''

def get_group_size(group, groupby):
        try:
            temp = group.get_group(groupby)
        except KeyError:
            return 0
        return temp.shape[0]

# Function to get data in the required format by the given time grain ("month" and "year" are the two)
# accepted values for now

def run(path, file_name, time_grain):
    folderList = os.listdir(path)
    aspect_list = []
    # Read in the csv file in question
    test = pd.read_csv(file_name)
    # Create two fields of "year" and "month" which will store the extracted year and month
    # from the date
    test_check = test
    test_check['year'] = pd.DatetimeIndex(test_check['date']).year
    test_check['month'] = pd.DatetimeIndex(test_check['date']).month

    # Assuming all your xml files are present in the same path, extract all aspects from the reviews and store
    # them in a list
    for file_name in folderList:
        ext = os.path.splitext(file_name)[-1].lower()
        if ext == ".xml":
            print("Processing ..." + str(file_name[:-4]))
            aspects = asp.get_aspect(path + "/" + file_name)
            asp_cat = aspc.get_aspect_categories(aspects)
            asp_sent = asps.get_aspect_sentiment(aspects, path + "/" + file_name, categories = True)
            aspect_list.append([file_name[:-4], asp_cat, asp_sent])

    # Create an empty dataframe with the below structure
    columns = ['rest_id', 'rev_id', 'year','month','overall_sentiment','food','price','service','ambience','others']
    vis_df = pd.DataFrame(columns=columns)

    # We have to start attaching the reviews to restaurants, create an empty list to do that
    tot_list = []
    # Populate the list
    for i, r in test_check.iterrows():
        for al in aspect_list:
            print("................")
            if r['review_id'] == al[0]:
                tot_list.append([r['restaurant_id'],r['review_id'],r['year'],r['month'], r['Sentiment'], al[2] ])

    # Populate the list
    for l in tot_list:
        food_val = check(l,'food')
        price_val = check(l,'price')
        service_val = check(l,'service')
        ambience_val = check(l,'ambience')
        others_val = check(l,'others')
        vis_df = vis_df.append({'rest_id': l[0], 'rev_id':l[1], 'year':l[2], 'month':l[3],'overall_sentiment':l[4], 'food':food_val, 'price':price_val, 'service':service_val, 'ambience':ambience_val, 'others':others_val }, ignore_index=True)

    # Create an empty dataframe with the below structure and which will hold actual sentiment positive to
    # overall ratios
    columns = ['rest_id', time_grain,'overall', 'food','price','service','ambience','others']
    rest_df = pd.DataFrame(columns=columns)

    # Group your initial dataframe by restaurant id
    grouped = vis_df.groupby('rest_id')


    # Looping through each restaurant
    for g in grouped:
        h = g[1]
        # Grouping by time_grain (example month or year)
        g_child = h.groupby(time_grain)
        # Looping through each time_grain (example month or year)
        for gc in g_child:
            h1 = gc[1]
            # Calculating all ratios
            g_over = h1.groupby('overall_sentiment')
            over_ratio = get_group_size(g_over, "positive")/float(h1.shape[0])
            g_food = h1.groupby('food')
            food_ratio =  get_group_size(g_food, "Positive")/float(h1.shape[0])
            g_price = h1.groupby('price')
            price_ratio =  get_group_size(g_price, "Positive")/float(h1.shape[0])
            g_service = h1.groupby("service")
            service_ratio =  get_group_size(g_service, "Positive")/float(h1.shape[0])
            g_ambience = h1.groupby("ambience")
            ambience_ratio =  get_group_size(g_ambience, "Positive")/float(h1.shape[0])
            g_others = h1.groupby("others")
            others_ratio =  get_group_size(g_others, "Positive")/float(h1.shape[0])
            rest_df = rest_df.append({'rest_id': g[0],time_grain:gc[0], 'overall':over_ratio, 'food':food_ratio, 'price':price_ratio, 'service':service_ratio, 'ambience':ambience_ratio, 'others':others_ratio }, ignore_index=True)
    # Writing to file
    rest_df.to_csv("result/question2.csv")
