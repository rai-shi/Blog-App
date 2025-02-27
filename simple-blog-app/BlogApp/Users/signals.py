from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, Profile
from Search.indexes import UserIndex


@receiver(post_save, sender=Profile)
def update_user_index_on_profile_save(sender, instance, **kwargs):
    user = instance.user  
    print(f"Profile updated for {user.username}")

    user_doc = UserIndex(
        meta={"id": user.id},
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f"{user.first_name} {user.last_name}",
        username=user.username,
        profile={
            "bio": instance.bio,
            "categories": [{
                "id": category.id, 
                "name": category.name} for category in instance.categories.all()]
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
