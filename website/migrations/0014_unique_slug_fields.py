# Generated manually for Task 5 — apply unique constraint to slug fields
# All existing rows were pre-populated with slugs before this migration runs.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "website",
            "0013_album_slug_sermon_slug_wartajemaat_slug",
        ),
    ]

    operations = [
        # Step 1: Add unique=True while keeping null=True (safe — no NULLs exist)
        migrations.AlterField(
            model_name="album",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="sermon",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="wartajemaat",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        # Step 2: Remove null=True — no default needed because no NULL rows exist
        migrations.AlterField(
            model_name="album",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
        migrations.AlterField(
            model_name="sermon",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
        migrations.AlterField(
            model_name="wartajemaat",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
    ]
