# Generated by Django 5.0.4 on 2024-05-15 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billetterie', '0002_alter_utilisateur_clef_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='clef_unique',
            field=models.CharField(default='nB2sUUFoR2jFSysK', max_length=16, unique=True),
        ),
    ]
