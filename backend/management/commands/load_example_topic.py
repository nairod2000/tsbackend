import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from backend.models import Topic, Material, UserMaterial

class Command(BaseCommand):
    help = 'Load example topic and materials from a CSV file'

    def handle(self, *args, **kwargs):
        self.load_example_topic()

    def load_example_topic(self):
        # Define the username, email, and password for the user
        username = 'example_user@example.com'
        email = 'example_user@example.com'
        password = 'examplepassword'

        # Create or get the user
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))

        # Construct the absolute path to the CSV file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, '..', 'commands', 'data', 'material.csv')
        csv_path = os.path.normpath(csv_path)

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                topic_name = row['topic']
                content = row['content']

                # Get or create the topic
                topic, created = Topic.objects.get_or_create(name=topic_name, defaults={'created_by': user})
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created topic: {topic_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Topic {topic_name} already exists'))

                # Create the material
                material = Material.objects.create(topic=topic, content=content)
                self.stdout.write(self.style.SUCCESS(f'Added material to topic {topic_name}'))

                # Create the UserMaterial
                UserMaterial.objects.create(
                    material=material,
                    user=user,
                    ccount=0,
                    icount=0,
                    last_reviewed=None,
                    interval=1,
                    repetition=0,
                    easiness=2.5,
                    next_review=timezone.now(),
                    learned=False
                )
                self.stdout.write(self.style.SUCCESS(f'Associated material with user {username}'))

        self.stdout.write(self.style.SUCCESS('Finished loading example topic and materials'))
