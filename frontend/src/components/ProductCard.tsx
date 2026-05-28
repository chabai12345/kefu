import React from 'react'

interface Props {
  name: string
  price?: string
  stock?: string
  image?: string
  description?: string
}

export default function ProductCard({ name, price, stock, image, description }: Props) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      {image && <img src={image} alt={name} className="w-full h-40 object-cover" />}
      <div className="p-3">
        <h4 className="font-medium text-gray-800 text-sm">{name}</h4>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
        <div className="flex justify-between items-center mt-2">
          {price && <span className="text-red-500 font-semibold text-sm">{price}</span>}
          {stock && <span className={`text-xs ${stock === '有货' ? 'text-green-500' : 'text-red-400'}`}>{stock}</span>}
        </div>
      </div>
    </div>
  )
}
