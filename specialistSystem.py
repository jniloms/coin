# This program was made by:
#
# Nilo Martins and Ricardo Paranhos
#
# to a class of Computer Intelligence
#
# by Prof. Fernando Buarque, PhD
#
# from University of Pernambuco – UPE,
# School of Engineering – POLI
#
# Year 2018
#
# This software are licensed by GPLv3
#
# Contact: jniloms@gmail.com

import pandas as pd
import numpy as np
import os
import math
import json
import time
from fuzzy import Fuzzy, TrapezeFuzzyGroup
from lib import splitdataset, loaddataset

# --------------- Definig a fuzzy parameters ---------------------------------------------------------------------------
# Fuzzy with params options to calculate the assurance
# If you needs calibrate your assurance, config here
ab = TrapezeFuzzyGroup(70.0, 80.0, 100.0, 100.0, 256.0, 'absolute')
eh = TrapezeFuzzyGroup(40.0, 45.0, 70.0, 80.0, 64.0, 'exhi')
hi = TrapezeFuzzyGroup(25.0, 30.0, 40.0, 45.0, 16.0, 'hi')
me = TrapezeFuzzyGroup(15.0, 20.0, 25.0, 30.0, 4.0, 'medium')
lo = TrapezeFuzzyGroup(5.0, 10.0, 15.0, 20.0, 1.0, 'low')
fuzzy3 = Fuzzy([ab, hi, me, lo, eh])


# ---------------- Make rules file -------------------------------------------------------------------------------------

# This method make rules file using Fuzzy Logic in calc of assurance
# df1 - Pandas data frame with data of class1
# df2 - Pandas data frame with data of class2
# rulesfilename - full path for save rules files
# column id of categoricals data. This is necessary because is not good reduce the bin size of this data type.
# f - Fuzzy object to use in calc of assurance. In case of you like test more of one.
# return - This method don't return anything, just write a file with rules.
def makerulesFuzzy(df1, df2, rulesfilename, categoricalcolids=[], label1='benign', label2='malware', f=fuzzy3):
    columns = df1.columns

    ONE = -1.0
    TWO = 1.0

    rules = {}
    for i in range(0, len(columns)):

        # define max limit
        max1 = df1[columns[i]].max()
        max2 = df2[columns[i]].max()
        if max2 > max1:
            max = max2
        else:
            max = max1

        # define min limit
        min1 = df1[columns[i]].min()
        min2 = df2[columns[i]].min()
        if min2 < min1:
            min = min2
        else:
            min = min1

        if math.isnan(min) or math.isnan(max):
            # bypass invalid values
            continue

        # define bins size
        if i in categoricalcolids:
            bin = max + 1
        elif max > 100:
            bin = 100
        elif max > 50:
            bin = 50
        elif max > 25:
            bin = 25
        elif max > 10:
            bin = 10
        elif max > 5:
            bin = 5
        elif max > 2:
            bin = 3
        else:
            bin = 2

        # make histogram
        h1, tp1 = np.histogram(df1[columns[i]], bins=bin, range=(min, max), density=False)
        h2, tp1 = np.histogram(df2[columns[i]], bins=bin, range=(min, max), density=False)

        r = []
        general_assurance = 0.0
        c = 0

        for j in range(0, len(h2)):
            total = h1[j] + h2[j]
            if total > 0:
                p1 = h1[j] * 100 / total
                p2 = h2[j] * 100 / total
            else:
                p1, p2 = 0, 0
            relevance = (h1[j] + h2[j]) * 100 / (len(df1.index) + len(df2.index))

            d = abs(p1 - p2)

            assurance = f.fuzzyfy(d)

            if assurance == 0.0:
                # if unkonown, don't write the rule.
                continue

            c += 1
            general_assurance += assurance

            if p1 > p2:
                response = ONE
            else:
                response = TWO

            r.append({'assurance': assurance, 'response': response, 'relevance': relevance, 'rangeini': tp1[j],
                      'rangeend': tp1[j + 1]})

        if c != 0:
            ga = general_assurance / c
        else:
            ga = 0

        ga = f.defuzzyfy(ga)

        if len(r) > 0:
            a = {'rule': r, 'general_assurance': ga}
            rules[columns[i]] = a

    rules = { 'labels': [label1, label2], 'rules' : rules }
    txt = json.dumps(rules, default=str, indent=4)

    with open(rulesfilename, 'w') as f:
        f.write(txt)

# -------------- Analyze file ------------------------------------------------------------------------------------------

# scan file atributs
def scan(fileattributes, columns, rules, DEBUG=False):
    score = 0
    d = []
    for i in range(0, len(fileattributes)):
        resp = 0
        k_selected = None
        currentvalue = fileattributes[i]
        try:
            r = rules[columns[i]]
        except:
            # if rule is not found ignore
            continue
        for k in r['rule']:
            if currentvalue >= k['rangeini'] and currentvalue < k['rangeend']:
                resp = k['assurance'] * k['response'] * math.pow((k['relevance'] / 100 + 1), 2)
                k_selected = k
                break
        score += resp
        if DEBUG:
            d.append((columns[i], resp, (fileattributes[i], k_selected)))

    return score, d


# Analyze a file csv and determine the score of any records
def analyzer(df, rulesfile, columns, DEBUG=False):
    c1 = 0
    c2 = 0
    # load rules file
    with open(rulesfile, 'r') as f:
        fr = json.load(f)
        labels = fr["labels"]
        rules = fr["rules"]
    results = []
    for file in df.values:
        score, d = scan(file, columns, rules, DEBUG=DEBUG)
        if score < 0:
            score = labels[0]
        else:
            score = labels[1]
        if d:
            results.append((score, d))
        else:
            results.append((score))
        if score == labels[1]:
            c2 += 1
        else:
            c1 += 1
    p1 = c1 * 100 / (c1 + c2)
    p2 = c2 * 100 / (c1 + c2)
    return results, labels, [p1, p2]


# -------------- Macro Routines ------------------------------------------------------------------------------------------

# make rule file
def makerulesfile(classonefilename, classtwofilename, rulesfilename, classonename='Class1', classtwoname='Class2'):
    try:
        # Open files in dataframe, all columns not numeric will be ignored
        df1 = loaddataset(classonefilename)
        df2 = loaddataset(classtwofilename)
        makerulesFuzzy(df1, df2, rulesfilename, label1=classonename, label2=classtwoname)
        return True
    except Exception as e:
        print(str(e))
        return False

# analyse file
def analysefile(filenametoanalyse, rulesfilename, resultfilename, columnname):
    try:
        df = loaddataset(filenametoanalyse)
        columns = df.columns
        results, labels, percents = analyzer(df, rulesfilename, columns)
        df = pd.concat([df,pd.DataFrame({ columnname : results })], axis=1)
        df.to_csv(resultfilename,sep=';')
        return '%s = %03.3f%%\n%s = %03.3f%%' % (labels[0], percents[0], labels[1], percents[1])
    except Exception as e:
        print(str(e))
        return None

# make test
def maketests(classonefilename, classtwofilename, rulesfilename, classonename='Class1', classtwoname='Class2', progress=None, root=None):
    try:
        # Open files in dataframe, all columns not numeric will be ignored
        df1 = loaddataset(classonefilename)
        df2 = loaddataset(classtwofilename)
        columns1 = df1.columns
        columns2 = df2.columns
        dir = os.path.dirname(rulesfilename)
        r = os.path.splitext(os.path.basename(rulesfilename))
        results = []
        print('Testing ', end='', flush=True)
        totalhits1 = 0
        totalmistakes1 = 0
        totalhits2 = 0
        totalmistakes2 = 0
        for i in range(50):
            if progress:
                progress.set(i+1)
                if root:
                    root.update()
            print('.', end='', flush=True)
            startsplit = time.time()
            df1training, df1test = splitdataset(df1)
            df2training, df2test = splitdataset(df2)
            rulesfilename = dir + os.path.sep + r[0]+'-test-'+str(i+1)+r[1]
            startRules = time.time()
            makerulesFuzzy(df1training, df2training, rulesfilename, label1=classonename, label2=classtwoname)
            startAnalyse1 = time.time()
            r1, l1, p1 = analyzer(df1test, rulesfilename, columns1)
            startAnalyse2 = time.time()
            r2, l2, p2 = analyzer(df2test, rulesfilename, columns1)
            end = time.time()
            results.append({    'test': i+1,
                                'times' : {
                                    'splitdatasets' : startRules - startsplit,
                                    'makerules': startAnalyse1 - startRules,
                                    'analyseclass1': startAnalyse2 - startAnalyse1,
                                    'analyseclass2': end - startAnalyse2
                                },
                                l1[0] : { 'hits' : p1[0], 'mistakes' : p1[1] },
                                l1[1] : { 'hits' : p2[1], 'mistakes' : p2[0] },
                            })
            totalhits1 += p1[0]
            totalmistakes1 += p1[1]
            totalhits2 += p2[1]
            totalmistakes2 += p2[0]
        average = { 'average' : {
                            l1[0] : { 'hits' : totalhits1 / 50, 'mistakes' : totalmistakes1  / 50 },
                            l1[1] : { 'hits' : totalhits2 / 50, 'mistakes' : totalmistakes2  / 50 },
                        } }
        results.append( average )
        print(average)
        filename = os.path.dirname(rulesfilename)+ os.path.sep + 'analyse-'+time.strftime('%Y%m%d-%H%M')+'.json'
        txt = json.dumps(results, default=str, indent=4)
        with open(filename, 'w') as f:
            f.write(txt)
        return filename
    except Exception as e:
        print(str(e))
        return None



