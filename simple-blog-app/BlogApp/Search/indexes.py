from elasticsearch_dsl import Document, Text, Integer, Keyword, Date, Nested, InnerDoc
import elasticsearch_dsl as es

class ProfileInner(InnerDoc):
    bio = Text()
    categories = Keyword(multi=True) # denormalized categories [names]

class UserIndex(Document):
    first_name = Text(required=True)
    last_name = Text(required=True)
    full_name = Text(required=True)
    username = Keyword(required=True)
    profile = ProfileInner()

    class Index:
        name = "user_index"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    class Meta:
        doc_type = 'user'



class CommentInner(InnerDoc):
    id = Integer(required=True)
    content = Text()
    user = Nested(properties={
        "id": Integer(required=True),
        "username": Keyword(required=True)
    })

class BlogIndex(Document):
    title = Text(required=True)
    description = Text()
    content = Text(required=True)
    created_at = Date()
    author_id = Integer(required=True)  # author id
    author_username = Keyword(required=True)  # author
    categories = Nested(properties={
        "id": Integer(required=True),
        "name": Keyword(required=True)
    })
    comment_count = Integer()
    like_count = Integer()
    comments = Nested(CommentInner)

    class Index:
        name = "blog_index"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
            # "max_result_window": 10000
        }
