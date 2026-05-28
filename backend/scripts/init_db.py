"""Initialize database and seed sample orders."""

import logging
from datetime import datetime, timedelta

from models.database import Order, get_sync_session, init_sync_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_ORDERS = [
    Order(
        order_id="ORD20240101001",
        user_id="default",
        status="delivered",
        product_name="Apple iPhone 15 Pro 256GB",
        price=8999.00,
        quantity=1,
        total_amount=8999.00,
        created_at=datetime.now() - timedelta(days=30),
        updated_at=datetime.now() - timedelta(days=25),
        shipping_address="北京市朝阳区建国路88号",
        logistics_company="顺丰速运",
        tracking_number="SF1234567890",
    ),
    Order(
        order_id="ORD20240115002",
        user_id="default",
        status="shipped",
        product_name="Samsung 990 Pro 2TB SSD",
        price=1599.00,
        quantity=1,
        total_amount=1599.00,
        created_at=datetime.now() - timedelta(days=14),
        updated_at=datetime.now() - timedelta(days=12),
        shipping_address="上海市浦东新区张江高科技园区",
        logistics_company="京东物流",
        tracking_number="JD9876543210",
    ),
    Order(
        order_id="ORD20240201003",
        user_id="default",
        status="paid",
        product_name="Sony WH-1000XM5 降噪耳机",
        price=2499.00,
        quantity=1,
        total_amount=2499.00,
        created_at=datetime.now() - timedelta(days=7),
        updated_at=datetime.now() - timedelta(days=7),
        shipping_address="广东省深圳市南山区科技园",
    ),
    Order(
        order_id="ORD20240215004",
        user_id="default",
        status="pending",
        product_name="Dell XPS 16 笔记本电脑",
        price=15999.00,
        quantity=1,
        total_amount=15999.00,
        created_at=datetime.now() - timedelta(days=1),
        updated_at=datetime.now() - timedelta(days=1),
        shipping_address="浙江省杭州市西湖区文三路",
    ),
    Order(
        order_id="ORD20240301005",
        user_id="default",
        status="returning",
        product_name="Logitech MX Master 3S 鼠标",
        price=699.00,
        quantity=1,
        total_amount=699.00,
        created_at=datetime.now() - timedelta(days=20),
        updated_at=datetime.now() - timedelta(days=3),
        shipping_address="北京市海淀区中关村大街",
        return_reason="鼠标滚轮异响",
    ),
    Order(
        order_id="ORD20240315006",
        user_id="default",
        status="refunded",
        product_name="Anker 65W 充电器",
        price=299.00,
        quantity=2,
        total_amount=598.00,
        created_at=datetime.now() - timedelta(days=25),
        updated_at=datetime.now() - timedelta(days=10),
        shipping_address="广州市天河区体育西路",
        return_reason="充电器发热严重",
        refund_amount=598.00,
    ),
    Order(
        order_id="ORD20240401007",
        user_id="default",
        status="cancelled",
        product_name="机械革命 旷世16 游戏本",
        price=7499.00,
        quantity=1,
        total_amount=7499.00,
        created_at=datetime.now() - timedelta(days=10),
        updated_at=datetime.now() - timedelta(days=9),
        shipping_address="四川省成都市高新区天府大道",
    ),
    Order(
        order_id="ORD20240415008",
        user_id="default",
        status="shipped",
        product_name="Apple Watch Ultra 2",
        price=5999.00,
        quantity=1,
        total_amount=5999.00,
        created_at=datetime.now() - timedelta(days=5),
        updated_at=datetime.now() - timedelta(days=3),
        shipping_address="湖北省武汉市东湖高新区",
        logistics_company="中通快递",
        tracking_number="ZTO5556667777",
    ),
    Order(
        order_id="ORD20240501009",
        user_id="default",
        status="delivered",
        product_name="AirPods Pro 2 USB-C",
        price=1899.00,
        quantity=1,
        total_amount=1899.00,
        created_at=datetime.now() - timedelta(days=60),
        updated_at=datetime.now() - timedelta(days=55),
        shipping_address="江苏省南京市鼓楼区",
    ),
    Order(
        order_id="ORD20240520010",
        user_id="default",
        status="pending",
        product_name="罗技 G Pro X Superlight 鼠标",
        price=1099.00,
        quantity=1,
        total_amount=1099.00,
        created_at=datetime.now() - timedelta(hours=6),
        updated_at=datetime.now() - timedelta(hours=6),
        shipping_address="福建省厦门市思明区",
    ),
]


def main():
    logger.info("Initializing database schema...")
    engine = init_sync_engine()
    session = get_sync_session(engine)

    try:
        # Check if already seeded
        existing = session.query(Order).count()
        if existing > 0:
            logger.info("Database already has %d orders, skipping seed.", existing)
            return

        for order in SAMPLE_ORDERS:
            session.add(order)

        session.commit()
        logger.info("Seeded %d sample orders.", len(SAMPLE_ORDERS))

        # Print summary
        for o in SAMPLE_ORDERS:
            print(f"  {o.order_id} | {o.status:12s} | {o.product_name}")

    except Exception as e:
        logger.error("Seed failed: %s", e)
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
