# Generated by Django 5.0.6 on 2024-06-04 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_remove_chat_backend_cha_mode_c675ab_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='user_material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.usermaterial'),
        ),
    ]