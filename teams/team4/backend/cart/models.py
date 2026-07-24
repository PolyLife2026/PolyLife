from django.db import models


class DiscountCode(models.Model):
    """
    کد تخفیف (FR9)
    مثال: SALAM10 = ۱۰٪ تخفیف
    """
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "discount_codes"

    def is_valid(self):
        from django.utils import timezone
        if not self.is_active or self.is_deleted:
            return False
        if self.used_count >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"


class Order(models.Model):
    """
    سفارش (FR10, FR11, FR12)
    یک سفارش شامل چند کالا است.
    """
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "در انتظار پرداخت"),
        (STATUS_PAID, "پرداخت شده"),
        (STATUS_FAILED, "ناموفق"),
        (STATUS_CANCELLED, "لغو شده"),
    ]

    # user_id از هدر X-User-Id می‌آید - ما آن را در DB ذخیره می‌کنیم
    user_id = models.IntegerField(db_index=True)
    discount_code = models.ForeignKey(
        DiscountCode, on_delete=models.SET_NULL, null=True, blank=True
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "orders"
        indexes = [models.Index(fields=["user_id", "status"])]

    def __str__(self):
        return f"Order #{self.id} - User {self.user_id} - {self.status}"


class OrderItem(models.Model):
    """کالاهای هر سفارش"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("store.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # قیمت لحظه خرید
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "order_items"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class Transaction(models.Model):
    """
    تراکنش مالی (FR10)
    هر بار که کاربر پرداخت می‌کند، یک رکورد اینجا ثبت می‌شود.
    اطلاعات کارت بانکی اینجا ذخیره نمی‌شود (NFR3).
    """
    STATUS_CHOICES = [
        ("pending", "در انتظار"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    transaction_ref = models.CharField(max_length=255, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    gateway_response = models.TextField(blank=True)  # پاسخ درگاه بانکی (JSON)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "transactions"


class Invoice(models.Model):
    """
    فاکتور دیجیتال (FR11)
    پس از پرداخت موفق صادر می‌شود.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "invoices"

    def __str__(self):
        return self.invoice_number
