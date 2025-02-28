from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Blogs.models import Category, Blog
from Users.models import User
from Blogs.serializers import CommentSerializer
import os
from django.conf import settings  
from pathlib import Path  
import pandas as pd



class Command(BaseCommand):
    help = 'Import specialities from a .csv file into the database'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'Blogs' / 'management' / 'commands' / 'comments.csv'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        df = pd.read_csv(file_path)
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            print(row_dict)

            # post
            # user
            # comment

            if User.objects.filter(id=row_dict["user"]).exists() and Blog.objects.filter(id=row_dict["post"]).exists():

                row_dict["content"] = row_dict["comment"]
                row_dict.pop("comment")
                
                comment_serializer = CommentSerializer(data=row_dict)
                if comment_serializer.is_valid():
                    comment_serializer.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully added comment'))
                else:
                    self.stdout.write(self.style.ERROR(f'Error adding comment: {comment_serializer.errors}'))
            else:
                self.stdout.write(self.style.ERROR(f'Author or Blog found: {row_dict["author"]}, {row_dict["blog"]}'))
                continue

        self.stdout.write(self.style.SUCCESS('Import completed successfuly'))

