from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, Profile
from Search.indexes import UserIndex


# @receiver(post_save, sender=Profile)
# def update_user_index_on_profile_save(sender, instance, **kwargs):
#     user = instance.user  
#     print(f"Profile updated for {user.username}")
#     print(instance.user.profile.categories) # Blogs.Category.None
#     user_doc = UserIndex(
#         meta={"id": user.id},
#         first_name=user.first_name,
#         last_name=user.last_name,
#         full_name=f"{user.first_name} {user.last_name}",
#         username=user.username,
#         profile={
#             "bio": instance.bio,
#             "categories": [{
#                 "id": category.id, 
#                 "name": category.name} for category in instance.categories.all()]
#         }
#     )
#     user_doc.save()
#     print(f"Elasticsearch index updated for {user.username}")


from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Profile
from Search.indexes import UserIndex

@receiver(post_save, sender=Profile)
def update_user_index_on_profile_save(sender, instance, **kwargs):
    print(f"Profile updated for {instance.user.username}")
    update_elasticsearch(instance)

@receiver(m2m_changed, sender=Profile.categories.through)
def update_user_index_on_category_change(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        print(f"Categories updated for {instance.user.username}")
        update_elasticsearch(instance)

def update_elasticsearch(instance):
    user = instance.user

    categories = list(instance.categories.all())

    print(f"Updating Elasticsearch for {user.username}")
    print(f"Categories: {categories}") 

    user_doc = UserIndex(
        meta={"id": user.id},
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f"{user.first_name} {user.last_name}",
        username=user.username,
        profile={
            "bio": instance.bio,
            "categories": [{"id": cat.id, "name": cat.name} for cat in categories]
        }
    )
    user_doc.save()
    print(f"Elasticsearch index updated for {user.username}")


@receiver(post_delete, sender=User)
def delete_user_index(sender, instance, **kwargs):
    try:
        UserIndex.get(id=instance.id).delete()
    except:
        raise Exception("User not found in index")
