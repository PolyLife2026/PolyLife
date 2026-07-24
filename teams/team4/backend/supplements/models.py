from django.db import models


class Supplement(models.Model):
    """
    اطلاعات علمی هر مکمل ورزشی (FR6, FR7)
    این جدول اطلاعات علمی را نگه می‌دارد - جدا از محصول فروشگاه
    """
    name = models.CharField(max_length=300)
    scientific_name = models.CharField(max_length=300, blank=True)
    description = models.TextField(help_text="توضیح کلی مکمل")
    dosage = models.TextField(help_text="دوز توصیه‌شده - مثلاً: ۲۵ گرم در روز")
    usage_instructions = models.TextField(
        help_text="نحوه و زمان مصرف - مثلاً: ۳۰ دقیقه قبل از تمرین"
    )
    benefits = models.TextField(help_text="مزایا و فواید")
    side_effects = models.TextField(help_text="عوارض جانبی احتمالی")
    warnings = models.TextField(help_text="هشدارها - مثلاً: برای افراد زیر ۱۸ سال مناسب نیست")
    # طبق FR9 NFR: اطلاعات مکمل باید بر اساس استانداردهای سازمان غذا و دارو باشد
    fda_reference = models.CharField(max_length=500, blank=True, help_text="مرجع FDA/سازمان غذا و دارو")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "supplements"
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name
