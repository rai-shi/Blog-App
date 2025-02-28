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
from elasticsearch_dsl import Q

# es = Elasticsearch(['http://localhost:9200'])


class SearchUserView(APIView):
    def get(self, request):

        if not bool(request.query_params):
            return Response(
                {"error": "Query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        search = UserIndex.search()
        if request.query_params.get('user'):
            # multi_match search
            query = request.query_params.get('user')
            search_query = search.query("multi_match", 
                                        query=query, 
                                        fields=["full_name", "username"])
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
        elif request.query_params.get('username'):
            # term search
            query = request.query_params.get('username')
            search_query = search.query("term", 
                                        username=query)
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )
        elif request.query_params.get('category'):
            # inner object search  
            query = request.query_params.get('category')
            search_query = search.query("match", 
                                        profile__categories__name=query)
            response = search_query.execute()
            return Response(
                response.to_dict(),
                status=status.HTTP_200_OK
            )

        elif request.query_params.get('user-blogs'):
            # get all blogs of a user
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
    


class SearchBlogView(APIView):
    def get(self, request):
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
        
        elif request.query_params.get("category"):
            query = request.query_params.get("category")  

            search_query =  BlogIndex.search().query(
                                                "nested", 
                                                path="categories", 
                                                query=Q("term", categories__name=query.capitalize())) # term, match, wildcard, case sensitive slug kullanılacak
                                                # query=Q("match_all"))
            results = search_query.execute()

            return Response(
                # {"results": [hit.to_dict() for hit in results]},
                {"results": results.to_dict()},
                status=status.HTTP_200_OK)
        
        # belli bir kullanıcının bloglarında category'lerine göre arama yapma

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
    

class SearchCategoryView(APIView):
    def get(self, request):
        q = request.GET.get("tag")
        if not q:
            return Response(
                {"error": "Query parameter 'tag' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        search = BlogIndex.search().query(
            "nested", 
            path="categories", 
            query=Q("match", categories__name=q)
            # **{'address.city': 'prague'}
        ).sort(
            {"like_count": {"order": "desc"}},
            {"comment_count": {"order": "desc"}}
        )
        results = search.execute()

        return Response(
            # {"results": [hit.to_dict() for hit in results]},
            {"results": results.to_dict()},
            status=status.HTTP_200_OK
        )
    


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
