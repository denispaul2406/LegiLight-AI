import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import axios from 'axios';
import { Upload, FileText, Shield, DollarSign, Users, MessageCircle, Trash2, Download, AlertTriangle, CheckCircle, AlertCircle, Sparkles, TrendingUp, BarChart3, Zap, Brain, Target } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [currentView, setCurrentView] = useState('landing');
  const [documentText, setDocumentText] = useState('');
  const [documentFile, setDocumentFile] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [question, setQuestion] = useState('');
  const [questionResponse, setQuestionResponse] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [sampleContracts, setSampleContracts] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [cuadSamples, setCuadSamples] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [useEnhancedAnalysis, setUseEnhancedAnalysis] = useState(true);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);

  // Add debugging for state changes
  useEffect(() => {
    console.log('App state updated:', {
      currentView,
      hasDocumentText: !!documentText,
      hasDocumentFile: !!documentFile,
      isAnalyzing,
      useEnhancedAnalysis
    });
  }, [currentView, documentText, documentFile, isAnalyzing, useEnhancedAnalysis]);

  // Add global event debugging
  useEffect(() => {
    const debugEvents = (e) => {
      if (['click', 'submit', 'keydown', 'change'].includes(e.type)) {
        console.log('Event triggered:', {
          type: e.type,
          target: e.target.tagName,
          classList: e.target.className,
          defaultPrevented: e.defaultPrevented
        });
      }
    };
    
    document.addEventListener('click', debugEvents, true);
    document.addEventListener('submit', debugEvents, true);
    document.addEventListener('keydown', debugEvents, true);
    document.addEventListener('change', debugEvents, true);
    
    return () => {
      document.removeEventListener('click', debugEvents, true);
      document.removeEventListener('submit', debugEvents, true);
      document.removeEventListener('keydown', debugEvents, true);
      document.removeEventListener('change', debugEvents, true);
    };
  }, []);

  useEffect(() => {
    checkHealthStatus();
    loadSampleContracts();
    loadDocuments();
    loadCuadSamples();
    loadAnalyticsData();
  }, []);

  const checkHealthStatus = async () => {
    try {
      const response = await axios.get(`${API}/health`);
      setHealthStatus(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'error', services: { ai_analysis: false, database: false } });
    }
  };

  const loadSampleContracts = async () => {
    try {
      const response = await axios.get(`${API}/sample-contracts`);
      setSampleContracts(response.data.sample_contracts || []);
    } catch (error) {
      console.error('Failed to load sample contracts:', error);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API}/documents`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const loadCuadSamples = async () => {
    try {
      const response = await axios.get(`${API}/cuad-samples`);
      setCuadSamples(response.data.samples || []);
    } catch (error) {
      console.error('Failed to load CUAD samples:', error);
    }
  };

  const loadAnalyticsData = async () => {
    try {
      const response = await axios.get(`${API}/analytics/insights`);
      setAnalyticsData(response.data.analytics || null);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    }
  };

  const handleFileUpload = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const file = event.target.files[0];
    if (file) {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      const supportedFormats = ['txt', 'docx', 'pdf'];
      
      if (supportedFormats.includes(fileExtension)) {
        if (fileExtension === 'txt') {
          const reader = new FileReader();
          reader.onload = (e) => {
            setDocumentText(e.target.result);
            setDocumentName(file.name);
          };
          reader.readAsText(file);
        } else {
          setDocumentFile(file);
          setDocumentName(file.name);
          setDocumentText('');
        }
      } else {
        alert('Please upload a supported file format (.txt, .docx, .pdf)');
      }
    }
  }, []);

  const handleSampleContract = (contract) => {
    setDocumentText(contract.text);
    setDocumentName(contract.name);
    setDocumentFile(null); // Clear any uploaded file
    setCurrentView('upload');
  };

  const handleViewChange = (view, event) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    setCurrentView(view);
  };

  const analyzeDocument = async () => {
    // Check if we have either text or file
    if (!documentText.trim() && !documentFile) {
      alert('Please enter document text or upload a file');
      return;
    }

    console.log('Starting analysis...', {
      hasText: !!documentText.trim(),
      hasFile: !!documentFile,
      enhanced: useEnhancedAnalysis,
      textLength: documentText.length
    });

    setIsAnalyzing(true);
    try {
      let response;
      
      if (documentFile) {
        // Handle file upload
        const formData = new FormData();
        formData.append('file', documentFile);
        formData.append('analysis_type', useEnhancedAnalysis ? 'enhanced' : 'comprehensive');
        
        const endpoint = useEnhancedAnalysis ? '/analyze-enhanced/upload' : '/analyze/upload';
        console.log('Making file upload request to:', `${API}${endpoint}`);
        response = await axios.post(`${API}${endpoint}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        // Handle text input
        const endpoint = useEnhancedAnalysis ? '/analyze-enhanced' : '/analyze/document';
        const payload = {
          document_text: documentText,
          document_name: documentName || 'Untitled Document',
          analysis_type: useEnhancedAnalysis ? 'enhanced' : 'comprehensive'
        };
        console.log('Making text analysis request to:', `${API}${endpoint}`, payload);
        response = await axios.post(`${API}${endpoint}`, payload);
      }

      console.log('Analysis response:', response.data);
      setAnalysisResult(response.data);
      setCurrentView('results');
      setChatHistory([]);
      setShowSuccessAnimation(true);
      setTimeout(() => setShowSuccessAnimation(false), 3000);
      loadDocuments(); // Refresh document list
    } catch (error) {
      console.error('Analysis failed:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error detail array:', error.response?.data?.detail);
      console.error('Request config:', error.config);
      
      let errorMessage = 'Analysis failed: ';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage += error.response.data.detail.map(d => d.msg || d).join(', ');
        } else {
          errorMessage += error.response.data.detail;
        }
      } else {
        errorMessage += error.message;
      }
      
      alert(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || !analysisResult) return;

    try {
      const response = await axios.post(`${API}/question`, {
        document_id: analysisResult.analysis_id,
        question: question
      });
      
      const newChat = {
        question: question,
        answer: response.data.answer,
        confidence: response.data.confidence,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setChatHistory([...chatHistory, newChat]);
      setQuestionResponse(response.data);
      setQuestion('');
    } catch (error) {
      console.error('Question failed:', error);
      alert('Failed to get answer: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteDocument = async (analysisId) => {
    try {
      await axios.delete(`${API}/document/${analysisId}`);
      loadDocuments();
      if (analysisResult && analysisResult.analysis_id === analysisId) {
        setAnalysisResult(null);
        setCurrentView('landing');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete document');
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return <CheckCircle className="w-5 h-5" />;
      case 'medium': return <AlertCircle className="w-5 h-5" />;
      case 'high': return <AlertTriangle className="w-5 h-5" />;
      default: return <AlertCircle className="w-5 h-5" />;
    }
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                LegiLight AI
              </h1>
              <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
            </div>
            <div className="flex items-center space-x-4">
              {healthStatus && (
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                  healthStatus.status === 'healthy' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  <div className={`w-2 h-2 rounded-full animate-pulse ${
                    healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span>{healthStatus.status === 'healthy' ? 'AI Enhanced Ready' : 'Service Issue'}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6 leading-tight animate-fadeInUp">
            Transform Legal Contracts into{' '}
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent relative">
              Crystal Clear Insights
            </span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto animate-fadeInUp">
            Powered by Google Gemini 2.5 Flash + CUAD Dataset. Analyze contracts in 60 seconds with 
            <span className="font-semibold text-blue-600">AI-enhanced legal intelligence</span>. 
            Get risk assessments, clause analysis, and plain-language summaries.
          </p>
          
          {/* Enhanced Value Proposition Cards */}
          <div className="flex flex-wrap justify-center gap-6 mb-12 animate-fadeInUp">
            {[
              { icon: Brain, text: "CUAD Enhanced", color: "purple" },
              { icon: Zap, text: "60s Analysis", color: "yellow" },
              { icon: Shield, text: "Privacy-First", color: "blue" },
              { icon: Target, text: "Risk Aware", color: "red" }
            ].map((item, index) => (
              <div
                key={item.text}
                className="flex items-center space-x-2 px-4 py-2 bg-white rounded-full shadow-md cursor-pointer btn-hover-lift"
              >
                <item.icon className={`w-5 h-5 text-${item.color}-600`} />
                <span className="text-sm font-medium text-gray-700">{item.text}</span>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={(e) => handleViewChange('upload', e)}
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg group btn-hover-lift"
          >
            <Upload className="w-5 h-5 mr-2 group-hover:animate-bounce" />
            Start AI Analysis
            <Sparkles className="w-4 h-4 ml-2" />
          </button>
          
          {analyticsData && (
            <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto animate-fadeInUp">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{analyticsData.total_documents_analyzed}+</div>
                <div className="text-sm text-gray-600">Documents Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{(analyticsData.average_confidence * 100).toFixed(0)}%</div>
                <div className="text-sm text-gray-600">AI Confidence</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{analyticsData.enhanced_analysis_percentage}%</div>
                <div className="text-sm text-gray-600">Enhanced Analysis</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">2.1s</div>
                <div className="text-sm text-gray-600">Avg Processing</div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">1. Upload</h4>
              <p className="text-gray-600">Upload your contract (.txt, .docx, .pdf) or paste text directly. Multiple formats supported.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">2. Analyze</h4>
              <p className="text-gray-600">AI reads and analyzes your document, identifying key clauses and risks.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">3. Understand</h4>
              <p className="text-gray-600">Get plain-language summaries and ask questions about specific clauses.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Contracts */}
      {sampleContracts.length > 0 && (
        <section className="py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">Try Sample Contracts</h3>
            <div className="grid md:grid-cols-2 gap-6">
              {sampleContracts.map((contract) => (
                <div key={contract.id} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
                  <h4 className="text-xl font-semibold mb-2">{contract.name}</h4>
                  <p className="text-gray-600 mb-4">{contract.description}</p>
                  <button
                    type="button"
                    onClick={() => handleSampleContract(contract)}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Analyze Sample
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400 mb-4">
            <strong>Disclaimer:</strong> LegiLight provides informational analysis only and does not constitute legal advice. 
            Always consult with qualified legal professionals for legal matters.
          </p>
          <p className="text-sm text-gray-500">
            Built for Google Cloud GenAI Exchange Hackathon 2025
          </p>
        </div>
      </footer>
    </div>
  );

  // Enhanced Upload Component with Animations and CUAD Integration
  const UploadView = () => {
    return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-purple-600 animate-pulse" />
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI-Enhanced Document Analysis
              </h2>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Enhanced Analysis</label>
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setUseEnhancedAnalysis(!useEnhancedAnalysis);
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    useEnhancedAnalysis ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                    useEnhancedAnalysis ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              <button
                type="button"
                onClick={(e) => handleViewChange('landing', e)}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors flex items-center space-x-2"
              >
                <span>← Back to Home</span>
              </button>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Upload Section - Wrapped in form to control submission */}
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Form submission prevented - calling analyzeDocument instead');
                if (!isAnalyzing && (documentText.trim() || documentFile)) {
                  analyzeDocument();
                }
                return false;
              }}
            >
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Name
                </label>
                <input
                  type="text"
                  value={documentName}
                  onChange={(e) => setDocumentName(e.target.value)}
                  placeholder="Enter document name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                  <Upload className="w-4 h-4" />
                  <span>Upload Document or Drag & Drop</span>
                </label>
                <div className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300 ${
                  documentFile
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                }`}>
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    accept=".txt,.docx,.pdf"
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer block">
                    {documentFile ? (
                      <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
                    ) : (
                      <Upload className="mx-auto h-12 w-12 mb-4 text-gray-400" />
                    )}
                    <p className={`text-sm mb-2 ${
                      documentFile ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {documentFile
                        ? `Selected: ${documentFile.name}`
                        : 'Click to upload or drag and drop'
                      }
                    </p>
                    <p className="text-xs text-gray-500">
                      Supports: .txt, .docx, .pdf files (max 100KB)
                    </p>
                  </label>
                  
                  {documentFile && (
                    <div className="mt-4 p-3 bg-green-100 rounded-lg">
                      <p className="text-sm text-green-800 flex items-center justify-center space-x-2">
                        <FileText className="w-4 h-4" />
                        <span>{documentFile.name}</span>
                      </p>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setDocumentFile(null);
                          setDocumentName('');
                        }}
                        className="mt-2 text-xs text-red-600 hover:text-red-800"
                      >
                        Remove file
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Or paste document text directly</span>
                </label>
                <textarea
                  value={documentText}
                  onChange={(e) => {
                    setDocumentText(e.target.value);
                    if (e.target.value.trim()) {
                      setDocumentFile(null);
                    }
                  }}
                  placeholder={documentFile ? "File selected for analysis. You can still paste text here to override." : "Paste your legal document text here..."}
                  rows={12}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  disabled={documentFile && !documentText}
                />
                {documentFile && !documentText && (
                  <p className="mt-2 text-sm text-gray-500 flex items-center space-x-2">
                    <Zap className="w-4 h-4" />
                    <span>File ready for AI analysis. Text extraction will happen automatically.</span>
                  </p>
                )}
              </div>

              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('Analyze button clicked', {
                    isAnalyzing,
                    hasText: !!documentText.trim(),
                    hasFile: !!documentFile,
                    textLength: documentText.length
                  });
                  analyzeDocument();
                }}
                disabled={isAnalyzing || (!documentText.trim() && !documentFile)}
                className={`w-full px-6 py-4 font-semibold rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 btn-hover-lift shadow-xl ${
                  useEnhancedAnalysis
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isAnalyzing ? (
                  <>
                    <div className="rounded-full h-5 w-5 border-2 border-white border-t-transparent animate-spin" />
                    <span>{documentFile ? 'Processing File with AI...' : 'Analyzing Document...'}</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5" />
                    <span>
                      {useEnhancedAnalysis ? 'Enhanced AI Analysis' : 'Standard Analysis'}
                      {documentFile ? ` (${documentFile.name.split('.').pop().toUpperCase()})` : ''}
                    </span>
                    <Sparkles className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
            </form>

            {/* CUAD Samples & Features */}
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
                  <Target className="w-5 h-5 text-purple-600" />
                  <span>Enhanced Analysis Features</span>
                </h3>
                <div className="space-y-3">
                  {[
                    { icon: Brain, text: "CUAD Dataset Integration", desc: "Contract Understanding Atticus Dataset analysis" },
                    { icon: Zap, text: "Parallel AI Processing", desc: "Gemini 2.5 Flash + specialized models" },
                    { icon: Target, text: "Advanced Risk Detection", desc: "Enhanced clause categorization" },
                    { icon: BarChart3, text: "Confidence Scoring", desc: "Multi-model validation" }
                  ].map((feature, index) => (
                    <div
                      key={feature.text}
                      className="flex items-start space-x-3"
                    >
                      <feature.icon className="w-5 h-5 text-purple-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-sm text-gray-800">{feature.text}</p>
                        <p className="text-xs text-gray-600">{feature.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Contracts */}
              {(cuadSamples.length > 0 || sampleContracts.length > 0) && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <span>Try Sample Contracts</span>
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {/* CUAD Enhanced Samples */}
                    {cuadSamples.slice(0, 3).map((sample, index) => (
                      <div
                        key={sample.id}
                        className="bg-white p-4 rounded-lg shadow-sm border border-purple-200 cursor-pointer hover:scale-105 transition-transform card-hover"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setDocumentText(sample.sample_text);
                          setDocumentName(sample.name);
                          setDocumentFile(null);
                        }}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm text-gray-800">{sample.name}</h4>
                          <div className="flex items-center space-x-1">
                            <Sparkles className="w-3 h-3 text-purple-500" />
                            <span className="text-xs text-purple-600 font-medium">CUAD</span>
                          </div>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">{sample.description}</p>
                        <div className="flex items-center justify-between">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            sample.risk_level === 'Low' ? 'bg-green-100 text-green-700' :
                            sample.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {sample.risk_level} Risk
                          </span>
                          <span className="text-xs text-blue-600 hover:text-blue-800">Try Sample →</span>
                        </div>
                      </div>
                    ))}
                    
                    {/* Regular Samples */}
                    {sampleContracts.slice(0, 2).map((contract, index) => (
                      <div
                        key={contract.id}
                        className="bg-white p-4 rounded-lg shadow-sm border cursor-pointer hover:scale-105 transition-transform card-hover"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setDocumentText(contract.text);
                          setDocumentName(contract.name);
                          setDocumentFile(null);
                        }}
                      >
                        <h4 className="font-medium text-sm text-gray-800 mb-2">{contract.name}</h4>
                        <p className="text-xs text-gray-600 mb-2">{contract.description}</p>
                        <span className="text-xs text-blue-600 hover:text-blue-800">Try Sample →</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Success Animation */}
      {showSuccessAnimation && (
        <div className="fixed top-4 right-4 bg-green-500 text-white p-4 rounded-lg shadow-lg z-50 animate-fadeInUp">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5" />
            <span>Analysis Complete!</span>
          </div>
        </div>
      )}
    </div>
    );
  };

  // Enhanced Results Component with CUAD Analysis and Charts
  const ResultsView = () => {
    const riskColors = ['#ef4444', '#f59e0b', '#10b981']; // Red, Yellow, Green
    const riskData = analysisResult?.risk_assessment ? [
      { name: 'High Risk', value: (analysisResult.risk_assessment.red_flags?.length || 0), color: '#ef4444' },
      { name: 'Medium Risk', value: (analysisResult.risk_assessment.yellow_flags?.length || 0), color: '#f59e0b' },
      { name: 'Low Risk', value: (analysisResult.risk_assessment.green_flags?.length || 0), color: '#10b981' }
    ].filter(item => item.value > 0) : [];

    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <CheckCircle className="w-8 h-8 text-green-500 animate-pulse" />
              <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                Analysis Complete
              </h2>
              {analysisResult?.analysis_method && (
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                  {analysisResult.analysis_method}
                </span>
              )}
            </div>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={(e) => handleViewChange('upload', e)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 btn-hover-lift"
              >
                <Upload className="w-4 h-4" />
                <span>New Analysis</span>
              </button>
              <button
                type="button"
                onClick={(e) => handleViewChange('landing', e)}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                Home
              </button>
            </div>
          </div>

          {analysisResult && (
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Main Analysis */}
              <div className="lg:col-span-2 space-y-6">
                {/* Document Summary */}
                <div className="bg-white rounded-xl shadow-lg p-6 card-hover">
                  <div className="flex items-center mb-6">
                    <FileText className="w-6 h-6 text-blue-600 mr-2" />
                    <h3 className="text-xl font-semibold">Document Summary</h3>
                    {analysisResult.analysis_method?.includes('Enhanced') && (
                      <Sparkles className="w-5 h-5 text-purple-500 ml-2 animate-pulse" />
                    )}
                  </div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                      { label: 'Document Type', value: analysisResult.document_summary?.document_type },
                      { label: 'Main Purpose', value: analysisResult.document_summary?.main_purpose },
                      { label: 'Key Parties', value: analysisResult.document_summary?.key_parties?.join(', ') },
                      { label: 'AI Confidence', value: `${Math.round(analysisResult.ai_confidence * 100)}%` },
                      { label: 'Processing Time', value: `${analysisResult.processing_time?.toFixed(2)}s` },
                      { label: 'Analysis Method', value: analysisResult.analysis_method || 'Standard' }
                    ].map((item, index) => (
                      <div key={item.label} className="animate-fadeInUp">
                        <p className="text-sm text-gray-600 mb-1">{item.label}</p>
                        <p className="font-medium text-gray-900">{item.value || 'N/A'}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Risk Assessment with Charts */}
                <div className="bg-white rounded-xl shadow-lg p-6 card-hover">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                      <div className={`flex items-center space-x-2 ${getRiskColor(analysisResult.risk_assessment?.overall_risk_level)} px-3 py-1 rounded-lg mr-4`}>
                        {getRiskIcon(analysisResult.risk_assessment?.overall_risk_level)}
                        <span className="font-semibold">
                          {analysisResult.risk_assessment?.overall_risk_level || 'Unknown'} Risk Level
                        </span>
                      </div>
                    </div>
                    {riskData.length > 0 && (
                      <div className="w-32 h-32">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={riskData}
                              cx="50%"
                              cy="50%"
                              innerRadius={25}
                              outerRadius={50}
                              dataKey="value"
                            >
                              {riskData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { title: 'Red Flags', items: analysisResult.risk_assessment?.red_flags, color: 'red', icon: AlertTriangle },
                      { title: 'Yellow Flags', items: analysisResult.risk_assessment?.yellow_flags, color: 'yellow', icon: AlertCircle },
                      { title: 'Green Flags', items: analysisResult.risk_assessment?.green_flags, color: 'green', icon: CheckCircle }
                    ].map((category, categoryIndex) => (
                      <div key={category.title} className="animate-fadeInUp">
                        <h4 className={`font-medium mb-3 flex items-center space-x-2 text-${category.color}-600`}>
                          <category.icon className="w-4 h-4" />
                          <span>{category.title}</span>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                            {category.items?.length || 0}
                          </span>
                        </h4>
                        <ul className="text-sm space-y-2 max-h-32 overflow-y-auto">
                          {category.items?.map((item, index) => (
                            <li key={index} className="flex items-start space-x-2 animate-fadeInUp">
                              <span className={`w-2 h-2 rounded-full bg-${category.color}-500 mt-1.5 flex-shrink-0`}></span>
                              <span>{item}</span>
                            </li>
                          )) || (
                            <li className="text-gray-500 italic">None identified</li>
                          )}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CUAD Analysis (if available) */}
                {analysisResult.cuad_analysis && (
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl shadow-lg p-6 border-2 border-purple-200 card-hover">
                    <div className="flex items-center mb-6">
                      <Target className="w-6 h-6 text-purple-600 mr-2" />
                      <h3 className="text-xl font-semibold text-purple-800">CUAD Enhanced Analysis</h3>
                      <Sparkles className="w-5 h-5 text-purple-500 ml-2 animate-pulse" />
                    </div>
                    
                    {analysisResult.enhanced_insights && (
                      <div className="grid md:grid-cols-3 gap-6 mb-6">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-purple-600 mb-1">
                            {Math.round(analysisResult.enhanced_insights.contract_completeness * 100)}%
                          </div>
                          <div className="text-sm text-gray-600">Contract Completeness</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-blue-600 mb-1">
                            {analysisResult.cuad_analysis.categories_analyzed || 0}
                          </div>
                          <div className="text-sm text-gray-600">CUAD Categories</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-600 mb-1">
                            {Math.round(analysisResult.cuad_analysis.confidence_score * 100)}%
                          </div>
                          <div className="text-sm text-gray-600">CUAD Confidence</div>
                        </div>
                      </div>
                    )}
                    
                    {analysisResult.enhanced_insights?.missing_clauses?.length > 0 && (
                      <div className="bg-white rounded-lg p-4">
                        <h4 className="font-medium text-red-600 mb-3 flex items-center space-x-2">
                          <AlertTriangle className="w-4 h-4" />
                          <span>Missing Important Clauses</span>
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {analysisResult.enhanced_insights.missing_clauses.map((clause, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                            >
                              {clause}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {analysisResult.enhanced_insights?.recommendations?.length > 0 && (
                      <div className="bg-white rounded-lg p-4 mt-4">
                        <h4 className="font-medium text-blue-600 mb-3 flex items-center space-x-2">
                          <TrendingUp className="w-4 h-4" />
                          <span>AI Recommendations</span>
                        </h4>
                        <ul className="space-y-2">
                          {analysisResult.enhanced_insights.recommendations.map((rec, index) => (
                            <li
                              key={index}
                              className="flex items-start space-x-2"
                            >
                              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Financial Terms */}
                <div className="bg-white rounded-xl shadow-lg p-6 card-hover">
                  <div className="flex items-center mb-4">
                    <DollarSign className="w-6 h-6 text-green-600 mr-2" />
                    <h3 className="text-xl font-semibold">Financial Terms</h3>
                  </div>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-2">Payment Amounts</h4>
                      <ul className="text-sm space-y-1">
                        {analysisResult.financial_terms?.payment_amounts?.map((amount, index) => (
                          <li key={index}>{amount}</li>
                        )) || <li className="text-gray-500">None specified</li>}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Penalties & Fees</h4>
                      <ul className="text-sm space-y-1">
                        {analysisResult.financial_terms?.penalties?.concat(analysisResult.financial_terms?.fees || [])?.map((item, index) => (
                          <li key={index}>{item}</li>
                        )) || <li className="text-gray-500">None specified</li>}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Obligations */}
                <div className="bg-white rounded-xl shadow-lg p-6 card-hover">
                  <div className="flex items-center mb-4">
                    <Users className="w-6 h-6 text-purple-600 mr-2" />
                    <h3 className="text-xl font-semibold">Key Obligations</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Your Obligations</h4>
                      <ul className="text-sm space-y-1 list-disc list-inside">
                        {analysisResult.obligations?.party_1_obligations?.map((obligation, index) => (
                          <li key={index}>{obligation}</li>
                        )) || <li className="text-gray-500">None specified</li>}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Other Party's Obligations</h4>
                      <ul className="text-sm space-y-1 list-disc list-inside">
                        {analysisResult.obligations?.party_2_obligations?.map((obligation, index) => (
                          <li key={index}>{obligation}</li>
                        )) || <li className="text-gray-500">None specified</li>}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Key Clauses */}
                {analysisResult.key_clauses && analysisResult.key_clauses.length > 0 && (
                  <div className="bg-white rounded-xl shadow-lg p-6 card-hover">
                    <h3 className="text-xl font-semibold mb-4">Key Clauses</h3>
                    <div className="space-y-4">
                      {analysisResult.key_clauses.map((clause, index) => (
                        <div 
                          key={index}
                          className="border-l-4 border-blue-500 pl-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium capitalize">{clause.clause_type}</h4>
                            <span className={`px-2 py-1 rounded text-xs ${
                              clause.importance === 'High' ? 'bg-red-100 text-red-800' :
                              clause.importance === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {clause.importance} Priority
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{clause.plain_language}</p>
                          <details className="text-xs text-gray-500">
                            <summary className="cursor-pointer hover:text-gray-700">View original text</summary>
                            <p className="mt-2 p-2 bg-gray-50 rounded">{clause.clause_text}</p>
                          </details>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Q&A Sidebar */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
                  <div className="flex items-center mb-4">
                    <MessageCircle className="w-6 h-6 text-indigo-600 mr-2" />
                    <h3 className="text-xl font-semibold">Ask Questions</h3>
                    <Sparkles className="w-4 h-4 text-indigo-500 ml-2 animate-pulse" />
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask about this document..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            askQuestion();
                          }
                        }}
                      />
                      <button
                        type="button"
                        onClick={askQuestion}
                        disabled={!question.trim()}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Ask
                      </button>
                    </div>

                    {/* Chat History */}
                    <div className="max-h-96 overflow-y-auto space-y-3">
                      {chatHistory.map((chat, index) => (
                        <div 
                          key={index}
                          className="border-b border-gray-100 pb-3 last:border-b-0"
                        >
                          <div className="bg-indigo-50 p-3 rounded-lg mb-2">
                            <p className="text-sm font-medium text-indigo-900">Q: {chat.question}</p>
                          </div>
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <p className="text-sm text-gray-800">{chat.answer}</p>
                            <div className="flex items-center justify-between mt-2">
                              <span className="text-xs text-gray-500">
                                Confidence: {Math.round(chat.confidence * 100)}%
                              </span>
                              <span className="text-xs text-gray-500">{chat.timestamp}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {chatHistory.length === 0 && (
                      <div className="text-center text-gray-500 py-8">
                        <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">Ask questions about this document</p>
                        <p className="text-xs mt-1">Try: "What are the key risks?" or "Explain termination clause"</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case 'upload':
        return <UploadView />;
      case 'results':
        return <ResultsView />;
      default:
        return <LandingPage />;
    }
  };

  return renderCurrentView();
};

export default App;