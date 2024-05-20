# Generated by Django 5.0.6 on 2024-05-15 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FixedMaterial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, verbose_name="Name of the fixed material"
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=255, verbose_name="Type of the fixed material"
                    ),
                ),
                (
                    "description",
                    models.TextField(verbose_name="Description of the fixed material"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Fixed Material",
                "verbose_name_plural": "Fixed Materials",
                "indexes": [
                    models.Index(
                        fields=["name", "type"], name="backend_fix_name_93900a_idx"
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="FixedChatMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sequence",
                    models.PositiveIntegerField(verbose_name="Sequence of the chat"),
                ),
                ("content", models.TextField(verbose_name="Content of the chat")),
                (
                    "input_type",
                    models.CharField(
                        choices=[("button", "Button"), ("text", "Text")],
                        max_length=255,
                        verbose_name="Type of input expected",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.fixedmaterial",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fixed Chat Message",
                "verbose_name_plural": "Fixed Chat Messages",
            },
        ),
        migrations.CreateModel(
            name="Prompt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(verbose_name="Content of the prompt")),
                (
                    "editable",
                    models.BooleanField(
                        default=False, verbose_name="Is the prompt editable by the user"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.material",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prompt",
                "verbose_name_plural": "Prompts",
            },
        ),
        migrations.CreateModel(
            name="FixedInput",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "input_value",
                    models.CharField(max_length=255, verbose_name="Value of the input"),
                ),
                (
                    "input_type",
                    models.CharField(
                        choices=[("button", "Button"), ("text", "Text")],
                        max_length=255,
                        verbose_name="Type of input",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "chat_message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.fixedchatmessage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fixed Input",
                "verbose_name_plural": "Fixed Inputs",
                "indexes": [
                    models.Index(
                        fields=["chat_message", "input_type"],
                        name="backend_fix_chat_me_a5aaa9_idx",
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name="fixedchatmessage",
            index=models.Index(
                fields=["material", "sequence"], name="backend_fix_materia_8a5729_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="prompt",
            index=models.Index(
                fields=["material", "editable"], name="backend_pro_materia_05ff7a_idx"
            ),
        ),
    ]