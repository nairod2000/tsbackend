import os
from django.core.management.base import BaseCommand
from backend.models import Prompt

class Command(BaseCommand):
    help = 'load the prompts'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(base_dir, '..', 'commands', 'data', 'prompts')

        for file_name in os.listdir(prompt_dir):
            with open(os.path.join(prompt_dir, file_name)) as f:
                prompt = f.read()
                print(file_name.removesuffix('.txt'))
                Prompt.objects.update_or_create(
                    name = file_name.removesuffix('.txt'),
                    content = prompt
                )

