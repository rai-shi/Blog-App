from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Blogs.models import Category
from Blogs.serializers import CategorySerializer
import os
from django.conf import settings  
from pathlib import Path  


class Command(BaseCommand):
    help = 'Import specialities from a .txt file into the database'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'Blogs' / 'management' / 'commands' / 'categories.txt'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripted_line = line.strip() 
                data = stripted_line
                data_dict = {
                    "name": data
                }

                if not Category.objects.filter(name=data).exists():
                    category_serializer = CategorySerializer(data=data_dict)
                    if category_serializer.is_valid():
                        category = category_serializer.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully added: {category.slug}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Error adding: {category_serializer.errors}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Category already exists: {data}'))


        self.stdout.write(self.style.SUCCESS('Import completed'))
