# Generated by Django 5.0.4 on 2024-05-18 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billetterie', '0011_alter_utilisateur_clef_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='clef_unique',
            field=models.CharField(default='RG4Zo2cCgAxpADhc', max_length=16, unique=True),
        ),
    ]
