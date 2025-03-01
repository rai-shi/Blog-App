from django.shortcuts import render

# rest framework dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import IsAuthenticated

# swagger documentation libs
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# other requirements
from .indexes import *
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

es = Elasticsearch(['http://localhost:9200'])


class SearchUserView(APIView):
    def get(self, request):

        if not bool(request.query_params):
            # get all users by sorting their blogs count 
            search = Search(using=es, index="blog_index") 
            
            search.aggs.bucket("users_by_blog_count", # aggr name
                                "terms", # term aggregation
                                field="author_username", 
                                size=10,  
                                order={"_count": "desc"}  
                            )
            response = search.execute()

            results = [
                {"username": bucket.key, "blog_count": bucket.doc_count}
                for bucket in response.aggregations.users_by_blog_count.buckets
            ]
            return Response({
                    "results":results,
                    "response": response.to_dict()
                    },
                    status=status.HTTP_200_OK
            )

            # return Response(
            #     {"error": "Query parameter is required"},
            #     status=status.HTTP_400_BAD_REQUEST
            # )
        
        search = UserIndex.search()
        # multi match search
        # search with full_name and username
        if request.query_params.get('user'):
            query = request.query_params.get('user')
            search_query = search.query("multi_match", 
                                        query=query, 
                                        fields=["full_name", "username"])
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
        
        # term search with username
        elif request.query_params.get('username'):
            query = request.query_params.get('username')
            search_query = search.query("term", 
                                        username=query)
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
        
        # search user blogs by category
        elif request.query_params.get('user-blogs') and request.query_params.get('category'):
            print("user-blogs and category")
            username = request.query_params.get('user-blogs')
            category = request.query_params.get('category')
            search = BlogIndex.search().query("bool", 
                                              must=[Q("term", author_username=username),
                                                    Q("nested", 
                                                        path="categories", 
                                                        query=Q("term", categories__name=category))])
            response = search.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
        
        # returns users matched with specific category
        elif request.query_params.get('category'):
            print("category")
            query = request.query_params.get('category')
            search_query = search.query("match", 
                                        profile__categories__name=query)
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )

        # returns user all blogs
        elif request.query_params.get('user-blogs'):
            print("user-blogs")
            query = request.query_params.get('user-blogs')
            search = BlogIndex.search().query("term", 
                                              author_username=query)
            response = search.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
    
        else:
            return Response(
                {"error": "Query parameter is unknown"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SearchBlogView(APIView):
    def get(self, request):

        # gell all blogs by sorting like_count and comment_count
        if not bool(request.query_params):
            search = BlogIndex.search().query("match_all").sort(
                {"like_count": {"order": "desc"}},
                {"comment_count": {"order": "desc"}}
            ).extra(size=5) # default 10
            results = search.execute()

            return Response(
                # {"results": [hit.to_dict() for hit in results]},
                {"results": results.to_dict()},
                status=status.HTTP_200_OK
            )
        
        # search with keyword in title, description and content
        if request.query_params.get("keyword"):
            query = request.query_params.get("keyword")
            search = BlogIndex.search().query(
                "multi_match", 
                query=query, 
                fields=["title", "description", "content"]
            ).extra(size=5)
            results = search.execute()

            return Response(
                # {"results": [hit.to_dict() for hit in results]},
                {"results": results.to_dict()},
                status=status.HTTP_200_OK
            )
        
        # gets all blogs by specific category
        elif request.query_params.get("category"):
            query = request.query_params.get("category")  

            search_query =  BlogIndex.search().query(
                                                "nested", 
                                                path="categories", 
                                                query=Q("term", 
                                                        categories__name=query.capitalize())).sort(
                                                                {"like_count": {"order": "desc"}},
                                                                {"comment_count": {"order": "desc"}}
                                                            )
            # term, match, wildcard, case sensitive slug kullanılacak
            # query=Q("match_all"))
            results = search_query.execute()

            return Response(
                # {"results": [hit.to_dict() for hit in results]},
                {"results": results.to_dict()},
                status=status.HTTP_200_OK)

        else:
            return Response(
                {"error": "Query parameter is unknown"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
"""
{
"query": {
            "multi_match": {
            "query": "keyword",
            "fields": ["title", "description", "content"]
            }
        },
"sort": [
    { "like_count": { "order": "desc" } },
    { "comment_count": { "order": "desc" } }
  ]
}
"""


    
"""
    curl -X POST "http://localhost:9200/user_index/_search?pretty" -H "Content-Type: application/json" -d '{
        "query": {
            "match": {
            "query": "q",
            "fields": ["full_name", "username", "profile.bio"]
            }
        }
    }'

    search_query = search.query("nested", 
                                        path="profile.categories", 
                                        query=Q("match", profile__categories=query))
            response = search_query.execute()
"""
    


"""
leaf queries
- match
    - match
    - match_phrase
    - match_phrase_prefix
    - multi_match
    - match_all
- term  
    - term
    - terms
    - range
    - exists
- joining
    - nested
    - has_child
    - has_parent
    - parent_id


    - prefix
    - wildcard
    - regexp
    - fuzzy
    - type
    - ids
    - constant_score
    - query_string
    - simple_query_string
    - script
    - percolate
    - wrapper

    
compound
    sort?
    - constant_score
    - bool
        - must
        - filter
        - should
        - must_not
        - minimum_should_match
    - boosting
        - dis_max
        - function_score

    - boost
    - disable_coord
    - adjust_pure_negative
    - query_name 
    - indices
    - nested
    - has_child
    - has_parent
    - parent_id
    - percolate
    - script
    - score
    - search
    - search_as_you_type
    - span
    - span_near
    - span_or
    - span_not
    - span_term
    - span_first
    - span_multi
    - span_containing
    - span_within
    - span_field_masking
    - span_multi_term   
"""
