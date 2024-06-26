# Generated by Django 5.0.6 on 2024-05-15 17:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Topic', max_length=75, verbose_name='The name of the topic.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='Content', verbose_name='The content of the material')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.topic')),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materials',
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('eval', 'Evaluation'), ('teach', 'Teaching')], help_text='Chat mode', max_length=10, verbose_name='Chat mode (Eval or Teach).')),
                ('starred', models.BooleanField(default=False, help_text='Starred', verbose_name='Starred by user.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.topic')),
            ],
            options={
                'verbose_name': 'Chat',
                'verbose_name_plural': 'Chats',
            },
        ),
        migrations.CreateModel(
            name='UserMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ccount', models.PositiveSmallIntegerField(help_text='Correct count', verbose_name='Correct count: the number of times material recalled correctly.')),
                ('icount', models.PositiveSmallIntegerField(help_text='Incorrect count', verbose_name='Incorrect count: the number of times material recalled incorrectly.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.material')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Material',
                'verbose_name_plural': 'User Materials',
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ai', 'Tutor'), ('user', 'User')], help_text='Role', max_length=10, verbose_name='The role that the chat belongs to.')),
                ('content', models.TextField(help_text='Content', verbose_name='The content of the message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.chat')),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'indexes': [models.Index(fields=['chat', 'role'], name='backend_cha_chat_id_bf0b94_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='topic',
            index=models.Index(fields=['created_by'], name='backend_top_created_8efe5f_idx'),
        ),
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['topic'], name='backend_mat_topic_i_0f3f26_idx'),
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['mode', 'topic'], name='backend_cha_mode_987a2f_idx'),
        ),
        migrations.AddIndex(
            model_name='usermaterial',
            index=models.Index(fields=['user', 'material'], name='backend_use_user_id_c6a0b1_idx'),
        ),
    ]
