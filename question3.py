# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:37:27 2015

@author: Canh Tran
"""

# To create datasets for wordcloud summarization of positive and negative aspects per restaurant

import os
import collections
import functools
import operator
from collections import Counter
import pandas as pd
import aspect as asp
import aspect_categories as aspc
import aspect_sentiments as asps

def run(path):
    # Assuming that all the xml files are present in your current working directory
    folderList = os.listdir(path)

    # Read in all the xml files - other files such as .py files will be not read in. Extract all aspects to be
    # visualized as wordclouds

    asp_sent_list = []
    for file_name in folderList:
        ext = os.path.splitext(file_name)[-1].lower()
        if ext == ".xml":
            aspects = asp.get_aspect(path + "/" + file_name)
            asp_cat = aspc.get_aspect_categories(aspects)
            # asp_sent = asps.get_aspect_sentiment(aspects, path + "/" + file_name, categories = False)
            if "food" in asp_cat:
                temp_aspects = aspc.get_aspect_by_category(aspects, "food")
                asp_sent = asps.get_aspect_sentiment(temp_aspects, path + "/" + file_name, categories = False)
                asp_sent_list.append([file_name[:-4], temp_aspects, asp_sent])

    # Read in the csv file in question. This is done to match the review ids to the restaurant id
    # because we want to summarize aspects by restaurant
    test = pd.read_csv("charlotte_top10.csv")

    # Create a list with restaurant_ids aspects along with sentimentss
    rev_rest_list = []
    for i, r in test.iterrows():
        for asl in asp_sent_list:
            if r['review_id']==asl[0]:
                rev_rest_list.append([r['restaurant_id'], asl[2] ])

    # Convert list to dataframe for easy handling
    rev_rest = pd.DataFrame(rev_rest_list, columns = ['rest_id','Aspect_Sent'])

    # Create groups by restaurant id
    grouped = rev_rest.groupby('rest_id')

    # Process data so that frequency of each aspect-sentiment pair is counted
    dict_check = []
    temp1 = []
    for g in grouped:
        h = g[1]
        temp = []
        for i,r in h.iterrows():
            c = Counter( item for item in r.Aspect_Sent.items())
            d = dict(c)
            temp.append(d)
            dict_check = functools.reduce(operator.add, map(collections.Counter, temp))
        temp1.append([g[0], dict(dict_check)])

    # Create an empty dataframe with the structure which tableau requires
    columns = ['rest_id', 'Aspect', 'Freq', 'Type']
    temp_df = pd.DataFrame(columns = columns)


    # Fill in the empty dataframe with the list created, separating out negative and positive sentiments by
    # creating a column called "Type" and also storing their frequency in the column "Freq"
    for t in temp1:
        for k,v in t[1].items():
            if k[1] == 'Positive':
                temp_df = temp_df.append({'rest_id': t[0], 'Aspect':k[0], 'Freq': v, 'Type':"Positive"}, ignore_index = True)
            elif k[1] == 'Negative':
                temp_df = temp_df.append({'rest_id': t[0], 'Aspect':k[0], 'Freq': v, 'Type': "Negative"}, ignore_index = True)

    temp_df.to_csv("result/question3.csv", encoding = "UTF-8")
