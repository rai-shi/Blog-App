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
    # comments = list(instance.comments.all())
    print(f"Categories: {categories}") 
    # print(f"Comments: {comments}")
    print(type(instance.created_at))
    blog_doc = BlogIndex(
        meta={"id": instance.id},
        title=instance.title,
        description=instance.description,
        content=instance.content,
        created_at=instance.created_at,
        author_username=instance.author.username,
        author_id=instance.author.id,

        categories=[{"id": cat.id, "name": cat.name} for cat in categories],
        
        like_count=0,
        comment_count=0
        )
    blog_doc.save()


# blog deletion signals
@receiver(post_delete, sender=Blog)
def delete_blog_index(sender, instance, **kwargs):
    try:
        BlogIndex.get(id=instance.id).delete()
    except:
        raise Exception("Blog not found in index")

# blog update signals
# blog comment signals
# blog like signals
