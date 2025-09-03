import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import axios from 'axios';
import { Upload, FileText, Brain, Target, Sparkles, Zap, CheckCircle, Shield, Clock, BarChart3, AlertTriangle, Award } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Define all components outside to prevent re-creation
const LandingPage = ({ onNavigateToUpload, sampleContracts, handleSampleContract }) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
    {/* Background decoration */}
    <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
    <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
    <div className="absolute top-40 right-10 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDelay: '2s'}}></div>
    <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDelay: '4s'}}></div>
    
    {/* Hero Section */}
    <section className="relative py-20 px-4 text-center">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-lg opacity-30 animate-pulse"></div>
            <div className="relative bg-white p-4 rounded-full shadow-xl">
              <Brain className="w-12 h-12 text-blue-600" />
            </div>
          </div>
        </div>
        
        <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent leading-tight">
          LegiLight AI
        </h1>
        
        <p className="text-2xl text-gray-700 mb-4 font-light">
          Transform Complex Legal Documents into
        </p>
        <p className="text-2xl text-gray-700 mb-12 font-light">
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-semibold">Plain Language Insights</span> in 60 Seconds
        </p>
        
        {/* Features showcase */}
        <div className="grid md:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
          <div className="bg-white/60 backdrop-blur-sm p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4 mx-auto">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Lightning Fast</h3>
            <p className="text-sm text-gray-600">AI analysis in under 60 seconds</p>
          </div>
          <div className="bg-white/60 backdrop-blur-sm p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="bg-purple-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4 mx-auto">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Risk Detection</h3>
            <p className="text-sm text-gray-600">Identify hidden risks and obligations</p>
          </div>
          <div className="bg-white/60 backdrop-blur-sm p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="bg-indigo-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4 mx-auto">
              <BarChart3 className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Insights</h3>
            <p className="text-sm text-gray-600">Key clauses and financial terms</p>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button
            type="button"
            onClick={onNavigateToUpload}
            className="group relative inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-xl hover:shadow-2xl hover:-translate-y-1 transform"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
            <Upload className="relative w-5 h-5 mr-3" />
            <span className="relative">Start AI Analysis</span>
            <Sparkles className="relative w-4 h-4 ml-3 group-hover:animate-spin" />
          </button>
          
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="w-4 h-4 mr-2" />
            <span>Free • No signup required • Instant results</span>
          </div>
        </div>
      </div>
    </section>

    {/* Sample Contracts */}
    {sampleContracts.length > 0 && (
      <section className="relative py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">Try Sample Contracts</h3>
            <p className="text-lg text-gray-600">Experience our AI analysis with real legal documents</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sampleContracts.map((contract, index) => (
              <div key={contract.id} className="group bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-gray-100">
                <div className="flex items-center mb-4">
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 w-10 h-10 rounded-xl flex items-center justify-center mr-3">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-blue-100 px-3 py-1 rounded-full text-xs font-medium text-blue-700">
                    Sample {index + 1}
                  </div>
                </div>
                <h4 className="text-xl font-semibold mb-3 text-gray-900 group-hover:text-blue-600 transition-colors">{contract.name}</h4>
                <p className="text-gray-600 mb-6 leading-relaxed">{contract.description}</p>
                <button
                  type="button"
                  onClick={() => handleSampleContract(contract)}
                  className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                >
                  Analyze Sample
                  <Sparkles className="inline w-4 h-4 ml-2" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    )}
    
    {/* Trust indicators */}
    <section className="relative py-16 px-4 bg-white/50">
      <div className="max-w-4xl mx-auto text-center">
        <div className="grid md:grid-cols-4 gap-8">
          <div className="flex flex-col items-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">10k+</div>
            <div className="text-sm text-gray-600">Documents Analyzed</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">99.8%</div>
            <div className="text-sm text-gray-600">Accuracy Rate</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-3xl font-bold text-indigo-600 mb-2">45s</div>
            <div className="text-sm text-gray-600">Average Analysis Time</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-3xl font-bold text-green-600 mb-2">24/7</div>
            <div className="text-sm text-gray-600">Always Available</div>
          </div>
        </div>
      </div>
    </section>
  </div>
);

const UploadPage = ({
  documentText,
  setDocumentText,
  documentFile,
  setDocumentFile,
  documentName,
  setDocumentName,
  useEnhancedAnalysis,
  setUseEnhancedAnalysis,
  isAnalyzing,
  handleFileUpload,
  analyzeDocument,
  onNavigateToLanding
}) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-8">
    {/* Background decoration */}
    <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
    
    <div className="max-w-6xl mx-auto px-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-white/20 p-3 rounded-xl">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white">Document Analysis Studio</h2>
                <p className="text-blue-100">Upload and analyze your legal documents with AI precision</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onNavigateToLanding}
              className="px-6 py-2 bg-white/20 text-white rounded-xl hover:bg-white/30 transition-all duration-200 backdrop-blur-sm"
            >
              ← Back to Home
            </button>
          </div>
        </div>

        {/* Analysis Type Toggle */}
        <div className="px-8 py-6 bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <Target className="w-5 h-5 text-gray-600" />
                <span className="text-lg font-medium text-gray-700">Analysis Mode</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`text-sm font-medium transition-colors ${
                  !useEnhancedAnalysis ? 'text-blue-600' : 'text-gray-500'
                }`}>Standard</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setUseEnhancedAnalysis(!useEnhancedAnalysis);
                  }}
                  className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors duration-300 focus:outline-none ${
                    useEnhancedAnalysis ? 'bg-gradient-to-r from-purple-500 to-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <span className={`inline-block h-5 w-5 rounded-full bg-white shadow-lg transition-transform duration-300 ${
                    useEnhancedAnalysis ? 'translate-x-8' : 'translate-x-1'
                  }`} />
                </button>
                <span className={`text-sm font-medium transition-colors ${
                  useEnhancedAnalysis ? 'text-purple-600' : 'text-gray-500'
                }`}>Enhanced</span>
              </div>
            </div>
            <div className="flex items-center space-x-2 bg-white/60 px-4 py-2 rounded-xl">
              {useEnhancedAnalysis ? (
                <>
                  <Sparkles className="w-4 h-4 text-purple-600" />
                  <span className="text-sm font-medium text-purple-600">Advanced CUAD Analysis</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-600">Quick Analysis</span>
                </>
              )}
            </div>
          </div>
        </div>

        <form onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          if (!isAnalyzing && (documentText.trim() || documentFile)) {
            analyzeDocument();
          }
          return false;
        }}>
          <div className="p-8 space-y-8">
            {/* Document Name */}
            <div className="space-y-3">
              <label className="flex items-center text-sm font-medium text-gray-700 space-x-2">
                <FileText className="w-4 h-4" />
                <span>Document Name</span>
              </label>
              <input
                type="text"
                value={documentName}
                onChange={(e) => setDocumentName(e.target.value)}
                placeholder="Enter a descriptive name for your document"
                className="w-full px-4 py-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50/50 hover:bg-white"
              />
            </div>

            {/* File Upload */}
            <div className="space-y-3">
              <label className="flex items-center text-sm font-medium text-gray-700 space-x-2">
                <Upload className="w-4 h-4" />
                <span>Upload Legal Document</span>
              </label>
              <div className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                documentFile 
                  ? 'border-green-400 bg-green-50/50' 
                  : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50/50'
              }`}>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  accept=".txt,.docx,.pdf"
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer block">
                  <div className="space-y-4">
                    {documentFile ? (
                      <>
                        <div className="mx-auto w-20 h-20 bg-green-100 rounded-2xl flex items-center justify-center">
                          <CheckCircle className="w-10 h-10 text-green-600" />
                        </div>
                        <div>
                          <p className="text-lg font-medium text-green-700 mb-2">File Selected Successfully</p>
                          <p className="text-sm text-green-600 bg-green-100 inline-block px-4 py-2 rounded-xl">
                            {documentFile.name}
                          </p>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="mx-auto w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center hover:bg-blue-200 transition-colors">
                          <Upload className="w-10 h-10 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-lg font-medium text-gray-700 mb-2">Drop your document here or click to browse</p>
                          <p className="text-sm text-gray-500">Supports .txt, .docx, .pdf files (max 100KB)</p>
                        </div>
                      </>
                    )}
                  </div>
                </label>
                
                {documentFile && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setDocumentFile(null);
                      setDocumentName('');
                    }}
                    className="absolute top-4 right-4 p-2 bg-red-100 text-red-600 rounded-xl hover:bg-red-200 transition-colors"
                  >
                    <span className="text-sm">Remove</span>
                  </button>
                )}
              </div>
            </div>

            {/* Text Area */}
            <div className="space-y-3">
              <label className="flex items-center text-sm font-medium text-gray-700 space-x-2">
                <FileText className="w-4 h-4" />
                <span>Or paste your document text directly</span>
              </label>
              <div className="relative">
                <textarea
                  value={documentText}
                  onChange={(e) => {
                    setDocumentText(e.target.value);
                    if (e.target.value.trim()) {
                      setDocumentFile(null);
                    }
                  }}
                  placeholder="Paste your legal document content here... 

Example: Contract agreements, terms of service, privacy policies, employment contracts, lease agreements, etc."
                  rows={14}
                  className="w-full px-6 py-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50/50 hover:bg-white resize-none"
                />
                {documentText && (
                  <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-xl text-xs text-gray-500 border">
                    {documentText.length.toLocaleString()} characters
                  </div>
                )}
              </div>
            </div>

            {/* Analyze Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={isAnalyzing || (!documentText.trim() && !documentFile)}
                className={`group relative w-full px-8 py-6 font-semibold rounded-2xl transition-all duration-300 flex items-center justify-center space-x-3 transform hover:scale-[1.02] disabled:hover:scale-100 ${
                  useEnhancedAnalysis
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg hover:shadow-purple-200'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-blue-200'
                } text-white disabled:opacity-50 disabled:cursor-not-allowed shadow-xl`}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
                
                {isAnalyzing ? (
                  <>
                    <div className="relative rounded-full h-6 w-6 border-3 border-white border-t-transparent animate-spin" />
                    <span className="relative text-lg">Analyzing Document...</span>
                    <Sparkles className="relative w-5 h-5 animate-pulse" />
                  </>
                ) : (
                  <>
                    <Brain className="relative w-6 h-6 group-hover:animate-pulse" />
                    <span className="relative text-lg">
                      {useEnhancedAnalysis ? 'Start Enhanced AI Analysis' : 'Start Standard Analysis'}
                    </span>
                    <Sparkles className="relative w-5 h-5 group-hover:rotate-12 transition-transform" />
                  </>
                )}
              </button>
              
              {!isAnalyzing && (!documentText.trim() && !documentFile) && (
                <p className="text-center text-sm text-gray-500 mt-4 flex items-center justify-center space-x-2">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Please upload a file or paste document text to begin analysis</span>
                </p>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
);

const ResultsPage = ({ analysisResult, onNavigateToUpload, onNavigateToLanding }) => {
  if (!analysisResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-12">
            <AlertTriangle className="w-16 h-16 text-orange-500 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold text-gray-900 mb-2">No Analysis Results</h3>
            <p className="text-gray-600 mb-6">Unable to display analysis results. Please try again.</p>
            <button
              type="button"
              onClick={onNavigateToUpload}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Start New Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  const {
    document_summary = {},
    risk_assessment = {},
    financial_terms = {},
    obligations = {},
    key_clauses = [],
    processing_time = 0,
    ai_confidence = 0
  } = analysisResult;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-8">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="max-w-7xl mx-auto px-4 relative">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-3xl shadow-2xl p-8 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="bg-white/20 p-4 rounded-2xl">
                <Award className="w-12 h-12 text-white" />
              </div>
              <div>
                <h2 className="text-4xl font-bold mb-2">Analysis Complete!</h2>
                <p className="text-green-100 text-lg">Your document has been successfully analyzed with AI precision</p>
                <div className="flex items-center space-x-6 mt-4">
                  <div className="flex items-center space-x-2 bg-white/20 px-4 py-2 rounded-xl">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm font-medium">{processing_time.toFixed(1)}s processing time</span>
                  </div>
                  <div className="flex items-center space-x-2 bg-white/20 px-4 py-2 rounded-xl">
                    <Brain className="w-4 h-4" />
                    <span className="text-sm font-medium">{(ai_confidence * 100).toFixed(1)}% AI confidence</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={onNavigateToUpload}
                className="px-6 py-3 bg-white/20 text-white rounded-xl hover:bg-white/30 transition-all duration-200 backdrop-blur-sm font-medium"
              >
                New Analysis
              </button>
              <button
                type="button"
                onClick={onNavigateToLanding}
                className="px-6 py-3 bg-white text-green-600 rounded-xl hover:bg-green-50 transition-colors font-medium"
              >
                ← Home
              </button>
            </div>
          </div>
        </div>

        {/* Results Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Document Summary */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-500 px-6 py-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Document Summary
              </h3>
            </div>
            <div className="p-6">
              {document_summary.summary ? (
                <div className="space-y-4">
                  <p className="text-gray-700 leading-relaxed">{document_summary.summary}</p>
                  {document_summary.document_type && (
                    <div className="bg-blue-50 p-4 rounded-2xl">
                      <div className="text-sm font-medium text-blue-700 mb-1">Document Type</div>
                      <div className="text-blue-800">{document_summary.document_type}</div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 italic">No summary available</p>
              )}
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-red-500 to-pink-500 px-6 py-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Risk Assessment
              </h3>
            </div>
            <div className="p-6">
              {risk_assessment.overall_risk_level && (
                <div className="mb-4">
                  <div className={`inline-block px-4 py-2 rounded-xl font-medium ${
                    risk_assessment.overall_risk_level === 'High' ? 'bg-red-100 text-red-800' :
                    risk_assessment.overall_risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {risk_assessment.overall_risk_level} Risk Level
                  </div>
                </div>
              )}
              
              {risk_assessment.risks && risk_assessment.risks.length > 0 ? (
                <div className="space-y-3">
                  {risk_assessment.risks.slice(0, 3).map((risk, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-xl">
                      <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-red-800">{risk}</span>
                    </div>
                  ))}
                  {risk_assessment.risks.length > 3 && (
                    <p className="text-sm text-gray-500 text-center">
                      +{risk_assessment.risks.length - 3} more risks identified
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 italic">No specific risks identified</p>
              )}
            </div>
          </div>

          {/* Financial Terms */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Financial Terms
              </h3>
            </div>
            <div className="p-6">
              {Object.keys(financial_terms).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(financial_terms).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center p-3 bg-green-50 rounded-xl">
                      <span className="text-sm font-medium text-green-700 capitalize">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm text-green-800 font-semibold">{value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No financial terms identified</p>
              )}
            </div>
          </div>

          {/* Key Obligations */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-500 px-6 py-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Key Obligations
              </h3>
            </div>
            <div className="p-6">
              {obligations.parties && obligations.parties.length > 0 ? (
                <div className="space-y-4">
                  {obligations.parties.map((party, index) => (
                    <div key={index} className="p-4 bg-purple-50 rounded-xl">
                      <h4 className="font-medium text-purple-800 mb-2">{party.name || `Party ${index + 1}`}</h4>
                      {party.obligations && party.obligations.length > 0 ? (
                        <ul className="space-y-1">
                          {party.obligations.slice(0, 2).map((obligation, idx) => (
                            <li key={idx} className="text-sm text-purple-700 flex items-start">
                              <span className="w-1.5 h-1.5 bg-purple-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                              {obligation}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-purple-600 italic">No specific obligations listed</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No party obligations identified</p>
              )}
            </div>
          </div>
        </div>

        {/* Key Clauses */}
        {key_clauses && key_clauses.length > 0 && (
          <div className="mt-8 bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                Key Clauses Identified ({key_clauses.length})
              </h3>
            </div>
            <div className="p-6">
              <div className="grid md:grid-cols-2 gap-6">
                {key_clauses.slice(0, 4).map((clause, index) => (
                  <div key={index} className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100">
                    <h4 className="font-medium text-indigo-800 mb-2">
                      {clause.type || clause.title || `Clause ${index + 1}`}
                    </h4>
                    <p className="text-sm text-indigo-700 leading-relaxed">
                      {clause.text || clause.content || 'No content available'}
                    </p>
                    {clause.importance && (
                      <div className="mt-2">
                        <span className={`inline-block px-2 py-1 rounded-lg text-xs font-medium ${
                          clause.importance === 'High' ? 'bg-red-100 text-red-700' :
                          clause.importance === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {clause.importance} Importance
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {key_clauses.length > 4 && (
                <div className="mt-6 text-center">
                  <p className="text-sm text-gray-500">
                    +{key_clauses.length - 4} more clauses identified in the full analysis
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-12 text-center">
          <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-white/20">
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">What's Next?</h3>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                type="button"
                onClick={onNavigateToUpload}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Analyze Another Document
              </button>
              <button
                type="button"
                onClick={onNavigateToLanding}
                className="px-8 py-4 bg-white text-gray-700 font-semibold rounded-2xl hover:bg-gray-50 transition-colors shadow-lg border border-gray-200"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Fixed App component that applies all the lessons learned
const FixedApp = () => {
  const [currentView, setCurrentView] = useState('landing');
  const [documentText, setDocumentText] = useState('');
  const [documentFile, setDocumentFile] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [useEnhancedAnalysis, setUseEnhancedAnalysis] = useState(true);
  const [sampleContracts, setSampleContracts] = useState([]);

  useEffect(() => {
    loadSampleContracts();
  }, []);

  const loadSampleContracts = async () => {
    try {
      const response = await axios.get(`${API}/sample-contracts`);
      setSampleContracts(response.data.sample_contracts || []);
    } catch (error) {
      console.error('Failed to load sample contracts:', error);
    }
  };

  const handleViewChange = useCallback((view) => {
    setCurrentView(view);
  }, []);

  const handleSampleContract = useCallback((contract) => {
    setDocumentText(contract.text);
    setDocumentName(contract.name);
    setDocumentFile(null);
    setCurrentView('upload');
  }, []);

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

  const analyzeDocument = useCallback(async () => {
    if (!documentText.trim() && !documentFile) {
      alert('Please enter document text or upload a file');
      return;
    }

    setIsAnalyzing(true);
    try {
      let response;
      
      if (documentFile) {
        const formData = new FormData();
        formData.append('file', documentFile);
        formData.append('analysis_type', useEnhancedAnalysis ? 'enhanced' : 'comprehensive');
        
        const endpoint = useEnhancedAnalysis ? '/analyze-enhanced/upload' : '/analyze/upload';
        response = await axios.post(`${API}${endpoint}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        const endpoint = useEnhancedAnalysis ? '/analyze-enhanced' : '/analyze/document';
        const payload = {
          document_text: documentText,
          document_name: documentName || 'Untitled Document',
          analysis_type: useEnhancedAnalysis ? 'enhanced' : 'comprehensive'
        };
        response = await axios.post(`${API}${endpoint}`, payload);
      }

      setAnalysisResult(response.data);
      setCurrentView('results');
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsAnalyzing(false);
    }
  }, [documentText, documentFile, documentName, useEnhancedAnalysis]);

  // Render current view using external components
  return (
    <>
      {currentView === 'landing' && (
        <LandingPage
          onNavigateToUpload={() => handleViewChange('upload')}
          sampleContracts={sampleContracts}
          handleSampleContract={handleSampleContract}
        />
      )}
      
      {currentView === 'upload' && (
        <UploadPage
          documentText={documentText}
          setDocumentText={setDocumentText}
          documentFile={documentFile}
          setDocumentFile={setDocumentFile}
          documentName={documentName}
          setDocumentName={setDocumentName}
          useEnhancedAnalysis={useEnhancedAnalysis}
          setUseEnhancedAnalysis={setUseEnhancedAnalysis}
          isAnalyzing={isAnalyzing}
          handleFileUpload={handleFileUpload}
          analyzeDocument={analyzeDocument}
          onNavigateToLanding={() => handleViewChange('landing')}
        />
      )}
      
      {currentView === 'results' && (
        <ResultsPage
          analysisResult={analysisResult}
          onNavigateToUpload={() => handleViewChange('upload')}
          onNavigateToLanding={() => handleViewChange('landing')}
        />
      )}
    </>
  );
};

export default FixedApp;