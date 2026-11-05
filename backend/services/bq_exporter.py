"""
BigQuery Exporter for LegiLight Analytics
Streams anonymized compliance data to BigQuery for analytics and benchmarking
Supports Indian MSME compliance trends and sector analysis
"""

import os
import logging
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
import hashlib

# BigQuery
try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False
    bigquery = None

logger = logging.getLogger(__name__)

class BigQueryExporter:
    """BigQuery exporter for compliance analytics"""
    
    def __init__(self):
        self.bq_client = None
        self.bq_enabled = os.environ.get('BQ_ENABLED', 'false').lower() == 'true'
        self.project_id = os.environ.get('BQ_PROJECT_ID') or os.environ.get('GCP_PROJECT_ID')
        self.dataset_id = os.environ.get('BQ_DATASET', 'legilight')
        self.table_id = os.environ.get('BQ_TABLE', 'document_events')
        self.batch_size = int(os.environ.get('BQ_BATCH_SIZE', '100'))
        
        # Table schema
        self.table_schema = self._get_table_schema()
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize BigQuery client"""
        if not self.bq_enabled or not BQ_AVAILABLE:
            logger.info("BigQuery export not enabled or not available")
            return
        
        try:
            self.bq_client = bigquery.Client(project=self.project_id)
            logger.info("✓ BigQuery client initialized")
            
            # Ensure dataset and table exist
            asyncio.create_task(self._ensure_dataset_and_table())
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize BigQuery client: {e}")
            self.bq_client = None
    
    def _get_table_schema(self) -> List[Dict[str, Any]]:
        """Define BigQuery table schema"""
        return [
            bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("document_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("domains", "STRING", mode="REPEATED"),
            bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("compliance_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("ai_confidence", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("flags_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("red_flags_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("yellow_flags_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("green_flags_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("missing_clauses", "STRING", mode="REPEATED"),
            bigquery.SchemaField("languages", "STRING", mode="REPEATED"),
            bigquery.SchemaField("ocr_used", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("translation_used", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("processing_time_ms", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("model_versions", "RECORD", mode="NULLABLE", fields=[
                bigquery.SchemaField("gemini", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("inlegalbert", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("ocr", "STRING", mode="NULLABLE")
            ]),
            bigquery.SchemaField("document_hash", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("anonymized_metadata", "RECORD", mode="NULLABLE", fields=[
                bigquery.SchemaField("text_length", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("word_count", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("sentence_count", "INTEGER", mode="NULLABLE")
            ])
        ]
    
    async def _ensure_dataset_and_table(self):
        """Ensure BigQuery dataset and table exist"""
        if not self.bq_client:
            return
        
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.bq_client.dataset(self.dataset_id)
            try:
                self.bq_client.get_dataset(dataset_ref)
                logger.info(f"Dataset {self.dataset_id} already exists")
            except NotFound:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "asia-south1"  # Mumbai region
                dataset.description = "LegiLight compliance analytics data"
                self.bq_client.create_dataset(dataset)
                logger.info(f"Created dataset {self.dataset_id}")
            
            # Create table if it doesn't exist
            table_ref = dataset_ref.table(self.table_id)
            try:
                self.bq_client.get_table(table_ref)
                logger.info(f"Table {self.table_id} already exists")
            except NotFound:
                table = bigquery.Table(table_ref, schema=self.table_schema)
                table.description = "Document analysis events and compliance data"
                self.bq_client.create_table(table)
                logger.info(f"Created table {self.table_id}")
                
        except Exception as e:
            logger.error(f"Failed to ensure dataset/table: {e}")
    
    async def export_analysis_event(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export a single analysis event to BigQuery
        
        Args:
            analysis_data: Analysis result data to export
            
        Returns:
            Export result with success status
        """
        if not self.bq_enabled or not self.bq_client:
            return {
                'success': False,
                'message': 'BigQuery export not enabled',
                'exported': False
            }
        
        try:
            # Prepare row data
            row_data = self._prepare_row_data(analysis_data)
            
            # Insert row
            table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
            table = self.bq_client.get_table(table_ref)
            
            errors = self.bq_client.insert_rows_json(table, [row_data])
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                return {
                    'success': False,
                    'message': f'BigQuery insert failed: {errors}',
                    'exported': False
                }
            else:
                logger.info(f"Successfully exported analysis {analysis_data.get('analysis_id')}")
                return {
                    'success': True,
                    'message': 'Analysis exported successfully',
                    'exported': True
                }
                
        except Exception as e:
            logger.error(f"Failed to export analysis event: {e}")
            return {
                'success': False,
                'message': f'Export failed: {str(e)}',
                'exported': False
            }
    
    def _prepare_row_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare analysis data for BigQuery insertion"""
        # Extract basic information
        analysis_id = analysis_data.get('analysis_id', '')
        timestamp = datetime.utcnow()
        
        # Document type and metadata
        document_summary = analysis_data.get('document_summary', {})
        document_type = document_summary.get('document_type', 'unknown')
        
        # Risk assessment
        risk_assessment = analysis_data.get('risk_assessment', {})
        risk_level = risk_assessment.get('overall_risk_level', 'unknown')
        red_flags = risk_assessment.get('red_flags', [])
        yellow_flags = risk_assessment.get('yellow_flags', [])
        green_flags = risk_assessment.get('green_flags', [])
        
        # Compliance data
        compliance_score = analysis_data.get('compliance_score', 0.0)
        ai_confidence = analysis_data.get('ai_confidence', 0.0)
        
        # CUAD analysis
        cuad_analysis = analysis_data.get('cuad_analysis', {})
        domains = cuad_analysis.get('categories_analyzed', [])
        
        # Enhanced insights
        enhanced_insights = analysis_data.get('enhanced_insights', {})
        missing_clauses = enhanced_insights.get('missing_clauses', [])
        
        # Processing metadata
        processing_time = analysis_data.get('processing_time', 0.0)
        languages = analysis_data.get('languages_detected', [])
        ocr_used = analysis_data.get('ocr_used', False)
        translation_used = analysis_data.get('translation_used', False)
        
        # Model versions
        model_versions = {
            'gemini': analysis_data.get('model_versions', {}).get('gemini', 'unknown'),
            'inlegalbert': analysis_data.get('model_versions', {}).get('inlegalbert', 'unknown'),
            'ocr': analysis_data.get('model_versions', {}).get('ocr', 'unknown')
        }
        
        # Document hash for deduplication
        document_text = analysis_data.get('document_text', '')
        document_hash = hashlib.sha256(document_text.encode()).hexdigest()[:16] if document_text else None
        
        # Anonymized metadata
        text_length = len(document_text) if document_text else 0
        word_count = len(document_text.split()) if document_text else 0
        sentence_count = len([s for s in document_text.split('.') if s.strip()]) if document_text else 0
        
        anonymized_metadata = {
            'text_length': text_length,
            'word_count': word_count,
            'sentence_count': sentence_count
        }
        
        return {
            'analysis_id': analysis_id,
            'timestamp': timestamp.isoformat(),
            'document_type': document_type,
            'sector': analysis_data.get('sector', 'unknown'),
            'state': analysis_data.get('state', 'unknown'),
            'domains': domains,
            'risk_level': risk_level,
            'compliance_score': compliance_score,
            'ai_confidence': ai_confidence,
            'flags_count': len(red_flags) + len(yellow_flags) + len(green_flags),
            'red_flags_count': len(red_flags),
            'yellow_flags_count': len(yellow_flags),
            'green_flags_count': len(green_flags),
            'missing_clauses': missing_clauses,
            'languages': languages,
            'ocr_used': ocr_used,
            'translation_used': translation_used,
            'processing_time_ms': int(processing_time * 1000),
            'model_versions': model_versions,
            'document_hash': document_hash,
            'anonymized_metadata': anonymized_metadata
        }
    
    async def get_benchmarks(self, sector: str = None, state: str = None, 
                           days: int = 30) -> Dict[str, Any]:
        """
        Get compliance benchmarks from BigQuery
        
        Args:
            sector: Filter by sector
            state: Filter by state
            days: Number of days to look back
            
        Returns:
            Benchmark data
        """
        if not self.bq_enabled or not self.bq_client:
            return self._get_static_benchmarks()
        
        try:
            # Build query
            query = f"""
            SELECT 
                document_type,
                risk_level,
                AVG(compliance_score) as avg_compliance_score,
                AVG(ai_confidence) as avg_confidence,
                AVG(flags_count) as avg_flags_count,
                AVG(red_flags_count) as avg_red_flags,
                AVG(yellow_flags_count) as avg_yellow_flags,
                AVG(green_flags_count) as avg_green_flags,
                COUNT(*) as document_count
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            """
            
            if sector:
                query += f" AND sector = '{sector}'"
            if state:
                query += f" AND state = '{state}'"
            
            query += """
            GROUP BY document_type, risk_level
            ORDER BY document_count DESC
            """
            
            # Execute query
            query_job = self.bq_client.query(query)
            results = query_job.result()
            
            # Process results
            benchmarks = {
                'sector': sector,
                'state': state,
                'days': days,
                'data': [],
                'summary': {
                    'total_documents': 0,
                    'avg_compliance_score': 0.0,
                    'risk_distribution': {}
                }
            }
            
            total_docs = 0
            total_score = 0.0
            risk_counts = {}
            
            for row in results:
                doc_data = {
                    'document_type': row.document_type,
                    'risk_level': row.risk_level,
                    'avg_compliance_score': float(row.avg_compliance_score or 0),
                    'avg_confidence': float(row.avg_confidence or 0),
                    'avg_flags_count': float(row.avg_flags_count or 0),
                    'avg_red_flags': float(row.avg_red_flags or 0),
                    'avg_yellow_flags': float(row.avg_yellow_flags or 0),
                    'avg_green_flags': float(row.avg_green_flags or 0),
                    'document_count': int(row.document_count)
                }
                benchmarks['data'].append(doc_data)
                
                total_docs += int(row.document_count)
                total_score += float(row.avg_compliance_score or 0) * int(row.document_count)
                risk_counts[row.risk_level] = risk_counts.get(row.risk_level, 0) + int(row.document_count)
            
            # Calculate summary
            if total_docs > 0:
                benchmarks['summary']['total_documents'] = total_docs
                benchmarks['summary']['avg_compliance_score'] = total_score / total_docs
                benchmarks['summary']['risk_distribution'] = {
                    risk: count / total_docs for risk, count in risk_counts.items()
                }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Failed to get benchmarks from BigQuery: {e}")
            return self._get_static_benchmarks()
    
    def _get_static_benchmarks(self) -> Dict[str, Any]:
        """Get static benchmark data when BigQuery is not available"""
        return {
            'sector': 'general',
            'state': 'all',
            'days': 30,
            'data': [
                {
                    'document_type': 'gst_form',
                    'risk_level': 'medium',
                    'avg_compliance_score': 0.72,
                    'avg_confidence': 0.85,
                    'avg_flags_count': 3.2,
                    'avg_red_flags': 1.1,
                    'avg_yellow_flags': 1.8,
                    'avg_green_flags': 0.3,
                    'document_count': 150
                },
                {
                    'document_type': 'labor_document',
                    'risk_level': 'high',
                    'avg_compliance_score': 0.68,
                    'avg_confidence': 0.82,
                    'avg_flags_count': 4.1,
                    'avg_red_flags': 2.3,
                    'avg_yellow_flags': 1.5,
                    'avg_green_flags': 0.3,
                    'document_count': 89
                },
                {
                    'document_type': 'commercial_contract',
                    'risk_level': 'low',
                    'avg_compliance_score': 0.84,
                    'avg_confidence': 0.91,
                    'avg_flags_count': 2.1,
                    'avg_red_flags': 0.4,
                    'avg_yellow_flags': 1.2,
                    'avg_green_flags': 0.5,
                    'document_count': 203
                }
            ],
            'summary': {
                'total_documents': 442,
                'avg_compliance_score': 0.75,
                'risk_distribution': {
                    'low': 0.46,
                    'medium': 0.34,
                    'high': 0.20
                }
            },
            'source': 'static_fallback'
        }
    
    async def get_trends(self, metric: str = 'compliance_score', 
                        days: int = 30, group_by: str = 'day') -> Dict[str, Any]:
        """
        Get trend data for a specific metric
        
        Args:
            metric: Metric to analyze (compliance_score, ai_confidence, etc.)
            days: Number of days to look back
            group_by: Grouping (day, week, month)
            
        Returns:
            Trend data
        """
        if not self.bq_enabled or not self.bq_client:
            return self._get_static_trends(metric, days)
        
        try:
            # Build query based on group_by
            if group_by == 'day':
                date_format = '%Y-%m-%d'
                interval = 'DAY'
            elif group_by == 'week':
                date_format = '%Y-%U'
                interval = 'WEEK'
            elif group_by == 'month':
                date_format = '%Y-%m'
                interval = 'MONTH'
            else:
                date_format = '%Y-%m-%d'
                interval = 'DAY'
            
            query = f"""
            SELECT 
                FORMAT_TIMESTAMP('{date_format}', timestamp) as period,
                AVG({metric}) as avg_value,
                COUNT(*) as document_count
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY period
            ORDER BY period
            """
            
            # Execute query
            query_job = self.bq_client.query(query)
            results = query_job.result()
            
            # Process results
            trends = {
                'metric': metric,
                'days': days,
                'group_by': group_by,
                'data': [],
                'trend_direction': 'stable'
            }
            
            values = []
            for row in results:
                trend_point = {
                    'period': row.period,
                    'value': float(row.avg_value or 0),
                    'document_count': int(row.document_count)
                }
                trends['data'].append(trend_point)
                values.append(float(row.avg_value or 0))
            
            # Calculate trend direction
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg * 1.05:
                    trends['trend_direction'] = 'improving'
                elif second_avg < first_avg * 0.95:
                    trends['trend_direction'] = 'declining'
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get trends from BigQuery: {e}")
            return self._get_static_trends(metric, days)
    
    def _get_static_trends(self, metric: str, days: int) -> Dict[str, Any]:
        """Get static trend data when BigQuery is not available"""
        import random
        
        # Generate mock trend data
        base_value = 0.75 if metric == 'compliance_score' else 0.85
        data = []
        
        for i in range(min(days, 30)):
            value = base_value + random.uniform(-0.1, 0.1)
            data.append({
                'period': f'2024-{(i//30)+1:02d}-{(i%30)+1:02d}',
                'value': round(value, 3),
                'document_count': random.randint(5, 25)
            })
        
        return {
            'metric': metric,
            'days': days,
            'group_by': 'day',
            'data': data,
            'trend_direction': 'stable',
            'source': 'static_fallback'
        }

# Global BigQuery exporter instance
bq_exporter = BigQueryExporter()
