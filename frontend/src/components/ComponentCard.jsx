import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, CheckCircle2 } from 'lucide-react';

const TYPE_COLORS = {
  boilerplate: 'bg-purple-100 text-purple-800 border-purple-200',
  definition: 'bg-blue-100 text-blue-800 border-blue-200',
  study_section: 'bg-green-100 text-green-800 border-green-200',
  drug_info: 'bg-orange-100 text-orange-800 border-orange-200',
  safety: 'bg-red-100 text-red-800 border-red-200',
  procedure: 'bg-teal-100 text-teal-800 border-teal-200',
};

const REUSE_COLORS = {
  high: 'text-green-600',
  medium: 'text-yellow-600',
  low: 'text-red-600',
};

function ComponentCard({ component, index }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const typeColor = TYPE_COLORS[component.type] || 'bg-gray-100 text-gray-800 border-gray-200';
  const reuseColor = REUSE_COLORS[component.reuse_potential] || 'text-gray-600';
  
  const confidence = Math.round((component.confidence || 0) * 100);

  const copyText = () => {
    navigator.clipboard.writeText(component.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <div 
        className="px-4 py-3 bg-gray-50 cursor-pointer flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-400">#{index + 1}</span>
          <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${typeColor}`}>
            {component.type?.replace('_', ' ')}
          </span>
          <h3 className="font-medium text-gray-900 truncate max-w-[200px]">
            {component.title || 'Untitled Component'}
          </h3>
        </div>
        <div className="flex items-center space-x-4">
          {/* Confidence Badge */}
          <div className="flex items-center space-x-1">
            <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  confidence >= 90 ? 'bg-green-500' :
                  confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${confidence}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">{confidence}%</span>
          </div>
          {expanded ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-4 py-3 space-y-3">
          {/* Text Content */}
          <div className="relative">
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {component.text}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                copyText();
              }}
              className="absolute top-2 right-2 p-1.5 bg-white rounded border border-gray-200 hover:bg-gray-50 transition-colors"
              title="Copy text"
            >
              {copied ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>

          {/* Metadata */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <span className="text-gray-500">
                Reuse Potential: 
                <span className={`ml-1 font-medium capitalize ${reuseColor}`}>
                  {component.reuse_potential || 'unknown'}
                </span>
              </span>
            </div>
            {component.component_id && (
              <span className="text-xs text-gray-400 font-mono">
                {component.component_id}
              </span>
            )}
          </div>

          {/* Rationale */}
          {component.rationale && (
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                <span className="font-medium">Rationale:</span> {component.rationale}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ComponentCard;
