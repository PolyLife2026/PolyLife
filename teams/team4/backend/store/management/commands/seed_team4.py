from decimal import Decimal

from django.core.management.base import BaseCommand

from cart.models import DiscountCode
from store.models import Category, Product
from supplements.models import Supplement


class Command(BaseCommand):
    help = "Create Team 4 demonstration data."

    def handle(self, *args, **options):
        supplements_category, _ = Category.objects.update_or_create(
            slug="supplements",
            defaults={
                "name": "Supplements",
                "description": "Sports supplements",
                "is_deleted": False,
            },
        )

        equipment_category, _ = Category.objects.update_or_create(
            slug="equipment",
            defaults={
                "name": "Equipment",
                "description": "Sports equipment",
                "is_deleted": False,
            },
        )

        protein_category, _ = Category.objects.update_or_create(
            slug="protein-supplements",
            defaults={
                "name": "Protein Supplements",
                "parent": supplements_category,
                "description": "Protein-based supplements",
                "is_deleted": False,
            },
        )

        creatine, _ = Supplement.objects.update_or_create(
            name="Creatine Monohydrate",
            defaults={
                "scientific_name": "Creatine Monohydrate",
                "description": (
                    "A commonly used supplement for strength "
                    "and high-intensity exercise."
                ),
                "dosage": "3 to 5 grams daily.",
                "usage_instructions": (
                    "Take daily with water, before or after exercise."
                ),
                "benefits": (
                    "May improve strength and high-intensity "
                    "exercise performance."
                ),
                "side_effects": (
                    "May cause temporary water retention or "
                    "digestive discomfort."
                ),
                "warnings": (
                    "Users with medical conditions should consult "
                    "a qualified healthcare professional."
                ),
                "fda_reference": (
                    "Demonstration content only; not medical advice."
                ),
                "is_deleted": False,
            },
        )

        whey, _ = Supplement.objects.update_or_create(
            name="Whey Protein",
            defaults={
                "scientific_name": "Whey Protein Concentrate",
                "description": (
                    "A milk-derived protein supplement."
                ),
                "dosage": "20 to 30 grams per serving.",
                "usage_instructions": (
                    "Mix with water or milk after exercise."
                ),
                "benefits": (
                    "Supports daily protein intake and muscle recovery."
                ),
                "side_effects": (
                    "May cause digestive discomfort in lactose-sensitive "
                    "users."
                ),
                "warnings": (
                    "Not suitable for users with a milk-protein allergy."
                ),
                "fda_reference": (
                    "Demonstration content only; not medical advice."
                ),
                "is_deleted": False,
            },
        )

        Product.objects.update_or_create(
            slug="whey-protein-1kg",
            defaults={
                "name": "Whey Protein 1 kg",
                "description": "One-kilogram whey protein package.",
                "price": Decimal("1850000.00"),
                "stock_quantity": 25,
                "category": protein_category,
                "brand": "PolyLife",
                "sport_type": "bodybuilding",
                "rating": Decimal("4.50"),
                "supplement_id": whey.id,
                "is_active": True,
                "is_deleted": False,
            },
        )

        Product.objects.update_or_create(
            slug="creatine-300g",
            defaults={
                "name": "Creatine 300 g",
                "description": "Creatine monohydrate package.",
                "price": Decimal("950000.00"),
                "stock_quantity": 30,
                "category": supplements_category,
                "brand": "PolyLife",
                "sport_type": "strength-training",
                "rating": Decimal("4.70"),
                "supplement_id": creatine.id,
                "is_active": True,
                "is_deleted": False,
            },
        )

        Product.objects.update_or_create(
            slug="exercise-mat",
            defaults={
                "name": "Exercise Mat",
                "description": "Non-slip mat for home exercise.",
                "price": Decimal("650000.00"),
                "stock_quantity": 20,
                "category": equipment_category,
                "brand": "PolyLife",
                "sport_type": "fitness",
                "rating": Decimal("4.20"),
                "supplement_id": None,
                "is_active": True,
                "is_deleted": False,
            },
        )

        DiscountCode.objects.update_or_create(
            code="SALAM10",
            defaults={
                "discount_percent": Decimal("10.00"),
                "max_uses": 100,
                "is_active": True,
                "is_deleted": False,
            },
        )

        self.stdout.write(
            self.style.SUCCESS("Team 4 demo data created successfully.")
        )