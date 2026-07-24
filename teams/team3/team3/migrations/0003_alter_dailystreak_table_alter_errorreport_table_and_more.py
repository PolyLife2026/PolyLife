
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team3', '0002_seed_food_items'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='dailystreak',
            table='daily_streaks',
        ),
        migrations.AlterModelTable(
            name='errorreport',
            table='error_reports',
        ),
        migrations.AlterModelTable(
            name='favoritefood',
            table='favorite_foods',
        ),
        migrations.AlterModelTable(
            name='fooditem',
            table='food_items',
        ),
        migrations.AlterModelTable(
            name='healthprofile',
            table='health_profiles',
        ),
        migrations.AlterModelTable(
            name='meallog',
            table='meal_logs',
        ),
        migrations.AlterModelTable(
            name='meallogitem',
            table='meal_log_items',
        ),
        migrations.AlterModelTable(
            name='searchhistory',
            table='search_history',
        ),
    ]
