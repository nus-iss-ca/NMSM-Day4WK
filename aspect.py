# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:48:19 2015

@author: aditya
"""

from lxml import etree

# Get all dependencies in the parsed Stanford CoreNLP file
def get_dep(gen, tok_list):
    wrd_dep=[]    
    children =  gen.getchildren()
    tok_pos = []    
    for child in children:
        att = child.attrib['type']
        grandchildren = child.getchildren()
        wrd_dep.append([att, grandchildren[0].text, grandchildren[1].text])
    for wrd in wrd_dep:
        for tok in tok_list:
            if wrd[1] == tok[0]:
                wrd[1] = [wrd[1], tok[2], tok[3]]
            if wrd[2] == tok[0]:
                wrd[2] = [wrd[2], tok[2], tok[3]]
        
    return wrd_dep

# Get all "direct object" (dobj) dependencies. “She gave me a raise” => dobj(gave, raise)

def get_dobj(parse_list, word):
    dobj_list = []    
    for p in parse_list:
        for p1 in p[2]:
            if p1[0] == "dobj" and word in [p1[1][0], p1[2][0]]:
                dobj_list.append([p1])
    return(dobj_list)

# Get all "adjectival modifier" (amod) dependencies. “Sam eats red meat” => amod(meat, red)

def get_amod(parse_list, word):
    amod_list = []    
    for p in parse_list:
        for p1 in p[2]:
            if p1[0] == "amod" and word in [p1[1][0], p1[2][0]]:
                amod_list.append([p1])
    return(amod_list)

# Get all "nominal subject" (nsubj) dependencies. “Clinton defeated Dole” => nsubj(defeated, Clinton)

def get_nsubj(parse_list, word):
    nsubj_list = []    
    for p in parse_list:
        for p1 in p[2]:
            if p1[0] == "nsubj" and word in [p1[1][0], p1[2][0]]:
                nsubj_list.append([p1])
    return(nsubj_list)     

# Get all "passive nominal subject" (nsubjpass) dependencies. “Dole was defeated by Clinton” => nsubjpass(defeated, Dole)

def get_nsubjpass(parse_list, word):
    nsubjpass_list = []    
    for p in parse_list:
        for p1 in p[2]:
            if p1[0] == "nsubjpass" and word in [p1[1][0], p1[2][0]]:
                nsubjpass_list.append([p1])
    return(nsubjpass_list)     

# Get all "appositional modifier" (appos) dependencies. "Sam , my brother , arrived" appos(Sam, brother)

def get_appos(parse_list, word):
    nappos_list = []    
    for p in parse_list:
        for p1 in p[2]:
            if p1[0] == "appos" and word in [p1[1][0], p1[2][0]]:
                nappos_list.append([p1])
    return(nappos_list)     

"""Function to get all aspects based on the following algorithm:
1. Identify all sentiment words (Positive, Negative, Very Positive, Very Negative)
2. If the sentiment word is a Verb other than Verb, past participle, then look for either dependencies
"dobj" or "nsubj"
3. If the sentiment word is a Verb, past participle then look for dependency "nsubj"
4. If the sentiment word is an adjective, look for dependencies "nsubj" and "amod"
5. If the sentiment word is a noun, then look for dependencies "nsubj" and "appos"
6. After finding the right dependency, extract the word other than the sentiment word if it is some form of 
a noun
7. The extracted word is your aspect.
"""

def get_aspect(filename):
    # Read in the xml file and parse it
    tree = etree.parse(filename)
    
    # Counter to keep track of the sentences
    count = 1
    # Some intermediary lists needed for data pre-processing
    out_list = []
    senti = []
    
    # Iterate through all sentences
    for df in tree.xpath("//sentences"):
        # Navigating to individual tokens
        one_gen =  df.getchildren() 

        for gen in one_gen:
            next_gen = gen.getchildren()
            for gen1 in next_gen:
                if gen1.tag == 'tokens':
                    tok = []
                    tokens_children = gen1.getchildren()
                    for child in tokens_children:
                        token_children = child.getchildren()
                        # Getting the text (word) from the tokens
                        tk = [t.text for t in token_children if t.tag == "word"][0]
                        # Getting the actual sentiment
                        st = [t.text for t in token_children if t.tag == "sentiment"][0]
                        # Getting the Parts of Speech associated with each token
                        pos = [t.text for t in token_children if t.tag == "POS"][0]
                        #Creating a list with all the above datapoints
                        tok.append([tk, st, pos, child.attrib["id"]])
                        #Creating one list with all Sentiment words
                        if st in ['Positive', 'Negative', 'Very positive', 'Very negative']:
                            senti.append(tk)
                # Getting all the dependencies
                if (len(gen1.attrib)!=0):
                    if gen1.attrib['type'] == "collapsed-ccprocessed-dependencies":
                        dep=get_dep(gen1, tok)
            # Create one mega list of all sentiment tokens and dependencies by each sentence                             
            out_list.append([count, tok, dep])     
            count+=1
    # Apply all the rules as stated in the remarks above this function
    final=[]
    for out in out_list:
        tok = []
        dep = []
        for toks in out[1]:
            if toks[1] in ['Positive', 'Negative', 'Very positive', 'Very negative']:
                tok.append(toks)
        for deps in out[2]:
            if deps[0] in ['dobj', 'amod', 'nsubj', 'nsubjpass', 'appos']:
                dep.append(deps)
        final.append([out[0], tok, dep])   
    # Data Pre-processing to extract all aspects
    all_sent = []
    for f in final:
        if len(f[1]):
            for f1 in f[1]:
                if f1[2].startswith("VB") and f1[2]!="VBN":
                    all_sent.append(get_dobj(final, f1[0]))
                    all_sent.append(get_nsubj(final, f1[0]))
                if f1[2]=="VBN":
                    all_sent.append(get_nsubjpass(final, f1[0]))
                if f1[2].startswith("JJ"):
                    all_sent.append(get_amod(final, f1[0]))
                    all_sent.append(get_nsubj(final, f1[0]))
                if f1[2].startswith("NN"):
                    all_sent.append(get_nsubj(final, f1[0]))
                    all_sent.append(get_appos(final, f1[0]))
    # Data Pre-processing to extract all aspects
    all_s1 = [ x[0][0] for x in all_sent if len(x)] 
    aspects = []
    for s in senti:
        for a in all_s1:
            if s == a[1][0] and a[2][1].startswith("NN"):
                aspects.append(a[2][0])
            elif s == a[2][0] and a[1][1].startswith("NN"):
                aspects.append(a[1][0]) 
    # Return lower case aspects for consistency
                
    aspects = [x.lower() for x in aspects]
    # Return only unique aspects. Many aspects might be extracted, makes no sense to return duplicate aspects
    return(list(set(aspects)))
    




            
