import React from 'react'

interface Props {
  connected: boolean
  messageCount: number
  onSend: (text: string) => void
}

export default function SidePanel({ connected, messageCount, onSend }: Props) {
  return (
    <div className="w-72 bg-white border-l border-gray-200 p-4 hidden lg:block">
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">连接状态</h3>
        <div className="flex items-center gap-2 mt-2">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">{connected ? '已连接' : '未连接'}</span>
        </div>
      </div>
      <div>
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">对话信息</h3>
        <p className="text-sm text-gray-600 mt-2">消息数: {messageCount}</p>
      </div>
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">快捷操作</h3>
        <div className="mt-2 space-y-2">
          {[
            { label: '查订单', msg: '查我的订单' },
            { label: '商品咨询', msg: '有什么商品推荐？' },
            { label: '售后政策', msg: '售后政策是什么' },
            { label: '退换货', msg: '退换货流程是什么' },
          ].map(({ label, msg }) => (
            <button
              key={label}
              onClick={() => onSend(msg)}
              className="w-full text-left px-3 py-2 text-sm bg-gray-50 rounded-lg hover:bg-gray-100 text-gray-700 transition-colors"
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
