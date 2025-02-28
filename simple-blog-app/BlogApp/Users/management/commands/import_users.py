from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Users.models import Profile
from Users.serializers import UserSerializer, ProfileSerializer
import os
from django.conf import settings  
from pathlib import Path  


class Command(BaseCommand):
    help = 'Import specialities from a .txt file into the database'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'Users' / 'management' / 'commands' / 'authors.csv'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripted_line = line.strip()
                datas = stripted_line.split(",")

                data = datas[7].replace("[", "")
                data = data.replace("]", "")
                data = data.replace('"', "")
                data = data.split(",")
                categories = [(int(i)+1) for i in data]

                user_dict = {
                    "username": datas[1],
                    "first_name": datas[2],
                    "last_name": datas[3],
                    "email": datas[4],
                    "password": datas[5]
                }
                bio_dict = {
                    "bio": datas[6],
                    "categories": categories
                }
                
                if not User.objects.filter(username=datas[2]).exists():
                    user_serializer = UserSerializer(data=user_dict)
                    if user_serializer.is_valid():
                        user = user_serializer.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully added user: {user.username}'))

                        bio_dict["user"] = user.id
                        profile_serializer = ProfileSerializer(data=bio_dict)
                        if profile_serializer.is_valid():
                            profile_serializer.save()
                            self.stdout.write(self.style.SUCCESS(f'Successfully added profile: {user.username}'))
                        else:
                            self.stdout.write(self.style.ERROR(f'Error adding profile: {profile_serializer.errors}'))

                    else:
                        self.stdout.write(self.style.ERROR(f'Error adding user: {user_serializer.errors}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'User already exists: {datas[2]}'))


        self.stdout.write(self.style.SUCCESS('Import completed'))
