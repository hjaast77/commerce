# Generated by Django 4.1.7 on 2023-05-01 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_remove_listing_current_bid_remove_watchlist_listing_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watchlist',
            old_name='listings',
            new_name='listing',
        ),
    ]
