from django.db import models
from django.contrib.auth.models import User  # Import the User model
from django.utils import timezone

class Topic(models.Model):
    name = models.CharField(max_length=75, verbose_name='The name of the topic.', help_text='Topic')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtopics')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['parent']),
        ]
    
    def save(self, *args, **kwargs):
        if self.parent and self.parent.parent:
            raise ValueError("Subtopics can only be one level deep.")
        super().save(*args, **kwargs)


class Chat(models.Model):
    '''A dialogue between user and tutor.'''
    mode = models.CharField(max_length=10, choices=[('eval', 'Evaluation'), ('teach', 'Teaching')], verbose_name='Chat mode (Eval or Teach).', help_text='Chat mode')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE, null=True, blank=True)
    starred = models.BooleanField(default=False, verbose_name='Starred by user.', help_text='Starred')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mode} chat on {self.topic.name}"

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        indexes = [
            models.Index(fields=['mode', 'topic', 'material']),
        ]


class ChatMessage(models.Model):
    '''Message in a dialogue between user and tutor.'''
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('ai', 'Tutor'), ('user', 'User'), ('system', 'system')], verbose_name='The role that the chat belongs to.', help_text='Role')
    content = models.TextField(verbose_name='The content of the message', help_text='Content')
    sequence = models.PositiveIntegerField(verbose_name='Sequence of the message')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        indexes = [
            models.Index(fields=['chat', 'role']),
            models.Index(fields=['chat', 'sequence']),
        ]


class Material(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='The content of the material', help_text='Content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Material on {self.topic.name}"

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        indexes = [
            models.Index(fields=['topic']),
        ]


class UserMaterial(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ccount = models.PositiveSmallIntegerField(verbose_name='Correct count: the number of times material recalled correctly.', help_text='Correct count')
    icount = models.PositiveSmallIntegerField(verbose_name='Incorrect count: the number of times material recalled incorrectly.', help_text='Incorrect count')
    last_reviewed = models.DateTimeField(null=True, blank=True)
    interval = models.PositiveIntegerField(default=1)
    repetition = models.PositiveIntegerField(default=0)
    easiness = models.FloatField(default=2.5)
    next_review = models.DateTimeField(default=timezone.now)
    learned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserMaterial for {self.user.username} on {self.material.topic.name}"

    class Meta:
        verbose_name = 'User Material'
        verbose_name_plural = 'User Materials'
        indexes = [
            models.Index(fields=['user', 'material']),
        ]


# I dont think that this is something that I really want to have
class FixedMaterial(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name of the fixed material')
    type = models.CharField(max_length=255, verbose_name='Type of the fixed material')
    description = models.TextField(verbose_name='Description of the fixed material')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Fixed Material'
        verbose_name_plural = 'Fixed Materials'
        indexes = [
            models.Index(fields=['name', 'type']),
        ]


# 
class FixedChatMessage(models.Model):
    material = models.ForeignKey(FixedMaterial, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True)
    sequence = models.PositiveIntegerField(verbose_name='Sequence of the chat')
    content = models.TextField(verbose_name='Content of the chat')
    input_type = models.CharField(max_length=255, verbose_name='Type of input expected', choices=[('button', 'Button'), ('text', 'Text')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.name} - Step {self.sequence}"

    class Meta:
        verbose_name = 'Fixed Chat Message'
        verbose_name_plural = 'Fixed Chat Messages'
        indexes = [
            models.Index(fields=['material', 'sequence']),
        ]


class FixedInput(models.Model):
    chat_message = models.ForeignKey(FixedChatMessage, on_delete=models.CASCADE)
    input_value = models.CharField(max_length=255, verbose_name='Value of the input')
    input_type = models.CharField(max_length=255, verbose_name='Type of input', choices=[('button', 'Button'), ('text', 'Text')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chat_message.material.name} - Step {self.chat_message.sequence} - Input {self.input_value}"

    class Meta:
        verbose_name = 'Fixed Input'
        verbose_name_plural = 'Fixed Inputs'
        indexes = [
            models.Index(fields=['chat_message', 'input_type']),
        ]


class Prompt(models.Model):
    name = models.CharField(max_length=50, verbose_name='The name of the prompt.')
    content = models.TextField(verbose_name='Content of the prompt')
    editable = models.BooleanField(default=False, verbose_name='Is the prompt editable by the user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prompt: {self.name}"

    class Meta:
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'
        indexes = [
            models.Index(fields=['name', 'editable']),
        ]
