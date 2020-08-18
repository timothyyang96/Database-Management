# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response,render
from mysite.collect import ElasticObj
from matplotlib import pylab
from pylab import *
from io import StringIO
import PIL, PIL.Image

import matplotlib
import matplotlib.pyplot as plt, mpld3
import numpy as np

import io
from io import BytesIO
import base64


import pandas as pd
import seaborn as sns
matplotlib.style.use('ggplot')

## Search form
def search_form(request):
    return render_to_response('search_form.html')

## Receive the request data
def search(request):
    request.encoding = 'utf-8'
    es = ElasticObj(["127.0.0.1:9200"])
    if 'q' in request.GET:
        response = es.QuertData(request.GET.get('q'))
        message=request.GET.get('q')
        clearesponse=[]
        count = 0
        for hit in response['hits']['hits']:
            cleares={}
            cleares['source'] = hit['_source']
            cleares['source']['headline'] = cleares['source']['headline']
            if "articleBody" in hit['highlight']:
                cleares['source']["articleBody"]=''.join(hit["highlight"]["articleBody"])
            else:
                cleares['source']['articleBody'] = ' '.join(cleares['source']['articleBody'])
            cleares['index']=hit['_index']
            cleares['type'] = hit['_type']
            cleares['id'] = hit['_id']
            cleares['score'] = hit['_score']
            cleares['source']['web_url'] = cleares['source']['web_url']
            cleares['source']['words'] = cleares['source']['words']
            clearesponse.append(cleares)
            count += 1
            if count >= 10:
                break
        result_count=response['hits']['total']['value']#
        last_seconds = response['took']/1000.0#
        page_nums=int(result_count/10)+1  #
    else:
        message = 'The keyword is empty!'
    
    ## Similarity of two articles in the result
    
    # Pick top 10 articles
    N = len(clearesponse)
    if N > 10:
        N = 10
    D = [[0 for i in range(N)] for j in range(N)]        
    
    # Find the intersection of the word lists of two articles
    for i in range(N):
        s1 = set(clearesponse[i]['source']['words'])
        for j in range(i+1,N):
            s2 = set(clearesponse[j]['source']['words'])
            D[i][j] = len(s1 & s2) * 2 / (len(s1) + len(s2))
            D[j][i] = D[i][j]
    
    # Form the relational matrix into a dataframe
    # Use matplotlib to plot the heatmap of 10*10 relations
    d = pd.DataFrame(D)
    cols = [i for i in range(1,11)]
    sns.set(font_scale=2)
    fig, ax = plt.subplots(figsize=(12, 9))
    ax = plt.axes()
    mask = np.zeros_like(d, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    ax.set_title('Similarity Between 2 Articles in 10 Results').set_size(23)
    hm = sns.heatmap(d, cbar=True,annot=True, mask=mask, square=True, ax = ax, fmt='.2f', annot_kws={'size': 20}, yticklabels=cols, xticklabels=cols)

    # Output the plot to the front end
    img = io.BytesIO()
    fig.savefig(img,format='png',bbox_inches='tight')
    img.seek(0)
    encoded=base64.b64encode(img.getvalue())
    my_html = '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
    
    ## Return strings of the result for rendering
    return render(request,"result.html",{"all_hits":clearesponse,
                                          "result_count":result_count,
                                          "last_seconds":last_seconds,
                                          "page_nums":page_nums,
                                          "message":message,
                                          "my_html":my_html})