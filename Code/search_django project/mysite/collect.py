# _*_ coding:UTF-8 _*_

from elasticsearch import Elasticsearch

class ElasticObj(object):
    def __init__(self,ip):#ip=["172.21.201.147:9204"]
        self.client=Elasticsearch(
            ip
        )

    def QuertData(self,str):#str=""
        response=self.client.search(
            index= "nyt_articles",
            body={
                "query":{
                    "match":{
                        "articleBody": str
                    }},
                "size":100,
                "highlight":{
                    "pre_tags":['<span class="keyWord">'],
                    "post_tags":['</span>'],
                    "fields":{
                        "articleBody":{}                       
                    }

                }
            }
        )
        return response

# es=ElasticObj(["172.21.201.147:9204"])
# response = es.QuertData("")
# print(response)
# count = 1
# for hit in response['hits']['hits']:
#     print(hit["_source"]["title"][0] +" " +str(count))
#     count = int(count) + 1
# print(response['hits']['total'])
# print(response['took'])