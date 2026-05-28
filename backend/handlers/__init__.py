from engine.multi_intent import MultiIntentHandler
from models.schemas import IntentType

from .product import (
    handle_comparison,
    handle_price_inquiry,
    handle_product_inquiry,
    handle_promotion_inquiry,
    handle_recommendation,
    handle_shipping_inquiry,
    handle_stock_inquiry,
)
from .order import (
    handle_delivery_inquiry,
    handle_order_cancel,
    handle_order_confirm,
    handle_order_modify,
    handle_order_status,
)
from .after_sale import (
    handle_after_sale_policy,
    handle_complaint,
    handle_exchange_request,
    handle_refund_inquiry,
    handle_return_request,
    handle_warranty_inquiry,
)
from .account import (
    handle_account_issue,
    handle_invoice_request,
    handle_payment_issue,
    handle_point_inquiry,
)
from .general import (
    handle_chat,
    handle_faq,
    handle_farewell,
    handle_feedback,
    handle_greeting,
)


def register_all_handlers(multi_handler: MultiIntentHandler):
    mappings = [
        (IntentType.product_inquiry, handle_product_inquiry),
        (IntentType.price_inquiry, handle_price_inquiry),
        (IntentType.stock_inquiry, handle_stock_inquiry),
        (IntentType.recommendation, handle_recommendation),
        (IntentType.comparison, handle_comparison),
        (IntentType.promotion_inquiry, handle_promotion_inquiry),
        (IntentType.shipping_inquiry, handle_shipping_inquiry),
        (IntentType.order_status, handle_order_status),
        (IntentType.order_cancel, handle_order_cancel),
        (IntentType.order_modify, handle_order_modify),
        (IntentType.order_confirm, handle_order_confirm),
        (IntentType.delivery_inquiry, handle_delivery_inquiry),
        (IntentType.return_request, handle_return_request),
        (IntentType.exchange_request, handle_exchange_request),
        (IntentType.refund_inquiry, handle_refund_inquiry),
        (IntentType.after_sale_policy, handle_after_sale_policy),
        (IntentType.complaint, handle_complaint),
        (IntentType.warranty_inquiry, handle_warranty_inquiry),
        (IntentType.account_issue, handle_account_issue),
        (IntentType.payment_issue, handle_payment_issue),
        (IntentType.invoice_request, handle_invoice_request),
        (IntentType.point_inquiry, handle_point_inquiry),
        (IntentType.faq, handle_faq),
        (IntentType.chat, handle_chat),
        (IntentType.greeting, handle_greeting),
        (IntentType.farewell, handle_farewell),
        (IntentType.feedback, handle_feedback),
    ]
    for intent_type, handler in mappings:
        multi_handler.register(intent_type, handler)
