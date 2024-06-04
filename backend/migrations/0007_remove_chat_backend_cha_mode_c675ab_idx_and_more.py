# Generated by Django 5.0.6 on 2024-06-04 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_remove_prompt_backend_pro_materia_05ff7a_idx_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='chat',
            name='backend_cha_mode_c675ab_idx',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='material',
            new_name='user_material',
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='role',
            field=models.CharField(choices=[('ai', 'Tutor'), ('user', 'User'), ('system', 'system')], help_text='Role', max_length=10, verbose_name='The role that the chat belongs to.'),
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['mode', 'topic', 'user_material'], name='backend_cha_mode_824ad6_idx'),
        ),
    ]
