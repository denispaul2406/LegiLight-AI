"""
Pub/Sub Publisher for LegiLight Events
Publishes analysis completion events for downstream processing
Supports notifications, compliance alerts, and workflow automation
"""

import os
import logging
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime

# Google Cloud Pub/Sub
try:
    from google.cloud import pubsub_v1
    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False
    pubsub_v1 = None

logger = logging.getLogger(__name__)

class PubSubPublisher:
    """Pub/Sub publisher for analysis events"""
    
    def __init__(self):
        self.publisher = None
        self.pubsub_enabled = os.environ.get('PUBSUB_ENABLED', 'false').lower() == 'true'
        self.project_id = os.environ.get('GCP_PROJECT_ID')
        self.topic_name = os.environ.get('PUBSUB_TOPIC', 'analysis-completed')
        
        self._initialize_publisher()
    
    def _initialize_publisher(self):
        """Initialize Pub/Sub publisher"""
        if not self.pubsub_enabled or not PUBSUB_AVAILABLE:
            logger.info("Pub/Sub publishing not enabled or not available")
            return
        
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
            logger.info(f"✓ Pub/Sub publisher initialized for topic: {self.topic_name}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Pub/Sub publisher: {e}")
            self.publisher = None
    
    async def publish_analysis_completed(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish analysis completed event
        
        Args:
            analysis_data: Analysis result data
            
        Returns:
            Publish result with success status
        """
        if not self.pubsub_enabled or not self.publisher:
            return {
                'success': False,
                'message': 'Pub/Sub publishing not enabled',
                'published': False
            }
        
        try:
            # Prepare event data
            event_data = self._prepare_event_data(analysis_data)
            
            # Publish message
            message_data = json.dumps(event_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topic_path,
                message_data,
                **self._get_message_attributes(analysis_data)
            )
            
            message_id = future.result()
            
            logger.info(f"Published analysis event {analysis_data.get('analysis_id')} with message ID: {message_id}")
            
            return {
                'success': True,
                'message': 'Analysis event published successfully',
                'published': True,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to publish analysis event: {e}")
            return {
                'success': False,
                'message': f'Publish failed: {str(e)}',
                'published': False
            }
    
    def _prepare_event_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare analysis data for Pub/Sub event"""
        return {
            'event_type': 'analysis_completed',
            'analysis_id': analysis_data.get('analysis_id'),
            'timestamp': datetime.utcnow().isoformat(),
            'document_type': analysis_data.get('document_summary', {}).get('document_type'),
            'risk_level': analysis_data.get('risk_assessment', {}).get('overall_risk_level'),
            'compliance_score': analysis_data.get('compliance_score', 0.0),
            'ai_confidence': analysis_data.get('ai_confidence', 0.0),
            'domains_analyzed': analysis_data.get('cuad_analysis', {}).get('categories_analyzed', []),
            'violations_count': len(analysis_data.get('violations', [])),
            'recommendations_count': len(analysis_data.get('recommendations', [])),
            'processing_time': analysis_data.get('processing_time', 0.0),
            'languages_detected': analysis_data.get('languages_detected', []),
            'ocr_used': analysis_data.get('ocr_used', False),
            'translation_used': analysis_data.get('translation_used', False),
            'enhanced_analysis': analysis_data.get('analysis_method', '').lower().find('enhanced') != -1,
            'metadata': {
                'sector': analysis_data.get('sector', 'unknown'),
                'state': analysis_data.get('state', 'unknown'),
                'model_versions': analysis_data.get('model_versions', {}),
                'flags_summary': {
                    'red_flags': len(analysis_data.get('risk_assessment', {}).get('red_flags', [])),
                    'yellow_flags': len(analysis_data.get('risk_assessment', {}).get('yellow_flags', [])),
                    'green_flags': len(analysis_data.get('risk_assessment', {}).get('green_flags', []))
                }
            }
        }
    
    def _get_message_attributes(self, analysis_data: Dict[str, Any]) -> Dict[str, str]:
        """Get message attributes for Pub/Sub message"""
        risk_level = analysis_data.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
        document_type = analysis_data.get('document_summary', {}).get('document_type', 'unknown')
        
        return {
            'risk_level': risk_level,
            'document_type': document_type,
            'analysis_id': analysis_data.get('analysis_id', ''),
            'event_type': 'analysis_completed',
            'priority': 'high' if risk_level == 'high' else 'normal'
        }
    
    async def publish_high_risk_alert(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish high-risk alert event
        
        Args:
            analysis_data: Analysis result data with high risk
            
        Returns:
            Publish result
        """
        if not self.pubsub_enabled or not self.publisher:
            return {
                'success': False,
                'message': 'Pub/Sub publishing not enabled',
                'published': False
            }
        
        try:
            # Prepare high-risk alert data
            alert_data = {
                'event_type': 'high_risk_alert',
                'analysis_id': analysis_data.get('analysis_id'),
                'timestamp': datetime.utcnow().isoformat(),
                'risk_level': 'high',
                'document_type': analysis_data.get('document_summary', {}).get('document_type'),
                'compliance_score': analysis_data.get('compliance_score', 0.0),
                'red_flags': analysis_data.get('risk_assessment', {}).get('red_flags', []),
                'violations': analysis_data.get('violations', []),
                'urgent_recommendations': [
                    rec for rec in analysis_data.get('recommendations', [])
                    if rec.get('priority') == 'high'
                ],
                'metadata': {
                    'sector': analysis_data.get('sector', 'unknown'),
                    'state': analysis_data.get('state', 'unknown'),
                    'ai_confidence': analysis_data.get('ai_confidence', 0.0)
                }
            }
            
            # Publish alert
            message_data = json.dumps(alert_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topic_path,
                message_data,
                risk_level='high',
                event_type='high_risk_alert',
                priority='urgent',
                analysis_id=analysis_data.get('analysis_id', '')
            )
            
            message_id = future.result()
            
            logger.warning(f"Published high-risk alert for analysis {analysis_data.get('analysis_id')} with message ID: {message_id}")
            
            return {
                'success': True,
                'message': 'High-risk alert published successfully',
                'published': True,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to publish high-risk alert: {e}")
            return {
                'success': False,
                'message': f'Alert publish failed: {str(e)}',
                'published': False
            }
    
    async def publish_compliance_violation(self, analysis_data: Dict[str, Any], 
                                         violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish compliance violation event
        
        Args:
            analysis_data: Analysis result data
            violation: Specific violation details
            
        Returns:
            Publish result
        """
        if not self.pubsub_enabled or not self.publisher:
            return {
                'success': False,
                'message': 'Pub/Sub publishing not enabled',
                'published': False
            }
        
        try:
            # Prepare violation event data
            violation_data = {
                'event_type': 'compliance_violation',
                'analysis_id': analysis_data.get('analysis_id'),
                'timestamp': datetime.utcnow().isoformat(),
                'violation': {
                    'rule_id': violation.get('rule_id'),
                    'rule_name': violation.get('rule_name'),
                    'domain': violation.get('domain'),
                    'severity': violation.get('severity'),
                    'message': violation.get('message'),
                    'remediation': violation.get('remediation'),
                    'confidence': violation.get('confidence')
                },
                'document_type': analysis_data.get('document_summary', {}).get('document_type'),
                'compliance_score': analysis_data.get('compliance_score', 0.0),
                'metadata': {
                    'sector': analysis_data.get('sector', 'unknown'),
                    'state': analysis_data.get('state', 'unknown'),
                    'ai_confidence': analysis_data.get('ai_confidence', 0.0)
                }
            }
            
            # Publish violation event
            message_data = json.dumps(violation_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topic_path,
                message_data,
                event_type='compliance_violation',
                severity=violation.get('severity', 'medium'),
                domain=violation.get('domain', 'general'),
                analysis_id=analysis_data.get('analysis_id', '')
            )
            
            message_id = future.result()
            
            logger.info(f"Published compliance violation for analysis {analysis_data.get('analysis_id')} with message ID: {message_id}")
            
            return {
                'success': True,
                'message': 'Compliance violation published successfully',
                'published': True,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to publish compliance violation: {e}")
            return {
                'success': False,
                'message': f'Violation publish failed: {str(e)}',
                'published': False
            }
    
    async def publish_benchmark_update(self, benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish benchmark update event
        
        Args:
            benchmark_data: Updated benchmark data
            
        Returns:
            Publish result
        """
        if not self.pubsub_enabled or not self.publisher:
            return {
                'success': False,
                'message': 'Pub/Sub publishing not enabled',
                'published': False
            }
        
        try:
            # Prepare benchmark update event
            update_data = {
                'event_type': 'benchmark_update',
                'timestamp': datetime.utcnow().isoformat(),
                'benchmark_data': benchmark_data,
                'metadata': {
                    'update_type': 'scheduled',
                    'source': 'bigquery_aggregation'
                }
            }
            
            # Publish update event
            message_data = json.dumps(update_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topic_path,
                message_data,
                event_type='benchmark_update',
                priority='low',
                update_type='scheduled'
            )
            
            message_id = future.result()
            
            logger.info(f"Published benchmark update with message ID: {message_id}")
            
            return {
                'success': True,
                'message': 'Benchmark update published successfully',
                'published': True,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to publish benchmark update: {e}")
            return {
                'success': False,
                'message': f'Benchmark update publish failed: {str(e)}',
                'published': False
            }

# Global Pub/Sub publisher instance
pubsub_publisher = PubSubPublisher()
