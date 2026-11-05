"""
Compliance Model Service for Indian MSME regulatory analysis
Integrates InLegalBERT and CUAD-India dataset for specialized compliance detection
Handles GST, Labor Laws, Commercial Contracts, and other Indian regulatory frameworks
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
import re
from datetime import datetime

# Hugging Face Inference
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    InferenceClient = None

# Vertex AI (alternative)
try:
    from google.cloud import aiplatform
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    aiplatform = None

logger = logging.getLogger(__name__)

class ComplianceModelService:
    """Compliance model service with InLegalBERT and CUAD-India integration"""
    
    def __init__(self):
        self.hf_client = None
        self.vertex_client = None
        self.hf_token = os.environ.get('HF_TOKEN')
        self.hf_model = os.environ.get('INLEGALBERT_MODEL', 'law-ai/InLegalBERT')
        self.vertex_enabled = os.environ.get('VERTEX_ENABLED', 'false').lower() == 'true'
        self.vertex_project = os.environ.get('VERTEX_PROJECT_ID')
        self.vertex_location = os.environ.get('VERTEX_LOCATION', 'asia-south1')
        self.confidence_threshold = float(os.environ.get('COMPLIANCE_CONFIDENCE_THRESHOLD', '0.7'))
        
        # Model configurations
        self.model_configs = {
            'inlegalbert': {
                'hf_model': 'law-ai/InLegalBERT',
                'vertex_model': None,  # Will be set if using Vertex
                'max_length': 512,
                'task': 'classification'
            }
        }
        
        # CUAD-India compliance categories
        self.cuad_india_categories = self._load_cuad_india_categories()
        
        # Indian regulatory rules
        self.regulatory_rules = self._load_regulatory_rules()
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize model clients"""
        # Initialize Hugging Face client
        if self.hf_token and HF_AVAILABLE:
            try:
                self.hf_client = InferenceClient(token=self.hf_token)
                logger.info("✓ Hugging Face Inference client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize HF client: {e}")
        
        # Initialize Vertex AI client
        if self.vertex_enabled and VERTEX_AVAILABLE and self.vertex_project:
            try:
                aiplatform.init(project=self.vertex_project, location=self.vertex_location)
                self.vertex_client = aiplatform
                logger.info("✓ Vertex AI client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Vertex AI client: {e}")
    
    def _load_cuad_india_categories(self) -> Dict[str, Dict[str, Any]]:
        """Load CUAD-India compliance categories specific to Indian MSMEs"""
        return {
            'gst_compliance': {
                'name': 'GST Compliance',
                'categories': [
                    'gst_registration', 'gst_return_filing', 'gst_invoice_format',
                    'hsn_sac_codes', 'gst_rates', 'input_tax_credit', 'reverse_charge',
                    'gst_audit', 'gst_penalties', 'gst_refund'
                ],
                'keywords': [
                    'gst', 'cgst', 'sgst', 'igst', 'gstr', 'hsn', 'sac', 'gstin',
                    'tax invoice', 'bill of supply', 'credit note', 'debit note',
                    'input tax credit', 'reverse charge', 'gst return'
                ],
                'severity': 'high'
            },
            'labor_laws': {
                'name': 'Labor Law Compliance',
                'categories': [
                    'minimum_wages', 'working_hours', 'overtime', 'leave_entitlement',
                    'pf_contribution', 'esic_contribution', 'gratuity', 'bonus',
                    'contract_labor', 'apprentice', 'safety_measures', 'sexual_harassment'
                ],
                'keywords': [
                    'minimum wages', 'working hours', 'overtime', 'leave', 'pf', 'epf',
                    'esic', 'gratuity', 'bonus', 'contract labor', 'apprentice',
                    'safety', 'harassment', 'employee', 'worker', 'wages'
                ],
                'severity': 'high'
            },
            'commercial_contracts': {
                'name': 'Commercial Contract Compliance',
                'categories': [
                    'payment_terms', 'delivery_terms', 'warranty', 'liability',
                    'force_majeure', 'termination', 'dispute_resolution', 'governing_law',
                    'intellectual_property', 'confidentiality', 'indemnity', 'penalty'
                ],
                'keywords': [
                    'payment', 'delivery', 'warranty', 'liability', 'force majeure',
                    'termination', 'dispute', 'governing law', 'jurisdiction',
                    'intellectual property', 'confidentiality', 'indemnity', 'penalty'
                ],
                'severity': 'medium'
            },
            'environmental_compliance': {
                'name': 'Environmental Compliance',
                'categories': [
                    'pollution_control', 'waste_management', 'environmental_clearance',
                    'water_usage', 'energy_efficiency', 'carbon_footprint', 'renewable_energy'
                ],
                'keywords': [
                    'pollution', 'waste', 'environmental', 'clearance', 'water',
                    'energy', 'carbon', 'renewable', 'sustainability'
                ],
                'severity': 'medium'
            },
            'safety_compliance': {
                'name': 'Safety Compliance',
                'categories': [
                    'workplace_safety', 'fire_safety', 'electrical_safety',
                    'machinery_safety', 'personal_protective_equipment', 'emergency_procedures'
                ],
                'keywords': [
                    'safety', 'fire', 'electrical', 'machinery', 'ppe',
                    'emergency', 'accident', 'hazard', 'risk'
                ],
                'severity': 'high'
            }
        }
    
    def _load_regulatory_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load Indian regulatory rules and patterns"""
        return {
            'gst_rules': [
                {
                    'name': 'GST Registration Required',
                    'pattern': r'gstin|gst\s+registration|gst\s+number',
                    'severity': 'high',
                    'description': 'GST registration is mandatory for businesses above threshold'
                },
                {
                    'name': 'HSN/SAC Code Missing',
                    'pattern': r'hsn|sac',
                    'severity': 'medium',
                    'description': 'HSN/SAC codes should be mentioned for proper classification'
                },
                {
                    'name': 'GST Return Filing',
                    'pattern': r'gstr|gst\s+return|monthly\s+return',
                    'severity': 'high',
                    'description': 'Regular GST return filing is mandatory'
                }
            ],
            'labor_rules': [
                {
                    'name': 'Minimum Wages Compliance',
                    'pattern': r'minimum\s+wages|wage\s+rate',
                    'severity': 'high',
                    'description': 'Must comply with state minimum wage rates'
                },
                {
                    'name': 'PF Contribution',
                    'pattern': r'provident\s+fund|pf\s+contribution|epf',
                    'severity': 'high',
                    'description': 'PF contribution is mandatory for eligible employees'
                },
                {
                    'name': 'Working Hours',
                    'pattern': r'working\s+hours|overtime|8\s+hours',
                    'severity': 'medium',
                    'description': 'Working hours should comply with labor laws'
                }
            ],
            'contract_rules': [
                {
                    'name': 'Payment Terms',
                    'pattern': r'payment\s+terms|credit\s+period|due\s+date',
                    'severity': 'medium',
                    'description': 'Clear payment terms should be specified'
                },
                {
                    'name': 'Force Majeure',
                    'pattern': r'force\s+majeure|act\s+of\s+god|unforeseen',
                    'severity': 'low',
                    'description': 'Force majeure clause provides protection'
                },
                {
                    'name': 'Dispute Resolution',
                    'pattern': r'dispute\s+resolution|arbitration|jurisdiction',
                    'severity': 'medium',
                    'description': 'Dispute resolution mechanism should be clear'
                }
            ]
        }
    
    async def analyze_compliance(self, document_text: str, document_type: str = None, 
                               domains: List[str] = None) -> Dict[str, Any]:
        """
        Analyze document for Indian regulatory compliance
        
        Args:
            document_text: Document text to analyze
            document_type: Type of document (gst_form, labor_document, etc.)
            domains: Specific compliance domains to check
            
        Returns:
            Compliance analysis result
        """
        if not document_text or not document_text.strip():
            return {
                'compliance_score': 0.0,
                'violations': [],
                'recommendations': [],
                'categories_analyzed': [],
                'confidence': 0.0,
                'error': 'Empty document text'
            }
        
        try:
            # Determine domains to analyze
            if not domains:
                domains = self._determine_domains(document_type, document_text)
            
            # Run compliance analysis
            analysis_result = {
                'compliance_score': 0.0,
                'violations': [],
                'recommendations': [],
                'categories_analyzed': domains,
                'confidence': 0.0,
                'model_used': 'inlegalbert',
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Analyze each domain
            total_score = 0
            total_weight = 0
            
            for domain in domains:
                if domain in self.cuad_india_categories:
                    domain_result = await self._analyze_domain(document_text, domain)
                    analysis_result['violations'].extend(domain_result['violations'])
                    analysis_result['recommendations'].extend(domain_result['recommendations'])
                    
                    # Weight by severity
                    weight = 3 if self.cuad_india_categories[domain]['severity'] == 'high' else 2
                    total_score += domain_result['score'] * weight
                    total_weight += weight
            
            # Calculate overall compliance score
            if total_weight > 0:
                analysis_result['compliance_score'] = total_score / total_weight
            
            # Apply rule-based checks
            rule_violations = await self._check_regulatory_rules(document_text, domains)
            analysis_result['violations'].extend(rule_violations)
            
            # Generate recommendations
            analysis_result['recommendations'] = self._generate_recommendations(
                analysis_result['violations'], domains
            )
            
            # Calculate confidence
            analysis_result['confidence'] = self._calculate_confidence(
                analysis_result['violations'], 
                analysis_result['compliance_score']
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {e}")
            return {
                'compliance_score': 0.0,
                'violations': [],
                'recommendations': [],
                'categories_analyzed': domains or [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _determine_domains(self, document_type: str, document_text: str) -> List[str]:
        """Determine which compliance domains to analyze based on document type and content"""
        domains = []
        
        # Add domains based on document type
        if document_type == 'gst_form':
            domains.append('gst_compliance')
        elif document_type == 'labor_document':
            domains.append('labor_laws')
        elif document_type == 'commercial_contract':
            domains.append('commercial_contracts')
        
        # Add domains based on content analysis
        text_lower = document_text.lower()
        
        if any(keyword in text_lower for keyword in ['gst', 'cgst', 'sgst', 'igst', 'gstin']):
            domains.append('gst_compliance')
        
        if any(keyword in text_lower for keyword in ['employee', 'worker', 'wages', 'pf', 'esic']):
            domains.append('labor_laws')
        
        if any(keyword in text_lower for keyword in ['agreement', 'contract', 'terms', 'liability']):
            domains.append('commercial_contracts')
        
        if any(keyword in text_lower for keyword in ['pollution', 'waste', 'environmental']):
            domains.append('environmental_compliance')
        
        if any(keyword in text_lower for keyword in ['safety', 'fire', 'accident', 'hazard']):
            domains.append('safety_compliance')
        
        # Default to all domains if none determined
        if not domains:
            domains = list(self.cuad_india_categories.keys())
        
        return domains
    
    async def _analyze_domain(self, document_text: str, domain: str) -> Dict[str, Any]:
        """Analyze specific compliance domain"""
        domain_config = self.cuad_india_categories[domain]
        violations = []
        recommendations = []
        score = 1.0  # Start with perfect score
        
        # Check for required categories
        for category in domain_config['categories']:
            category_present = await self._check_category_presence(document_text, category)
            if not category_present['present']:
                violations.append({
                    'category': category,
                    'domain': domain,
                    'severity': domain_config['severity'],
                    'description': f'Missing {category} information',
                    'confidence': category_present['confidence']
                })
                score -= 0.1  # Reduce score for missing categories
        
        # Check for keyword presence
        keyword_matches = 0
        for keyword in domain_config['keywords']:
            if keyword.lower() in document_text.lower():
                keyword_matches += 1
        
        # Calculate score based on keyword coverage
        keyword_score = keyword_matches / len(domain_config['keywords'])
        score = (score + keyword_score) / 2
        
        # Generate domain-specific recommendations
        if score < 0.7:
            recommendations.append({
                'domain': domain,
                'priority': 'high' if domain_config['severity'] == 'high' else 'medium',
                'description': f'Improve {domain_config["name"]} compliance documentation'
            })
        
        return {
            'domain': domain,
            'score': max(score, 0.0),
            'violations': violations,
            'recommendations': recommendations
        }
    
    async def _check_category_presence(self, text: str, category: str) -> Dict[str, Any]:
        """Check if a specific category is present in the text"""
        # Prefer InLegalBERT/HF inference when available; fallback to patterns
        if self.hf_client and self.hf_token:
            try:
                hf_result = await self._hf_classify_category(text, category)
                if hf_result is not None:
                    return hf_result
            except Exception as e:
                logger.warning(f"HF classification failed for {category}: {e}")
        
        text_lower = text.lower()
        category_patterns = {
            'gst_registration': r'gstin|gst\s+registration|gst\s+number',
            'minimum_wages': r'minimum\s+wages|wage\s+rate',
            'payment_terms': r'payment\s+terms|credit\s+period',
            'force_majeure': r'force\s+majeure|act\s+of\s+god',
            'dispute_resolution': r'dispute\s+resolution|arbitration'
        }
        
        pattern = category_patterns.get(category, r'\b' + category.replace('_', r'\s+') + r'\b')
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        
        return {
            'present': len(matches) > 0,
            'confidence': min(len(matches) * 0.2, 1.0),
            'matches': len(matches)
        }

    async def _hf_classify_category(self, text: str, category: str) -> Optional[Dict[str, Any]]:
        """Use HF Inference text classification to detect category presence.
        Returns None if the model/task is unavailable.
        """
        try:
            # Some HF models expose text-classification, others require zero-shot labels.
            # We attempt text_classification; if unsupported, we gracefully fallback.
            # Labels we care about: the specific category vs 'other'.
            labels = [category.replace('_', ' '), 'other']
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.hf_client.text_classification(
                    inputs=text[:4000],  # keep payload modest
                    model=self.hf_model,
                    params={
                        'candidate_labels': labels,
                        'multi_label': False
                    }
                )
            )
            # Normalise output: HF can return list of dicts or dict
            scores = []
            if isinstance(result, list):
                scores = result
            elif isinstance(result, dict):
                scores = result.get('labels', [])
            
            # Try to extract a score for our category
            score_for_cat = 0.0
            if isinstance(scores, list) and scores and isinstance(scores[0], dict) and 'label' in scores[0]:
                for item in scores:
                    if item.get('label', '').lower().strip() == labels[0].lower().strip():
                        score_for_cat = float(item.get('score', 0.0))
                        break
            elif isinstance(result, dict) and 'scores' in result and 'labels' in result:
                # Alternative schema
                for label, score in zip(result.get('labels', []), result.get('scores', [])):
                    if str(label).lower().strip() == labels[0].lower().strip():
                        score_for_cat = float(score)
                        break
            
            present = score_for_cat >= self.confidence_threshold
            return {
                'present': present,
                'confidence': float(score_for_cat),
                'matches': 1 if present else 0
            }
        except Exception as e:
            # If the model/task is not compatible, signal caller to fallback
            logger.debug(f"HF classify exception for {category}: {e}")
            return None
    
    async def _check_regulatory_rules(self, text: str, domains: List[str]) -> List[Dict[str, Any]]:
        """Check document against regulatory rules"""
        violations = []
        text_lower = text.lower()
        
        for domain in domains:
            if domain in self.regulatory_rules:
                for rule in self.regulatory_rules[domain]:
                    pattern = rule['pattern']
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    
                    if not matches:  # Rule not found
                        violations.append({
                            'rule_name': rule['name'],
                            'domain': domain,
                            'severity': rule['severity'],
                            'description': rule['description'],
                            'confidence': 0.8  # High confidence for missing rules
                        })
        
        return violations
    
    def _generate_recommendations(self, violations: List[Dict[str, Any]], domains: List[str]) -> List[Dict[str, Any]]:
        """Generate compliance recommendations based on violations"""
        recommendations = []
        
        # Group violations by domain
        domain_violations = {}
        for violation in violations:
            domain = violation.get('domain', 'general')
            if domain not in domain_violations:
                domain_violations[domain] = []
            domain_violations[domain].append(violation)
        
        # Generate domain-specific recommendations
        for domain, domain_violations_list in domain_violations.items():
            high_severity = [v for v in domain_violations_list if v.get('severity') == 'high']
            medium_severity = [v for v in domain_violations_list if v.get('severity') == 'medium']
            
            if high_severity:
                recommendations.append({
                    'domain': domain,
                    'priority': 'high',
                    'description': f'Address {len(high_severity)} high-severity compliance issues in {domain}',
                    'count': len(high_severity)
                })
            
            if medium_severity:
                recommendations.append({
                    'domain': domain,
                    'priority': 'medium',
                    'description': f'Review {len(medium_severity)} medium-severity compliance issues in {domain}',
                    'count': len(medium_severity)
                })
        
        return recommendations
    
    def _calculate_confidence(self, violations: List[Dict[str, Any]], compliance_score: float) -> float:
        """Calculate confidence in the compliance analysis"""
        if not violations:
            return 0.9  # High confidence if no violations found
        
        # Base confidence on score and violation count
        base_confidence = compliance_score
        
        # Adjust based on violation severity
        high_severity_count = len([v for v in violations if v.get('severity') == 'high'])
        if high_severity_count > 0:
            base_confidence -= 0.1 * high_severity_count
        
        return max(min(base_confidence, 1.0), 0.0)
    
    async def get_compliance_benchmarks(self, sector: str = None) -> Dict[str, Any]:
        """Get compliance benchmarks for comparison"""
        # This would typically query BigQuery for aggregated data
        # For now, returning static benchmarks
        
        benchmarks = {
            'gst_compliance': {
                'average_score': 0.75,
                'common_violations': ['missing_hsn_codes', 'incorrect_gst_rates'],
                'improvement_tips': ['Ensure HSN/SAC codes are mentioned', 'Verify GST rates']
            },
            'labor_laws': {
                'average_score': 0.68,
                'common_violations': ['missing_pf_contribution', 'overtime_calculation'],
                'improvement_tips': ['Document PF contributions clearly', 'Specify overtime rates']
            },
            'commercial_contracts': {
                'average_score': 0.82,
                'common_violations': ['unclear_payment_terms', 'missing_force_majeure'],
                'improvement_tips': ['Define clear payment terms', 'Include force majeure clause']
            }
        }
        
        if sector:
            # Add sector-specific benchmarks
            benchmarks['sector'] = sector
            benchmarks['sector_notes'] = f'Benchmarks for {sector} sector'
        
        return benchmarks

# Global compliance model service instance
compliance_model_service = ComplianceModelService()
