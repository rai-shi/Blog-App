from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from django_elasticsearch_dsl.registries import registry

from .models import * 
from Users.models import User
from Search.indexes import UserIndex, BlogIndex

import datetime

# blog creation signals
@receiver(post_save, sender=Blog)
def create_blog_index(sender, instance, created, **kwargs):
    print(f"Blog {instance.title} created: {created}")
    if created:
        elasticsearch_blog(instance)
        print(f"Blog index created for {instance.title}")

@receiver(m2m_changed, sender=Blog.categories.through)
def update_blog_index_on_category_change(sender, instance, action, **kwargs):
    if action in ["post_add"]: 
        print(f"Categories updated for {instance.title}")
        elasticsearch_blog(instance)

def elasticsearch_blog(instance):
    categories = list(instance.categories.all())
    like_count = instance.likes.count()
    comment_count = instance.comments.count()
    # comments = list(instance.comments.all())
    # print(f"Comments: {comments}")
    blog_doc = BlogIndex(
        meta={"id": instance.id},
        title=instance.title,
        description=instance.description,
        content=instance.content,
        created_at=instance.created_at,
        author_username=instance.author.username,
        author_id=instance.author.id,

        categories=[{"id": cat.id, "name": cat.name} for cat in categories],
        
        like_count=like_count,
        comment_count=comment_count,
        # comments=[{"content": comment.content, "user": {"id": comment.user.id, "username": comment.user.username}} for comment in comments]
        )

    blog_doc.save()


# blog deletion signals
@receiver(post_delete, sender=Blog)
def delete_blog_index(sender, instance, **kwargs):
    try:
        BlogIndex.get(id=instance.id).delete()
    except:
        raise Exception("Blog not found in index")

# blog like signals
@receiver([post_save, post_delete], sender=Like)
def update_like_count(sender, instance, **kwargs):
    blog = instance.post
    like_count = blog.likes.count()

    try:
        blog_doc = BlogIndex.get(id=blog.id)
        blog_doc.update(like_count=like_count)
        print(f"Updated like_count for {blog.title} ({like_count} likes)")
    except BlogIndex.DoesNotExist:
        print(f"Blog {blog.title} not found in Elasticsearch!")

# blog comment signals
# blog update signals
