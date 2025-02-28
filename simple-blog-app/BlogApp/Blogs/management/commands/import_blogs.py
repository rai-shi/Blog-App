from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Blogs.models import Blog
from Blogs.serializers import BlogDetailSerializer
import os
from django.conf import settings  
from pathlib import Path  
import pandas as pd



class Command(BaseCommand):
    help = 'Import specialities from a .csv file into the database'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'Blogs' / 'management' / 'commands' / 'cleaned_articles.csv'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        df = pd.read_csv(file_path)
        for index, row in df.iterrows():
            row_dict = row.to_dict()

            row_dict["author"] = row_dict["author"].lower()
            row_dict["author"] = row_dict["author"].replace(" ", "_")
            row_dict["content"] = row_dict["text"]
            row_dict.pop("text")
            row_dict.pop("cluster")
            categories_data = row_dict["categories"]
            categories_data = categories_data.replace("[", "")
            categories_data = categories_data.replace("]", "")
            categories_data = categories_data.replace('"', "")
            categories_data = categories_data.split(",")
            categories = [(int(i)+1) for i in categories_data]
            row_dict["categories"] = categories

            # title
            # description
            # content
            # categories  
            # author
            # print(len(row_dict["title"]))
            if User.objects.filter(username=row_dict["author"]).exists():
                author_username = User.objects.filter(username=row_dict["author"]).first()
                row_dict["author"] = author_username.id

                blog_serializer = BlogDetailSerializer(data=row_dict)
                if blog_serializer.is_valid():
                    blog_serializer.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully added blog'))
                else:
                    self.stdout.write(self.style.ERROR(f'Error adding profile: {blog_serializer.errors}'))
            else:
                self.stdout.write(self.style.ERROR(f'Author not found: {row_dict["author"]}'))
                continue

        self.stdout.write(self.style.SUCCESS('Import completed successfuly'))

