# Generated by Django 4.1.7 on 2023-05-01 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_watchlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(related_name='watchlists', to='auctions.listing'),
        ),
    ]