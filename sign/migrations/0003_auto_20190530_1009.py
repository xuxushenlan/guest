# Generated by Django 2.2.1 on 2019-05-30 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0002_auto_20190529_1654'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guest',
            old_name='event_id',
            new_name='event',
        ),
        migrations.AlterUniqueTogether(
            name='guest',
            unique_together={('event', 'phone')},
        ),
    ]
