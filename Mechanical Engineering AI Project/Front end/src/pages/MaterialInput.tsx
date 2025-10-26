import { useState } from 'react';
import { Search, Database, Send, LayoutDashboard, Sparkles } from 'lucide-react';

export default function MaterialInput() {
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'input' | 'results'>('input');
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const materials = [
    { id: 1, name: 'Aluminum Oxide', date: '2025-10-24', properties: { density: '3.95 g/cm³', temp: '1650°C' } },
    { id: 2, name: 'Titanium Alloy Ti-6Al-4V', date: '2025-10-23', properties: { density: '4.43 g/cm³', temp: '1650°C' } },
    { id: 3, name: 'Carbon Fiber Composite', date: '2025-10-23', properties: { density: '1.55 g/cm³', temp: '300°C' } },
    { id: 4, name: 'Stainless Steel 316L', date: '2025-10-22', properties: { density: '8.00 g/cm³', temp: '1400°C' } },
    { id: 5, name: 'Polylactic Acid (PLA)', date: '2025-10-21', properties: { density: '1.24 g/cm³', temp: '150°C' } },
    { id: 6, name: 'Silicon Carbide', date: '2025-10-20', properties: { density: '3.21 g/cm³', temp: '2830°C' } },
  ];

  const getContextualResults = (query: string) => {
    const lowerQuery = query.toLowerCase();
    
    // Baseball bat context
    if (lowerQuery.includes('baseball') || lowerQuery.includes('bat') || lowerQuery.includes('sports')) {
      return {
        matchedMaterials: [
          {
            name: 'Carbon Fiber Composite',
            formula: 'CFRP',
            matchScore: 96,
            properties: { weight: '0.8 kg (Low)', strength: '1.2 GPa (High)', durability: 'Excellent', flexibility: 'High' },
            lattice: { type: 'Honeycomb', density: 'Optimized for impact resistance' },
            applications: ['Baseball bats', 'Sports equipment', 'High-performance tools']
          },
          {
            name: 'Aluminum Alloy 7075',
            formula: 'Al-Zn-Mg',
            matchScore: 91,
            properties: { weight: '1.2 kg (Low)', strength: '572 MPa (High)', durability: 'Excellent', flexibility: 'Moderate' },
            lattice: { type: 'Cross-hatched', density: 'Balanced weight-strength ratio' },
            applications: ['Aircraft components', 'Sports equipment', 'High-stress applications']
          },
          {
            name: 'Titanium Grade 5',
            formula: 'Ti-6Al-4V',
            matchScore: 85,
            properties: { weight: '1.5 kg (Moderate)', strength: '900 MPa (Very High)', durability: 'Exceptional', flexibility: 'Good' },
            lattice: { type: 'Wave pattern', density: 'Maximum strength at minimal weight' },
            applications: ['Aerospace', 'Medical implants', 'High-performance sports gear']
          }
        ]
      };
    }
    
    // Aerospace/high-temperature context
    if (lowerQuery.includes('aerospace') || lowerQuery.includes('airplane') || lowerQuery.includes('aircraft')) {
      return {
        matchedMaterials: [
          {
            name: 'Titanium Alloy Ti-6Al-4V',
            formula: 'Ti-6Al-4V',
            matchScore: 98,
            properties: { weight: '4.4 g/cm³ (Low)', strength: '900 MPa (Very High)', temp: '430°C (High)', corrosion: 'Excellent' },
            lattice: { type: 'BCC-HCP hybrid', density: 'Aerospace optimized' },
            applications: ['Aircraft frames', 'Engine components', 'Spacecraft structures']
          },
          {
            name: 'Carbon Fiber Reinforced Polymer',
            formula: 'CFRP',
            matchScore: 95,
            properties: { weight: '1.5 g/cm³ (Very Low)', strength: '1.2 GPa (High)', temp: '300°C (Moderate)', corrosion: 'Excellent' },
            lattice: { type: 'Woven fiber matrix', density: 'Weight-to-strength optimized' },
            applications: ['Wing structures', 'Fuselage panels', 'Interior components']
          },
          {
            name: 'Inconel 718',
            formula: 'Ni-Cr-Fe',
            matchScore: 92,
            properties: { weight: '8.2 g/cm³ (Moderate)', strength: '1379 MPa (Very High)', temp: '650°C (Very High)', corrosion: 'Exceptional' },
            lattice: { type: 'FCC structure', density: 'High-temperature optimized' },
            applications: ['Jet engines', 'Exhaust systems', 'Turbine blades']
          }
        ]
      };
    }
    
    // Vehicle/automotive context
    if (lowerQuery.includes('vehicle') || lowerQuery.includes('car') || lowerQuery.includes('frame') || lowerQuery.includes('automotive')) {
      return {
        matchedMaterials: [
          {
            name: 'High-Strength Steel',
            formula: 'Fe-Cr-Mn',
            matchScore: 97,
            properties: { weight: '7.8 g/cm³ (Moderate)', strength: '1200 MPa (Very High)', impact: 'High resistance', formability: 'Good' },
            lattice: { type: 'Martensitic structure', density: 'Crash safety optimized' },
            applications: ['Chassis frames', 'Safety cages', 'Body panels']
          },
          {
            name: 'Aluminum Alloy 6082',
            formula: 'Al-Si-Mg',
            matchScore: 94,
            properties: { weight: '2.7 g/cm³ (Low)', strength: '290 MPa (High)', impact: 'Good resistance', formability: 'Excellent' },
            lattice: { type: 'FCC structure', density: 'Weight reduction optimized' },
            applications: ['Body panels', 'Bumpers', 'Structural components']
          },
          {
            name: 'Magnesium Alloy AM60',
            formula: 'Mg-Al',
            matchScore: 89,
            properties: { weight: '1.8 g/cm³ (Very Low)', strength: '210 MPa (Moderate)', impact: 'Moderate', formability: 'Excellent' },
            lattice: { type: 'HCP structure', density: 'Ultra-lightweight optimized' },
            applications: ['Interior panels', 'Steering wheels', 'Seat frames']
          }
        ]
      };
    }
    
    // Default materials
    return {
      matchedMaterials: [
        {
          name: 'Carbon Nanotube Composite',
          formula: 'CNT-Polymer',
          matchScore: 88,
          properties: { weight: 'Very Low', strength: 'Exceptional', conductivity: 'High', durability: 'Excellent' },
          lattice: { type: 'Nanotube network', density: 'Cutting-edge optimized' },
          applications: ['Advanced composites', 'Electronics', 'Sensors']
        },
        {
          name: 'Silicon Carbide',
          formula: 'SiC',
          matchScore: 85,
          properties: { weight: '3.2 g/cm³ (Low)', strength: 'Very High', temp: '1650°C', hardness: 'Extremely High' },
          lattice: { type: 'Crystal structure', density: 'Ceramic optimized' },
          applications: ['High-temperature applications', 'Semiconductors', 'Abrasive materials']
        },
        {
          name: 'Graphene Composite',
          formula: 'Graphene-Polymer',
          matchScore: 82,
          properties: { weight: 'Very Low', strength: 'Exceptional', conductivity: 'Excellent', flexibility: 'High' },
          lattice: { type: 'Layered structure', density: 'Next-gen optimized' },
          applications: ['Flexible electronics', 'Aerospace', 'Energy storage']
        }
      ]
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsAnalyzing(true);
    
    // TODO: Connect to backend API
    // For now, simulate API call with contextual results
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisResults({
        ...getContextualResults(query),
        query: query
      });
      setActiveTab('results'); // Switch to results tab
    }, 2000);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-green-50/30">
      {/* Material Memory Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Database className="text-green-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800">Material Memory</h2>
          </div>
        </div>

        {/* Search */}
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search materials..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
            />
          </div>
        </div>

        {/* Material List */}
        <div className="flex-1 overflow-y-auto px-2 py-4 space-y-1">
          {materials.map((material) => (
            <div 
              key={material.id}
              onClick={() => setSelectedMaterial(selectedMaterial === material.id ? null : material.id)}
              className={`p-3 rounded-lg cursor-pointer transition-all ${
                selectedMaterial === material.id 
                  ? 'bg-green-50 border border-green-200' 
                  : 'hover:bg-gray-50'
              }`}
            >
              <p className="text-sm font-medium text-gray-800 truncate">{material.name}</p>
              <p className="text-xs text-gray-500 mt-1">{material.date}</p>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="h-full bg-gradient-to-br from-gray-50 to-green-50/30 p-8">
          <div className="max-w-6xl mx-auto h-full flex flex-col">
            {/* Tabs */}
            <div className="flex gap-4 mb-6">
              <button 
                onClick={() => setActiveTab('input')}
                className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all ${
                  activeTab === 'input' 
                    ? 'bg-green-600 text-white shadow-md' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Input Material
              </button>
              <button 
                onClick={() => setActiveTab('results')}
                className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all ${
                  activeTab === 'results' 
                    ? 'bg-green-600 text-white shadow-md' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <LayoutDashboard size={18} />
                Analysis Results
              </button>
            </div>

            {/* Content */}
            {activeTab === 'input' ? (
              <div className="flex-1 bg-white rounded-xl shadow-lg p-8 flex flex-col">
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="text-green-600" size={24} />
                    <h1 className="text-2xl font-bold text-gray-800">Material Design Assistant</h1>
                  </div>
                  <p className="text-gray-600">Describe what you need in natural language - our AI will find the perfect material and generate optimal lattice structures</p>
                </div>

              {/* Example Prompts */}
              <div className="mb-6 flex flex-wrap gap-2">
                <span className="text-sm text-gray-500">Try:</span>
                <button 
                  onClick={() => setQuery("I need a lightweight baseball bat with high durability")}
                  className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm hover:bg-green-100 transition-colors"
                >
                  Lightweight baseball bat
                </button>
                <button 
                  onClick={() => setQuery("Aerospace material for high-temperature applications")}
                  className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm hover:bg-green-100 transition-colors"
                >
                  High-temperature aerospace
                </button>
                <button 
                  onClick={() => setQuery("Strong yet lightweight vehicle frame material")}
                  className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm hover:bg-green-100 transition-colors"
                >
                  Vehicle frame material
                </button>
              </div>

              {/* Text Area */}
              <div className="flex-1 mb-6">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Example: I need a lightweight but strong material for a baseball bat that can handle high impact forces while remaining easy to swing. The material should be durable, corrosion-resistant, and suitable for outdoor sports equipment."
                  className="w-full h-full border-2 border-gray-200 rounded-xl p-6 focus:outline-none focus:border-green-500 resize-none text-gray-700 text-base leading-relaxed"
                />
              </div>

                {/* Action Button */}
                <div className="flex justify-end">
                  <button
                    onClick={handleSubmit}
                    disabled={!query.trim() || isAnalyzing}
                    className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2 shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send size={18} />
                    {isAnalyzing ? 'Storing & Analyzing...' : 'Store & Analyze Material'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex-1 bg-white rounded-xl shadow-lg p-8 flex flex-col">
                {/* Analysis Results Content */}
                {analysisResults ? (
                  <>
                    <div className="mb-6">
                      <h2 className="text-2xl font-bold text-gray-800 mb-2">Analysis Results</h2>
                      <p className="text-gray-600">Query: "{analysisResults.query}"</p>
                    </div>

                    <div className="space-y-4">
                      {analysisResults.matchedMaterials.map((material: any, index: number) => (
                        <div key={index} className="border-2 border-gray-200 rounded-xl p-6 hover:border-green-400 hover:shadow-lg transition-all bg-white group cursor-pointer animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: `${index * 100}ms` }}>
                          {/* Header */}
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h3 className="text-xl font-semibold text-gray-800">{material.name}</h3>
                              {material.formula && <p className="text-sm text-gray-500 mt-1">{material.formula}</p>}
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-gray-500">Match Score</span>
                              <span className="px-4 py-1 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-full font-semibold shadow-md group-hover:shadow-lg transition-shadow">
                                {material.matchScore}%
                              </span>
                            </div>
                          </div>

                          {/* Properties Grid */}
                          <div className="grid grid-cols-3 gap-4 mb-4">
                            {Object.entries(material.properties).slice(0, 3).map(([key, value]: [string, any]) => (
                              <div key={key} className="bg-gray-50 rounded-lg p-3 group-hover:bg-green-50 transition-colors">
                                <p className="text-xs text-gray-500 mb-1 uppercase tracking-wide">{key}</p>
                                <p className="font-semibold text-gray-800 text-sm">{value}</p>
                              </div>
                            ))}
                          </div>

                          {/* Lattice Info */}
                          {material.lattice && (
                            <div className="border-t border-gray-200 pt-4 mb-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Database className="text-green-600 group-hover:text-green-700 transition-colors" size={16} />
                                <p className="text-sm font-semibold text-gray-800">Lattice Structure</p>
                              </div>
                              <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gradient-to-br from-green-50 to-white rounded-lg p-3">
                                  <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wide">Type</p>
                                  <p className="text-sm font-semibold text-gray-800">{material.lattice.type}</p>
                                </div>
                                <div className="bg-gradient-to-br from-green-50 to-white rounded-lg p-3">
                                  <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wide">Optimization</p>
                                  <p className="text-sm font-semibold text-gray-800">{material.lattice.density}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Applications */}
                          {material.applications && (
                            <div className="border-t border-gray-200 pt-4">
                              <p className="text-sm font-semibold text-gray-800 mb-3">Recommended Applications:</p>
                              <div className="flex flex-wrap gap-2">
                                {material.applications.map((app: string, idx: number) => (
                                  <span key={idx} className="px-3 py-1.5 bg-gradient-to-r from-green-50 to-green-100 text-green-700 rounded-full text-xs font-medium hover:from-green-100 hover:to-green-200 transition-all cursor-default">
                                    {app}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <p className="text-gray-500">No results yet. Submit a query to see analysis results.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
