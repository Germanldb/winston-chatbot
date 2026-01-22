from woocommerce import API
from ..core.config import settings

class WooCommerceService:
    def __init__(self):
        self.wcapi = API(
            url=settings.WOOCOMMERCE_URL,
            consumer_key=settings.WOOCOMMERCE_CONSUMER_KEY,
            consumer_secret=settings.WOOCOMMERCE_CONSUMER_SECRET,
            version="wc/v3"
        )

    def get_product_by_name(self, name: str):
        response = self.wcapi.get("products", params={"search": name}).json()
        return response

    def get_all_products(self):
        # This could be expensive, better to use search or categories
        response = self.wcapi.get("products", params={"per_page": 100}).json()
        return response

    def get_product_variations(self, product_id: int):
        response = self.wcapi.get(f"products/{product_id}/variations").json()
        return response

woocommerce_service = WooCommerceService()
