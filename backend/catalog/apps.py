from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """商品主檔、採購批次、倉庫與庫存位置。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
    verbose_name = "商品主檔與採購批次"
