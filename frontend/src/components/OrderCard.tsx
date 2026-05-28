import React from 'react'

interface Props {
  orderId: string
  status: string
  total?: string
  items?: number
  delivery?: string
}

const statusColors: Record<string, string> = {
  '待付款': 'text-yellow-500',
  '已付款': 'text-blue-500',
  '已发货': 'text-green-500',
  '运输中': 'text-blue-500',
  '已签收': 'text-green-600',
  '已完成': 'text-gray-500',
  '已取消': 'text-red-400',
  '退款中': 'text-orange-500',
}

export default function OrderCard({ orderId, status, total, items, delivery }: Props) {
  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs text-gray-400">订单号: {orderId}</p>
          <p className={`text-sm font-medium mt-1 ${statusColors[status] || 'text-gray-600'}`}>
            {status}
          </p>
        </div>
        {total && <span className="text-sm font-semibold text-gray-800">{total}</span>}
      </div>
      {items && <p className="text-xs text-gray-500 mt-2">{items} 件商品</p>}
      {delivery && <p className="text-xs text-gray-500 mt-1">物流: {delivery}</p>}
    </div>
  )
}
