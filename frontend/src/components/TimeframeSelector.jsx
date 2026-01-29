import React from 'react';

const TIMEFRAMES = [
    { id: '1d', label: 'Today' },
    { id: '7d', label: '7 Days' },
    { id: '30d', label: '30 Days' },
    { id: '1y', label: 'Year' },
];

export default function TimeframeSelector({ activeTab, onTabChange }) {
    return (
        <div className="flex gap-2 mb-8 border-b border-gray-200 pb-4 overflow-x-auto">
            {TIMEFRAMES.map((tf) => (
                <button
                    key={tf.id}
                    onClick={() => onTabChange(tf.id)}
                    className={`
            px-4 py-2 text-sm font-medium transition-colors duration-200 
            ${activeTab === tf.id
                            ? 'text-text-main border-b-2 border-text-main'
                            : 'text-gray-400 hover:text-gray-600'}
          `}
                >
                    {tf.label}
                </button>
            ))}
        </div>
    );
}
