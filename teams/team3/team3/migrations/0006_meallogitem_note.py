from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team3', '0005_seed_persian_foods'),
    ]

    operations = [
        migrations.AddField(
            model_name='meallogitem',
            name='note',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
