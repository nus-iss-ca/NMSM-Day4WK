# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:20:36 2015

@author: aditya
"""
from lxml import etree
from aspect_categories import get_aspect_cat_senti as gacs
from aspect import get_dep
from aspect import get_dobj
from aspect import get_amod
from aspect import get_nsubj
from aspect import get_nsubjpass
from aspect import get_appos
from collections import defaultdict
from operator import itemgetter

# Function to get sentiments if passed the name of the file and the aspects extracted in earlier steps.
def get_aspect_sentiment (aspects, filename, categories = False):
    tree = etree.parse(filename)
    count = 1
    out_list = []
    senti = []
    for df in tree.xpath("//sentences"):
        one_gen =  df.getchildren() 

        for gen in one_gen:
            next_gen = gen.getchildren()
            for gen1 in next_gen:
                if gen1.tag == 'tokens':
                    tok = []
                    tokens_children = gen1.getchildren()
                    for child in tokens_children:
                        token_children = child.getchildren()
                        tk = [t.text for t in token_children if t.tag == "word"][0]
                        st = [t.text for t in token_children if t.tag == "sentiment"][0]
                        pos = [t.text for t in token_children if t.tag == "POS"][0]
                        tok.append([tk, st, pos, child.attrib["id"]])
                        if st in ['Positive', 'Negative', 'Very positive', 'Very negative']:
                            senti.append(tk)
                if (len(gen1.attrib)!=0):
                    if gen1.attrib['type'] == "collapsed-ccprocessed-dependencies":
                        dep=get_dep(gen1, tok)
                                          
            out_list.append([count, tok, dep])     
            count+=1
    final=[]
    for out in out_list:
        tok = []
        dep = []
        for toks in out[1]:
            if toks[1] in ['Positive', 'Negative', 'Very positive', 'Very negative']:
                tok.append(toks)
        for deps in out[2]:
            if deps[0] in ['dobj', 'amod', 'nsubj', 'nsubjpass', 'appos', 'neg']:
                dep.append(deps)
                #print dep
        final.append([out[0], tok, dep])   
    
    # Convert the verbose sentiments like "Positive", "Very negative" etc to +1, -1
    for f in final:
        for f1 in f[1]:
            if f1[1] == "Negative" or f1[1]=="Very negative":
                f1[1] = -1
            else:
                f1[1] = 1
                
    # Reverse polarity for negative sentiments like "not good", "not bad" etc.
    for a in aspects:
        for f in final:
            for f1 in f[1]:
                sent_temp = f1[0]
                for f2 in f[2]:
                    if f2[0] == "neg" and sent_temp == f2[1][0]:
                        f1[1] = -1*f1[1]
                        
    # Calculate the total sentiment score for each aspect
    tot_sentiment = []
    for a in aspects:
        for f in final:
            for f1 in f[2]:
                if len(f1):
                    temp1 = f1[1:]
                else:
                    continue
                #print temp1
                for t in temp1:
                    if a == t[0].lower():
                        temp2 = [x for x in temp1 if x != t]
                        tot_sent = 0
                        for f2 in f[1]:
                            sent_temp = f2[0]
                            sent_type = f2[1]
                            sent_ix = f2[3]
                            for t2 in temp2:
                                if sent_temp == t2[0]:
                                    tot_sent+=sent_type
                        tot_sentiment.append([t[0].lower(), tot_sent])
    
    
    d = defaultdict(int)
    for item in tot_sentiment:
        d[item[0]] += item[1]
    d1 = dict(d)
    d2 = {k:'Positive' if v > 0 else 'Negative' for (k,v) in d1.items()}
    
    aspect_senti_list = []
    for key, value in d1.iteritems():
        temp = [key,value]
        aspect_senti_list.append(temp)

    if not categories:
        return d2
    elif categories:
        return gacs(aspects, aspect_senti_list)
    
    
    