import { useState } from 'react';
import { Search, Database, X, Menu } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`bg-white border-r border-gray-200 transition-all duration-300 ${
        isSidebarOpen ? 'w-64' : 'w-16'
      }`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {isSidebarOpen && <h2 className="text-lg font-semibold text-gray-800">Material Memory</h2>}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Search */}
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search materials..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Material List */}
        <div className="px-2 py-4 space-y-1">
          {[
            { name: 'Aluminum Oxide', date: '2025-10-24' },
            { name: 'Titanium Alloy Ti-6Al-4V', date: '2025-10-23' },
            { name: 'Carbon Fiber Composite', date: '2025-10-23' },
            { name: 'Stainless Steel 316L', date: '2025-10-22' },
            { name: 'Polylactic Acid (PLA)', date: '2025-10-21' },
            { name: 'Silicon Carbide', date: '2025-10-20' },
          ].map((material, index) => (
            <div 
              key={index}
              className="flex items-center gap-3 px-3 py-2 hover:bg-green-50 rounded-lg cursor-pointer transition-colors"
            >
              <Database className="text-green-600 flex-shrink-0" size={18} />
              {isSidebarOpen && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{material.name}</p>
                  <p className="text-xs text-gray-500">{material.date}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
