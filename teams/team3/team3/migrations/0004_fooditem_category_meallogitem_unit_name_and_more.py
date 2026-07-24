
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team3', '0003_alter_dailystreak_table_alter_errorreport_table_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='category',
            field=models.CharField(choices=[('iranian', 'غذای ایرانی'), ('western', 'غذای فرنگی'), ('fruit', 'میوه'), ('dairy', 'لبنیات'), ('drink', 'نوشیدنی'), ('snack', 'تنقلات'), ('other', 'سایر')], db_index=True, default='other', max_length=20),
        ),
        migrations.AddField(
            model_name='meallogitem',
            name='unit_name',
            field=models.CharField(default='گرم', max_length=50),
        ),
        migrations.AddField(
            model_name='meallogitem',
            name='unit_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.CreateModel(
            name='FoodUnit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('unit_name', models.CharField(max_length=50)),
                ('grams_per_unit', models.DecimalField(decimal_places=2, max_digits=8)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='units', to='team3.fooditem')),
            ],
            options={
                'db_table': 'food_units',
                'unique_together': {('food_item', 'unit_name')},
            },
        ),
    ]
