# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 13:39:52 2015

@author: Canh Tran
"""


# To create overall summary visualizations

import pandasql
from pandasql import *
import pandas as pd

def run():
    # Read in the csv file in question
    test_sql = pd.read_csv('charlotte_top10.csv', encoding='latin-1')
    temp_dictionary = {'test_sql': test_sql}

    # Initiate pysqldf to enable sql-like querying in python
    pysqldf = lambda q: sqldf(q, temp_dictionary)

    # Write your query, counting positive and negative reviews by restaurant
    q  = """
    SELECT
    m.restaurant_id, m.Sentiment, count(*) as Freq
    FROM
        test_sql m
    GROUP BY
        m.restaurant_id, m.Sentiment;
    """

    # Create a dataframe with the result of the query
    for_overall = pysqldf(q)

    # Write to file
    for_overall.to_csv("result/question1.csv")
