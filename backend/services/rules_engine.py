"""
Rules Engine for Indian MSME compliance checking
Manages custom compliance rules and evaluates documents against them
Supports GST, Labor Laws, Commercial Contracts, and custom business rules
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import json
import re
import asyncio
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class RulesEngine:
    """Rules engine for compliance checking and custom rule evaluation"""
    
    def __init__(self):
        self.rules_storage_path = os.environ.get('RULES_STORAGE_PATH', 'backend/data/rules.json')
        self.confidence_threshold = float(os.environ.get('RULES_CONFIDENCE_THRESHOLD', '0.7'))
        self.max_rules_per_domain = int(os.environ.get('MAX_RULES_PER_DOMAIN', '50'))
        
        # Load existing rules
        self.rules = self._load_rules()
        
        # Built-in Indian regulatory rules
        self.builtin_rules = self._load_builtin_rules()
    
    def _load_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load custom rules from storage"""
        try:
            if os.path.exists(self.rules_storage_path):
                with open(self.rules_storage_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    return rules_data.get('rules', {})
            else:
                # Create directory if it doesn't exist
                Path(self.rules_storage_path).parent.mkdir(parents=True, exist_ok=True)
                return {}
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return {}
    
    def _save_rules(self):
        """Save rules to storage"""
        try:
            rules_data = {
                'rules': self.rules,
                'last_updated': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            with open(self.rules_storage_path, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Rules saved successfully")
        except Exception as e:
            logger.error(f"Failed to save rules: {e}")
    
    def _load_builtin_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load built-in Indian regulatory rules"""
        return {
            'gst': [
                {
                    'id': 'gst_001',
                    'name': 'GST Registration Required',
                    'description': 'GST registration number must be present',
                    'pattern': r'gstin\s*:?\s*[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}',
                    'severity': 'high',
                    'category': 'registration',
                    'confidence_threshold': 0.9,
                    'message': 'GST registration number is missing or invalid',
                    'remediation': 'Obtain GST registration and include GSTIN in documents'
                },
                {
                    'id': 'gst_002',
                    'name': 'HSN/SAC Code Required',
                    'description': 'HSN or SAC codes must be mentioned for goods/services',
                    'pattern': r'(hsn|sac)\s*:?\s*[0-9]{4,8}',
                    'severity': 'medium',
                    'category': 'classification',
                    'confidence_threshold': 0.8,
                    'message': 'HSN/SAC codes are missing',
                    'remediation': 'Include appropriate HSN/SAC codes for goods/services'
                },
                {
                    'id': 'gst_003',
                    'name': 'GST Rate Specification',
                    'description': 'GST rates should be clearly specified',
                    'pattern': r'gst\s*:?\s*[0-9]+(?:\.[0-9]+)?%|cgst\s*:?\s*[0-9]+(?:\.[0-9]+)?%|sgst\s*:?\s*[0-9]+(?:\.[0-9]+)?%|igst\s*:?\s*[0-9]+(?:\.[0-9]+)?%',
                    'severity': 'medium',
                    'category': 'tax_calculation',
                    'confidence_threshold': 0.7,
                    'message': 'GST rates are not clearly specified',
                    'remediation': 'Specify applicable GST rates (CGST, SGST, IGST)'
                }
            ],
            'labor': [
                {
                    'id': 'labor_001',
                    'name': 'Minimum Wages Compliance',
                    'description': 'Wages must comply with minimum wage requirements',
                    'pattern': r'minimum\s+wages?|wage\s+rate|daily\s+wage',
                    'severity': 'high',
                    'category': 'wages',
                    'confidence_threshold': 0.8,
                    'message': 'Minimum wage compliance not clearly addressed',
                    'remediation': 'Ensure wages meet state minimum wage requirements'
                },
                {
                    'id': 'labor_002',
                    'name': 'PF Contribution Mention',
                    'description': 'Provident Fund contribution should be mentioned',
                    'pattern': r'provident\s+fund|pf\s+contribution|epf',
                    'severity': 'high',
                    'category': 'benefits',
                    'confidence_threshold': 0.7,
                    'message': 'PF contribution details are missing',
                    'remediation': 'Include PF contribution details for eligible employees'
                },
                {
                    'id': 'labor_003',
                    'name': 'Working Hours Specification',
                    'description': 'Working hours should be clearly specified',
                    'pattern': r'working\s+hours?|8\s+hours?|overtime|shift\s+timing',
                    'severity': 'medium',
                    'category': 'working_conditions',
                    'confidence_threshold': 0.6,
                    'message': 'Working hours are not clearly specified',
                    'remediation': 'Specify working hours and overtime policies'
                }
            ],
            'contract': [
                {
                    'id': 'contract_001',
                    'name': 'Payment Terms Clarity',
                    'description': 'Payment terms should be clearly defined',
                    'pattern': r'payment\s+terms?|credit\s+period|due\s+date|net\s+[0-9]+',
                    'severity': 'medium',
                    'category': 'payment',
                    'confidence_threshold': 0.7,
                    'message': 'Payment terms are not clearly defined',
                    'remediation': 'Specify clear payment terms and credit periods'
                },
                {
                    'id': 'contract_002',
                    'name': 'Force Majeure Clause',
                    'description': 'Force majeure clause should be included',
                    'pattern': r'force\s+majeure|act\s+of\s+god|unforeseen\s+circumstances',
                    'severity': 'low',
                    'category': 'risk_management',
                    'confidence_threshold': 0.6,
                    'message': 'Force majeure clause is missing',
                    'remediation': 'Include force majeure clause for risk protection'
                },
                {
                    'id': 'contract_003',
                    'name': 'Dispute Resolution Mechanism',
                    'description': 'Dispute resolution mechanism should be specified',
                    'pattern': r'dispute\s+resolution|arbitration|jurisdiction|governing\s+law',
                    'severity': 'medium',
                    'category': 'dispute_resolution',
                    'confidence_threshold': 0.7,
                    'message': 'Dispute resolution mechanism is not specified',
                    'remediation': 'Include clear dispute resolution and jurisdiction clauses'
                }
            ]
        }
    
    async def evaluate_document(self, document_text: str, domains: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate document against all applicable rules
        
        Args:
            document_text: Document text to evaluate
            domains: Specific domains to check (gst, labor, contract, etc.)
            
        Returns:
            Evaluation result with rule violations and recommendations
        """
        if not document_text or not document_text.strip():
            return {
                'total_rules_checked': 0,
                'violations': [],
                'recommendations': [],
                'compliance_score': 0.0,
                'confidence': 0.0,
                'error': 'Empty document text'
            }
        
        try:
            # Determine domains to check
            if not domains:
                domains = self._detect_domains(document_text)
            
            # Get applicable rules
            applicable_rules = self._get_applicable_rules(domains)
            
            # Evaluate rules
            violations = []
            recommendations = []
            total_rules = len(applicable_rules)
            passed_rules = 0
            
            for rule in applicable_rules:
                try:
                    result = await self._evaluate_rule(document_text, rule)
                    if not result['passed']:
                        violations.append({
                            'rule_id': rule['id'],
                            'rule_name': rule['name'],
                            'domain': rule.get('domain', 'general'),
                            'severity': rule['severity'],
                            'message': rule['message'],
                            'remediation': rule['remediation'],
                            'confidence': result['confidence'],
                            'matched_text': result.get('matched_text', ''),
                            'line_number': result.get('line_number', 0)
                        })
                        
                        recommendations.append({
                            'rule_id': rule['id'],
                            'priority': rule['severity'],
                            'description': rule['remediation'],
                            'category': rule['category']
                        })
                    else:
                        passed_rules += 1
                        
                except Exception as e:
                    logger.error(f"Error evaluating rule {rule['id']}: {e}")
                    continue
            
            # Calculate compliance score
            compliance_score = passed_rules / total_rules if total_rules > 0 else 0.0
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(violations, total_rules)
            
            return {
                'total_rules_checked': total_rules,
                'passed_rules': passed_rules,
                'violations': violations,
                'recommendations': recommendations,
                'compliance_score': compliance_score,
                'confidence': confidence,
                'domains_checked': domains,
                'evaluation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document evaluation failed: {e}")
            return {
                'total_rules_checked': 0,
                'violations': [],
                'recommendations': [],
                'compliance_score': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _detect_domains(self, document_text: str) -> List[str]:
        """Detect relevant domains based on document content"""
        domains = []
        text_lower = document_text.lower()
        
        # GST indicators
        if any(keyword in text_lower for keyword in ['gst', 'cgst', 'sgst', 'igst', 'gstin', 'hsn', 'sac']):
            domains.append('gst')
        
        # Labor law indicators
        if any(keyword in text_lower for keyword in ['employee', 'worker', 'wages', 'pf', 'esic', 'gratuity', 'bonus']):
            domains.append('labor')
        
        # Contract indicators
        if any(keyword in text_lower for keyword in ['agreement', 'contract', 'terms', 'liability', 'warranty']):
            domains.append('contract')
        
        # Default to all domains if none detected
        if not domains:
            domains = ['gst', 'labor', 'contract']
        
        return domains
    
    def _get_applicable_rules(self, domains: List[str]) -> List[Dict[str, Any]]:
        """Get all applicable rules for the given domains"""
        applicable_rules = []
        
        # Add built-in rules
        for domain in domains:
            if domain in self.builtin_rules:
                for rule in self.builtin_rules[domain]:
                    rule_copy = rule.copy()
                    rule_copy['domain'] = domain
                    rule_copy['source'] = 'builtin'
                    applicable_rules.append(rule_copy)
        
        # Add custom rules
        for domain in domains:
            if domain in self.rules:
                for rule in self.rules[domain]:
                    rule_copy = rule.copy()
                    rule_copy['domain'] = domain
                    rule_copy['source'] = 'custom'
                    applicable_rules.append(rule_copy)
        
        return applicable_rules
    
    async def _evaluate_rule(self, document_text: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single rule against the document"""
        try:
            pattern = rule['pattern']
            confidence_threshold = rule.get('confidence_threshold', self.confidence_threshold)
            
            # Search for pattern matches
            matches = re.finditer(pattern, document_text, re.IGNORECASE | re.MULTILINE)
            match_list = list(matches)
            
            if match_list:
                # Rule passed - pattern found
                matched_text = match_list[0].group(0)
                line_number = document_text[:match_list[0].start()].count('\n') + 1
                
                return {
                    'passed': True,
                    'confidence': 1.0,
                    'matched_text': matched_text,
                    'line_number': line_number,
                    'match_count': len(match_list)
                }
            else:
                # Rule failed - pattern not found
                return {
                    'passed': False,
                    'confidence': confidence_threshold,
                    'matched_text': '',
                    'line_number': 0,
                    'match_count': 0
                }
                
        except Exception as e:
            logger.error(f"Error evaluating rule {rule['id']}: {e}")
            return {
                'passed': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _calculate_confidence(self, violations: List[Dict[str, Any]], total_rules: int) -> float:
        """Calculate overall confidence in the evaluation"""
        if total_rules == 0:
            return 0.0
        
        if not violations:
            return 0.9  # High confidence if no violations
        
        # Calculate average confidence of violations
        violation_confidences = [v.get('confidence', 0.5) for v in violations]
        avg_confidence = sum(violation_confidences) / len(violation_confidences)
        
        # Adjust based on rule coverage
        coverage_factor = len(violations) / total_rules
        
        return min(avg_confidence * (1 + coverage_factor), 1.0)
    
    async def create_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom rule"""
        try:
            # Validate rule data
            required_fields = ['name', 'description', 'pattern', 'severity', 'domain']
            for field in required_fields:
                if field not in rule_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Generate rule ID
            rule_id = f"custom_{int(datetime.utcnow().timestamp())}"
            rule_data['id'] = rule_id
            rule_data['created_at'] = datetime.utcnow().isoformat()
            rule_data['source'] = 'custom'
            
            # Add to rules storage
            domain = rule_data['domain']
            if domain not in self.rules:
                self.rules[domain] = []
            
            # Check rule limit
            if len(self.rules[domain]) >= self.max_rules_per_domain:
                return {
                    'success': False, 
                    'error': f'Maximum rules limit ({self.max_rules_per_domain}) reached for domain {domain}'
                }
            
            self.rules[domain].append(rule_data)
            self._save_rules()
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': 'Rule created successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            return {'success': False, 'error': str(e)}
    
    async def update_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing custom rule"""
        try:
            # Find and update rule
            for domain, rules in self.rules.items():
                for i, rule in enumerate(rules):
                    if rule['id'] == rule_id and rule.get('source') == 'custom':
                        # Update rule data
                        rule_data['id'] = rule_id
                        rule_data['updated_at'] = datetime.utcnow().isoformat()
                        rule_data['source'] = 'custom'
                        
                        self.rules[domain][i] = rule_data
                        self._save_rules()
                        
                        return {
                            'success': True,
                            'message': 'Rule updated successfully'
                        }
            
            return {'success': False, 'error': 'Rule not found'}
            
        except Exception as e:
            logger.error(f"Failed to update rule: {e}")
            return {'success': False, 'error': str(e)}
    
    async def delete_rule(self, rule_id: str) -> Dict[str, Any]:
        """Delete a custom rule"""
        try:
            # Find and delete rule
            for domain, rules in self.rules.items():
                for i, rule in enumerate(rules):
                    if rule['id'] == rule_id and rule.get('source') == 'custom':
                        del self.rules[domain][i]
                        self._save_rules()
                        
                        return {
                            'success': True,
                            'message': 'Rule deleted successfully'
                        }
            
            return {'success': False, 'error': 'Rule not found'}
            
        except Exception as e:
            logger.error(f"Failed to delete rule: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_rules(self, domain: str = None) -> Dict[str, Any]:
        """Get rules for a specific domain or all domains"""
        try:
            if domain:
                return {
                    'domain': domain,
                    'rules': self.rules.get(domain, []),
                    'builtin_rules': self.builtin_rules.get(domain, []),
                    'total_count': len(self.rules.get(domain, [])) + len(self.builtin_rules.get(domain, []))
                }
            else:
                all_rules = {}
                for domain in set(list(self.rules.keys()) + list(self.builtin_rules.keys())):
                    all_rules[domain] = {
                        'custom_rules': self.rules.get(domain, []),
                        'builtin_rules': self.builtin_rules.get(domain, []),
                        'total_count': len(self.rules.get(domain, [])) + len(self.builtin_rules.get(domain, []))
                    }
                
                return {
                    'domains': all_rules,
                    'total_domains': len(all_rules)
                }
                
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return {'error': str(e)}
    
    async def test_rule(self, rule_pattern: str, test_text: str) -> Dict[str, Any]:
        """Test a rule pattern against sample text"""
        try:
            matches = re.findall(rule_pattern, test_text, re.IGNORECASE)
            match_count = len(matches)
            
            return {
                'success': True,
                'matches': matches,
                'match_count': match_count,
                'pattern_valid': True
            }
            
        except re.error as e:
            return {
                'success': False,
                'error': f'Invalid regex pattern: {str(e)}',
                'pattern_valid': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pattern_valid': True
            }

# Global rules engine instance
rules_engine = RulesEngine()
