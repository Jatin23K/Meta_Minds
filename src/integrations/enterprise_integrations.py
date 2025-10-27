# =========================================================
# enterprise_integrations.py: Enterprise Platform Integrations
# =========================================================
# Comprehensive integrations with major enterprise platforms
# Slack, Teams, Salesforce, Tableau, PowerBI, AWS, Azure, GCP

import asyncio
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import base64
import hmac
import hashlib
from urllib.parse import urlencode
import aiohttp
import boto3
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
from google.oauth2 import service_account
import pandas as pd
from io import StringIO, BytesIO

@dataclass
class IntegrationConfig:
    """Configuration for enterprise integrations."""
    platform: str
    credentials: Dict[str, str]
    endpoints: Dict[str, str]
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}

class SlackIntegration:
    """Slack integration for notifications and bot interactions."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.bot_token = config.credentials.get('bot_token')
        self.signing_secret = config.credentials.get('signing_secret')
        self.base_url = "https://slack.com/api"
        
        self.logger = logging.getLogger("SlackIntegration")
    
    async def send_notification(self, channel: str, message: str, 
                               attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send notification to Slack channel."""
        
        payload = {
            'channel': channel,
            'text': message,
            'as_user': True
        }
        
        if attachments:
            payload['attachments'] = attachments
        
        headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat.postMessage",
                json=payload,
                headers=headers
            ) as response:
                result = await response.json()
                
                if result.get('ok'):
                    self.logger.info(f"Message sent to Slack channel {channel}")
                    return result
                else:
                    self.logger.error(f"Failed to send Slack message: {result.get('error')}")
                    return result
    
    async def send_analysis_complete_notification(self, channel: str, 
                                                analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send analysis completion notification with rich formatting."""
        
        # Create rich attachment
        attachment = {
            "color": "good",
            "title": "📊 Meta Minds Analysis Complete",
            "fields": [
                {
                    "title": "Dataset",
                    "value": analysis_results.get('dataset_name', 'Unknown'),
                    "short": True
                },
                {
                    "title": "Questions Generated",
                    "value": str(len(analysis_results.get('questions', []))),
                    "short": True
                },
                {
                    "title": "Quality Score",
                    "value": f"{analysis_results.get('quality_score', 0):.2f}/1.0",
                    "short": True
                },
                {
                    "title": "Analysis Time",
                    "value": analysis_results.get('duration', 'N/A'),
                    "short": True
                }
            ],
            "footer": "Meta Minds Automation",
            "ts": int(datetime.now().timestamp())
        }
        
        # Add action buttons
        attachment["actions"] = [
            {
                "type": "button",
                "text": "View Results",
                "url": analysis_results.get('results_url', '#'),
                "style": "primary"
            },
            {
                "type": "button",
                "text": "Download Report",
                "url": analysis_results.get('report_url', '#')
            }
        ]
        
        message = "Your data analysis has been completed! 🎉"
        return await self.send_notification(channel, message, [attachment])
    
    async def send_human_intervention_request(self, channel: str, 
                                            intervention_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send human intervention request to Slack."""
        
        attachment = {
            "color": "warning",
            "title": "🚨 Human Intervention Required",
            "text": intervention_data.get('description', 'Decision needed'),
            "fields": [
                {
                    "title": "Priority",
                    "value": intervention_data.get('priority', 'Medium'),
                    "short": True
                },
                {
                    "title": "System",
                    "value": intervention_data.get('automation_system', 'Unknown'),
                    "short": True
                },
                {
                    "title": "Deadline",
                    "value": intervention_data.get('deadline', 'No deadline'),
                    "short": False
                }
            ],
            "footer": "Automation Ecosystem",
            "ts": int(datetime.now().timestamp())
        }
        
        # Add action buttons for available options
        if intervention_data.get('options'):
            attachment["actions"] = []
            for option in intervention_data['options']:
                attachment["actions"].append({
                    "type": "button",
                    "text": option['label'],
                    "value": option['id'],
                    "name": "intervention_action"
                })
        
        message = f"Intervention needed for: {intervention_data.get('title', 'Automation Task')}"
        return await self.send_notification(channel, message, [attachment])
    
    def verify_request(self, timestamp: str, signature: str, body: str) -> bool:
        """Verify Slack request signature."""
        
        if not self.signing_secret:
            return True  # Skip verification if no secret configured
        
        # Create signature
        sig_basestring = f"v0:{timestamp}:{body}"
        my_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(my_signature, signature)

class MicrosoftTeamsIntegration:
    """Microsoft Teams integration for notifications and bot interactions."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.webhook_url = config.credentials.get('webhook_url')
        self.app_id = config.credentials.get('app_id')
        self.app_password = config.credentials.get('app_password')
        
        self.logger = logging.getLogger("TeamsIntegration")
    
    async def send_notification(self, title: str, message: str, 
                               color: str = "0078D4") -> Dict[str, Any]:
        """Send notification to Teams channel via webhook."""
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color,
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": "Meta Minds Automation",
                "activityImage": "https://via.placeholder.com/64x64.png?text=MM",
                "text": message,
                "markdown": True
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    self.logger.info("Message sent to Teams")
                    return {"success": True}
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to send Teams message: {error_text}")
                    return {"success": False, "error": error_text}
    
    async def send_analysis_complete_notification(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send analysis completion notification to Teams."""
        
        title = "📊 Data Analysis Complete"
        message = f"""
**Dataset:** {analysis_results.get('dataset_name', 'Unknown')}  
**Questions Generated:** {len(analysis_results.get('questions', []))}  
**Quality Score:** {analysis_results.get('quality_score', 0):.2f}/1.0  
**Duration:** {analysis_results.get('duration', 'N/A')}

Your analysis is ready for review!
        """
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "28a745",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": "Meta Minds Automation",
                "text": message,
                "markdown": True
            }],
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "View Results",
                "targets": [{
                    "os": "default",
                    "uri": analysis_results.get('results_url', '#')
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload,
                headers=headers
            ) as response:
                return {"success": response.status == 200}

class SalesforceIntegration:
    """Salesforce integration for CRM data and workflow automation."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.instance_url = config.credentials.get('instance_url')
        self.client_id = config.credentials.get('client_id')
        self.client_secret = config.credentials.get('client_secret')
        self.username = config.credentials.get('username')
        self.password = config.credentials.get('password')
        self.security_token = config.credentials.get('security_token')
        
        self.access_token = None
        self.token_expires_at = None
        
        self.logger = logging.getLogger("SalesforceIntegration")
    
    async def authenticate(self) -> bool:
        """Authenticate with Salesforce using OAuth."""
        
        auth_url = f"{self.instance_url}/services/oauth2/token"
        
        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': f"{self.password}{self.security_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=payload) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data['access_token']
                    self.token_expires_at = datetime.now() + timedelta(hours=1)
                    
                    self.logger.info("Salesforce authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Salesforce authentication failed: {error_text}")
                    return False
    
    async def create_analysis_case(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a case in Salesforce for analysis results."""
        
        if not await self._ensure_authenticated():
            return {"success": False, "error": "Authentication failed"}
        
        case_data = {
            "Subject": f"Data Analysis: {analysis_results.get('dataset_name', 'Unknown Dataset')}",
            "Description": f"""
Data Analysis Results:
- Dataset: {analysis_results.get('dataset_name')}
- Questions Generated: {len(analysis_results.get('questions', []))}
- Quality Score: {analysis_results.get('quality_score', 0):.2f}
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Key Insights:
{chr(10).join(q.get('question', '') for q in analysis_results.get('questions', [])[:5])}
            """,
            "Priority": "Medium",
            "Status": "New",
            "Origin": "Meta Minds Automation"
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        create_url = f"{self.instance_url}/services/data/v54.0/sobjects/Case/"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                create_url,
                json=case_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    case_id = result['id']
                    
                    self.logger.info(f"Salesforce case created: {case_id}")
                    return {"success": True, "case_id": case_id}
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to create Salesforce case: {error_text}")
                    return {"success": False, "error": error_text}
    
    async def query_data(self, soql_query: str) -> Dict[str, Any]:
        """Execute SOQL query and return results."""
        
        if not await self._ensure_authenticated():
            return {"success": False, "error": "Authentication failed"}
        
        query_url = f"{self.instance_url}/services/data/v54.0/query/"
        params = {'q': soql_query}
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                query_url,
                params=params,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "data": result}
                else:
                    error_text = await response.text()
                    self.logger.error(f"Salesforce query failed: {error_text}")
                    return {"success": False, "error": error_text}
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure valid authentication token."""
        
        if not self.access_token or datetime.now() >= self.token_expires_at:
            return await self.authenticate()
        
        return True

class TableauIntegration:
    """Tableau integration for dashboard creation and data visualization."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.server_url = config.credentials.get('server_url')
        self.username = config.credentials.get('username')
        self.password = config.credentials.get('password')
        self.site_id = config.credentials.get('site_id', '')
        
        self.auth_token = None
        self.site_id_actual = None
        
        self.logger = logging.getLogger("TableauIntegration")
    
    async def authenticate(self) -> bool:
        """Authenticate with Tableau Server."""
        
        auth_payload = f"""
        <tsRequest>
            <credentials name='{self.username}' password='{self.password}'>
                <site contentUrl='{self.site_id}' />
            </credentials>
        </tsRequest>
        """
        
        auth_url = f"{self.server_url}/api/3.9/auth/signin"
        headers = {'Content-Type': 'application/xml'}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                auth_url,
                data=auth_payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    # Parse XML response for auth token
                    response_text = await response.text()
                    # Simplified parsing (in production, use proper XML parser)
                    if 'token="' in response_text:
                        start = response_text.find('token="') + 7
                        end = response_text.find('"', start)
                        self.auth_token = response_text[start:end]
                        
                        self.logger.info("Tableau authentication successful")
                        return True
                
                self.logger.error("Tableau authentication failed")
                return False
    
    async def publish_data_source(self, df: pd.DataFrame, 
                                data_source_name: str) -> Dict[str, Any]:
        """Publish dataset to Tableau as data source."""
        
        if not await self._ensure_authenticated():
            return {"success": False, "error": "Authentication failed"}
        
        # Convert DataFrame to Tableau-compatible format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Create data source XML
        datasource_xml = f"""
        <tsRequest>
            <datasource name='{data_source_name}'>
                <project id='default' />
            </datasource>
        </tsRequest>
        """
        
        # Prepare multipart form data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        
        form_data = f"""--{boundary}\r
Content-Disposition: form-data; name="request_payload"\r
Content-Type: application/xml\r
\r
{datasource_xml}\r
--{boundary}\r
Content-Disposition: form-data; name="tableau_datasource"; filename="{data_source_name}.csv"\r
Content-Type: text/csv\r
\r
{csv_data}\r
--{boundary}--\r
"""
        
        headers = {
            'X-Tableau-Auth': self.auth_token,
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        publish_url = f"{self.server_url}/api/3.9/sites/{self.site_id}/datasources"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                publish_url,
                data=form_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    self.logger.info(f"Data source published to Tableau: {data_source_name}")
                    return {"success": True, "data_source_name": data_source_name}
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to publish to Tableau: {error_text}")
                    return {"success": False, "error": error_text}
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure valid authentication."""
        
        if not self.auth_token:
            return await self.authenticate()
        
        return True

class AWSIntegration:
    """AWS integration for cloud storage and compute services."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.access_key = config.credentials.get('access_key_id')
        self.secret_key = config.credentials.get('secret_access_key')
        self.region = config.credentials.get('region', 'us-east-1')
        
        # Initialize AWS clients
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        
        self.logger = logging.getLogger("AWSIntegration")
    
    async def upload_analysis_results(self, analysis_results: Dict[str, Any],
                                    bucket_name: str, 
                                    object_key: str) -> Dict[str, Any]:
        """Upload analysis results to S3."""
        
        try:
            # Convert results to JSON
            results_json = json.dumps(analysis_results, indent=2, default=str)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=results_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'source': 'meta-minds',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Generate pre-signed URL for access
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=3600  # 1 hour
            )
            
            self.logger.info(f"Analysis results uploaded to S3: {object_key}")
            
            return {
                "success": True,
                "s3_url": f"s3://{bucket_name}/{object_key}",
                "presigned_url": presigned_url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to upload to S3: {e}")
            return {"success": False, "error": str(e)}
    
    async def store_dataset(self, df: pd.DataFrame, bucket_name: str,
                          object_key: str) -> Dict[str, Any]:
        """Store dataset in S3."""
        
        try:
            # Convert DataFrame to Parquet for efficient storage
            parquet_buffer = BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            parquet_data = parquet_buffer.getvalue()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=parquet_data,
                ContentType='application/octet-stream',
                Metadata={
                    'format': 'parquet',
                    'rows': str(len(df)),
                    'columns': str(len(df.columns)),
                    'uploaded_by': 'meta-minds'
                }
            )
            
            self.logger.info(f"Dataset stored in S3: {object_key}")
            
            return {
                "success": True,
                "s3_url": f"s3://{bucket_name}/{object_key}",
                "size_bytes": len(parquet_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store dataset in S3: {e}")
            return {"success": False, "error": str(e)}

class EnterpriseIntegrationManager:
    """Central manager for all enterprise integrations."""
    
    def __init__(self):
        self.integrations: Dict[str, Any] = {}
        self.logger = logging.getLogger("EnterpriseIntegrationManager")
    
    def register_integration(self, name: str, integration: Any):
        """Register an enterprise integration."""
        self.integrations[name] = integration
        self.logger.info(f"Registered integration: {name}")
    
    async def notify_analysis_complete(self, analysis_results: Dict[str, Any],
                                     channels: List[str] = None) -> Dict[str, Any]:
        """Notify all configured channels about analysis completion."""
        
        if channels is None:
            channels = ['slack', 'teams', 'salesforce']
        
        results = {}
        
        for channel in channels:
            if channel == 'slack' and 'slack' in self.integrations:
                slack_config = self.integrations['slack'].config.settings
                slack_channel = slack_config.get('default_channel', '#general')
                
                result = await self.integrations['slack'].send_analysis_complete_notification(
                    slack_channel, analysis_results
                )
                results['slack'] = result
            
            elif channel == 'teams' and 'teams' in self.integrations:
                result = await self.integrations['teams'].send_analysis_complete_notification(
                    analysis_results
                )
                results['teams'] = result
            
            elif channel == 'salesforce' and 'salesforce' in self.integrations:
                result = await self.integrations['salesforce'].create_analysis_case(
                    analysis_results
                )
                results['salesforce'] = result
        
        return results
    
    async def store_analysis_results(self, analysis_results: Dict[str, Any],
                                   storage_configs: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Store analysis results in configured storage systems."""
        
        if storage_configs is None:
            storage_configs = [
                {'platform': 'aws', 'bucket': 'meta-minds-results', 'prefix': 'analysis/'},
                {'platform': 'tableau', 'publish_as_datasource': True}
            ]
        
        results = {}
        
        for config in storage_configs:
            platform = config['platform']
            
            if platform == 'aws' and 'aws' in self.integrations:
                bucket = config['bucket']
                object_key = f"{config.get('prefix', '')}analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                result = await self.integrations['aws'].upload_analysis_results(
                    analysis_results, bucket, object_key
                )
                results['aws'] = result
            
            elif platform == 'tableau' and 'tableau' in self.integrations:
                if config.get('publish_as_datasource') and 'questions' in analysis_results:
                    # Convert questions to DataFrame
                    questions_df = pd.DataFrame(analysis_results['questions'])
                    datasource_name = f"MetaMinds_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    result = await self.integrations['tableau'].publish_data_source(
                        questions_df, datasource_name
                    )
                    results['tableau'] = result
        
        return results
    
    async def request_human_intervention(self, intervention_data: Dict[str, Any],
                                       notification_channels: List[str] = None) -> Dict[str, Any]:
        """Request human intervention across multiple channels."""
        
        if notification_channels is None:
            notification_channels = ['slack', 'teams']
        
        results = {}
        
        for channel in notification_channels:
            if channel == 'slack' and 'slack' in self.integrations:
                slack_config = self.integrations['slack'].config.settings
                slack_channel = slack_config.get('intervention_channel', '#alerts')
                
                result = await self.integrations['slack'].send_human_intervention_request(
                    slack_channel, intervention_data
                )
                results['slack'] = result
            
            elif channel == 'teams' and 'teams' in self.integrations:
                title = "🚨 Human Intervention Required"
                message = f"""
**Priority:** {intervention_data.get('priority', 'Medium')}  
**System:** {intervention_data.get('automation_system', 'Unknown')}  
**Description:** {intervention_data.get('description', 'Decision needed')}

Please review and take action.
                """
                
                result = await self.integrations['teams'].send_notification(
                    title, message, "ffc107"  # Warning color
                )
                results['teams'] = result
        
        return results
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all configured integrations."""
        
        status = {}
        
        for name, integration in self.integrations.items():
            try:
                # Basic health check
                status[name] = {
                    'configured': True,
                    'type': type(integration).__name__,
                    'last_check': datetime.now().isoformat()
                }
                
                # Platform-specific status checks
                if hasattr(integration, 'access_token'):
                    status[name]['authenticated'] = integration.access_token is not None
                elif hasattr(integration, 'bot_token'):
                    status[name]['authenticated'] = integration.bot_token is not None
                
            except Exception as e:
                status[name] = {
                    'configured': False,
                    'error': str(e)
                }
        
        return status

# Global integration manager
integration_manager = EnterpriseIntegrationManager()

def setup_enterprise_integrations(configs: List[IntegrationConfig]):
    """Setup enterprise integrations from configuration."""
    
    for config in configs:
        platform = config.platform.lower()
        
        if platform == 'slack':
            integration = SlackIntegration(config)
            integration_manager.register_integration('slack', integration)
        
        elif platform == 'teams':
            integration = MicrosoftTeamsIntegration(config)
            integration_manager.register_integration('teams', integration)
        
        elif platform == 'salesforce':
            integration = SalesforceIntegration(config)
            integration_manager.register_integration('salesforce', integration)
        
        elif platform == 'tableau':
            integration = TableauIntegration(config)
            integration_manager.register_integration('tableau', integration)
        
        elif platform == 'aws':
            integration = AWSIntegration(config)
            integration_manager.register_integration('aws', integration)

# Example configuration
EXAMPLE_CONFIGS = [
    IntegrationConfig(
        platform="slack",
        credentials={
            "bot_token": "xoxb-your-bot-token",
            "signing_secret": "your-signing-secret"
        },
        endpoints={},
        settings={
            "default_channel": "#data-analysis",
            "intervention_channel": "#alerts"
        }
    ),
    IntegrationConfig(
        platform="teams",
        credentials={
            "webhook_url": "https://outlook.office.com/webhook/your-webhook-url"
        },
        endpoints={},
        settings={}
    ),
    IntegrationConfig(
        platform="aws",
        credentials={
            "access_key_id": "your-access-key",
            "secret_access_key": "your-secret-key",
            "region": "us-east-1"
        },
        endpoints={},
        settings={}
    )
]
