# Blog-App
PostgreSQL-Elasticsearch-Django-Bootstrap

* set up conda env 
* install requirements ```pip install -m requirements.txt```
* set up elasticsearch (this [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/deb.html) was used)
* set up postgresql, (used awesome-docker-compose) 
* run migrations
* start django server in manage.py path ```python manage.py runserver```

you can find some example data for testing API's in here.

---
User can 
* register, login, logout, view profile, delete account, 
* create blog, delete his/her blog, list all his/her blog, view one of his/her blog
* view all blogs
* like and unlike blogs, comment blogs
---

**Django Models**
```
User 
   ├── Profile (OneToOne)
   ├── Post (OneToMany)
   ├── Comment (OneToMany)
   ├── Like (OneToMany)

Post 
   ├── Comment (OneToMany)
   ├── Like (OneToMany)
   ├── Category (ManyToMany)

```

**Elasticsearch Indices**
```
user_index
   first_name
   last_name
   full_name
   username
   profile (Inner Object)
      bio
      categories (Denormalized)
         id 
         name

user-profile 1-1 -> inner object
profile-category N-N -> denormalized
```
```
blog_index 
   title
   description
   content
   created_at
   author_id
   author_username
   comment_count
   like_count
   comments (Nested)
      id
      user (Nested)
         id
         username
   categories (Nested)
      id
      name
   
blog-comment 1-N -> nested
user-comment 1-N -> nested 
blog-category N-N -> nested
```