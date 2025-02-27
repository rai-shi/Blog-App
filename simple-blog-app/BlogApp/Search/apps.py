from django.apps import AppConfig
from elasticsearch_dsl.connections import connections
from .indexes import UserIndex, BlogIndex

class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Search'

    def ready(self):
        connections.create_connection(hosts=["http://localhost:9200"])
        UserIndex.init()
        BlogIndex.init()
        print("Elasticsearch connected and indexes created")
        


# from elasticsearch.helpers import bulk
# from elasticsearch import Elasticsearch

# def bulk_indexing():
#     Index.init()
#     es = Elasticsearch()
#     bulk(client=es, actions=(b.indexing() for b in models.ModelName.objects.all().iterator()))