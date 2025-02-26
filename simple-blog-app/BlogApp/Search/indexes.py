from elasticsearch_dsl import Document, Text, Keyword, Date, Nested, InnerDoc
import elasticsearch_dsl as es

class ProfileInner(InnerDoc):
    bio = Text()
    categories = Keyword(multi=True) # denormalized categories [names]

class UserIndex(Document):
    first_name = Text()
    last_name = Text()
    full_name = Text()
    username = Keyword()
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
    content = Text()
    user = Nested(properties={
        "id": Keyword(),
        "username": Keyword()
    })

class BlogIndex(Document):
    title = Text()
    description = Text()
    content = Text()
    created_at = Date()
    author_id = Keyword()  # author id
    author_username = Keyword()  # author
    categories = Nested(properties={
        "id": Keyword(),
        "name": Text()
    })
    comment_count = Keyword()
    like_count = Keyword()
    comments = Nested(CommentInner)

    class Index:
        name = "blog_index"
