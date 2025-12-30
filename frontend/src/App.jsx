import { useState, useCallback } from 'react';
import { 
  FileText, 
  Loader2, 
  AlertCircle, 
  CheckCircle2, 
  Copy, 
  Download,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import ComponentCard from './components/ComponentCard';
import SampleTexts from './components/SampleTexts';

// ⚠️ UPDATE THIS URL after deploying your backend to Render
const API_URL = 'https://your-app-name.onrender.com';  // e.g., 'https://clinical-api.onrender.com'

// For local development, use:
// const API_URL = 'http://localhost:5000';

function App() {
  const [inputText, setInputText] = useState('');
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiInfo, setApiInfo] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const identifyComponents = useCallback(async () => {
    if (!inputText.trim()) {
      setError('Please enter some clinical text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setComponents([]);
    setApiInfo(null);

    try {
      const response = await fetch(`${API_URL}/api/identify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          options: {
            min_confidence: 0.7,
            max_components: 20
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setComponents(data.components || []);
        setApiInfo({
          model: data.model_used,
          tokens: data.usage?.total_tokens,
          count: data.total_components
        });
      } else {
        throw new Error(data.error || 'Unknown error occurred');
      }
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'Failed to connect to the API. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, [inputText]);

  const handleSampleSelect = useCallback((text) => {
    setInputText(text);
    setComponents([]);
    setError(null);
  }, []);

  const copyResults = useCallback(() => {
    const json = JSON.stringify(components, null, 2);
    navigator.clipboard.writeText(json);
  }, [components]);

  const downloadResults = useCallback(() => {
    const json = JSON.stringify(components, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'clinical-components.json';
    a.click();
    URL.revokeObjectURL(url);
  }, [components]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-clinical-500 rounded-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Clinical Component Identifier
                </h1>
                <p className="text-sm text-gray-500">
                  AI-powered extraction of reusable document components
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <Info className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Info Banner */}
      {showInfo && (
        <div className="bg-blue-50 border-b border-blue-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium">How it works:</p>
                <p className="mt-1">
                  This tool uses a fine-tuned GPT model to identify reusable components 
                  in clinical documents. Components are classified into types like 
                  boilerplate, definitions, study sections, drug info, safety, and procedures.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h2 className="font-semibold text-gray-900">Input Clinical Text</h2>
              </div>
              <div className="p-4">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste your clinical document text here...&#10;&#10;For example: protocol sections, consent forms, regulatory text, etc."
                  className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-clinical-500 focus:border-transparent transition-all"
                />
                
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    {inputText.length.toLocaleString()} characters
                  </span>
                  <button
                    onClick={identifyComponents}
                    disabled={loading || !inputText.trim()}
                    className="inline-flex items-center px-6 py-2.5 bg-clinical-600 text-white font-medium rounded-lg hover:bg-clinical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5 mr-2" />
                        Identify Components
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Sample Texts */}
            <SampleTexts onSelect={handleSampleSelect} />
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
                <h2 className="font-semibold text-gray-900">
                  Identified Components
                  {components.length > 0 && (
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      ({components.length} found)
                    </span>
                  )}
                </h2>
                {components.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={copyResults}
                      className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                      title="Copy JSON"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <button
                      onClick={downloadResults}
                      className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                      title="Download JSON"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>

              <div className="p-4 max-h-[600px] overflow-y-auto">
                {/* Error State */}
                {error && (
                  <div className="flex items-start space-x-3 p-4 bg-red-50 rounded-lg border border-red-200">
                    <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Error</p>
                      <p className="text-sm text-red-600 mt-1">{error}</p>
                    </div>
                  </div>
                )}

                {/* Loading State */}
                {loading && (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-4 border border-gray-200 rounded-lg">
                        <div className="loading-shimmer h-4 w-24 rounded mb-3" />
                        <div className="loading-shimmer h-3 w-full rounded mb-2" />
                        <div className="loading-shimmer h-3 w-3/4 rounded" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Empty State */}
                {!loading && !error && components.length === 0 && (
                  <div className="text-center py-12">
                    <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">
                      Enter clinical text and click "Identify Components" to get started
                    </p>
                  </div>
                )}

                {/* Results */}
                {!loading && components.length > 0 && (
                  <div className="space-y-4">
                    {components.map((component, index) => (
                      <ComponentCard key={index} component={component} index={index} />
                    ))}
                  </div>
                )}
              </div>

              {/* API Info Footer */}
              {apiInfo && (
                <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                  <div className="flex items-center justify-between">
                    <span>Model: {apiInfo.model}</span>
                    <span>{apiInfo.tokens?.toLocaleString()} tokens used</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Powered by OpenAI Fine-Tuned Model • 
            <a 
              href="https://github.com/yourusername/clinical-component-identifier" 
              className="text-clinical-600 hover:text-clinical-700 ml-1"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
