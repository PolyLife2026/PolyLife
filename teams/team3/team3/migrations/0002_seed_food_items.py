from django.db import migrations

def seed_data(apps, schema_editor):
    FoodItem = apps.get_model('team3', 'FoodItem')
    foods = [
        ("Chicken Breast", 165, 31.0, 0.0, 3.6), ("Cooked White Rice", 130, 2.7, 28.0, 0.3),
        ("Boiled Egg", 155, 13.0, 1.1, 11.0), ("Almonds", 579, 21.0, 22.0, 50.0),
        ("Banana", 89, 1.1, 23.0, 0.3), ("Apple", 52, 0.3, 14.0, 0.2),
        ("Salmon Fish", 206, 22.0, 0.0, 13.0), ("Oats", 389, 17.0, 66.0, 7.0),
        ("Milk (Whole)", 61, 3.2, 4.8, 3.3), ("Greek Yogurt", 59, 10.0, 3.6, 0.4),
        ("Peanut Butter", 588, 25.0, 20.0, 50.0), ("Broccoli", 34, 2.8, 6.6, 0.4),
        ("Potato", 77, 2.0, 17.0, 0.1), ("Sweet Potato", 86, 1.6, 20.0, 0.1),
        ("Avocado", 160, 2.0, 8.5, 15.0), ("Beef Steak", 271, 25.0, 0.0, 19.0),
        ("Tofu", 144, 16.0, 2.8, 8.8), ("Lentils", 116, 9.0, 20.0, 0.4),
        ("Chickpeas", 164, 8.9, 27.0, 2.6), ("Walnuts", 654, 15.0, 14.0, 65.0),
        ("Cheddar Cheese", 402, 25.0, 1.3, 33.0), ("Spaghetti", 158, 5.8, 31.0, 0.9),
        ("Tomato", 18, 0.9, 3.9, 0.2), ("Carrot", 41, 0.9, 10.0, 0.2),
        ("Cucumber", 15, 0.7, 3.6, 0.1), ("Orange", 47, 0.9, 12.0, 0.1),
        ("Olive Oil", 884, 0.0, 0.0, 100.0), ("Whole Wheat Bread", 247, 13.0, 41.0, 3.4),
        ("Quinoa", 120, 4.4, 21.0, 1.9), ("Tuna (Canned)", 132, 28.0, 0.0, 1.3)
    ]
    for name, cal, pro, carb, fat in foods:
        FoodItem.objects.create(name=name, calories=cal, protein=pro, carbs=carb, fat=fat)

class Migration(migrations.Migration):

    dependencies = [
        ('team3', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data),
    ]