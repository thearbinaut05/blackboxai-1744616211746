import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalAssessmentAgent:
    def __init__(self):
        self.compliance_cache = {}
        self.tos_cache = {}
        self.session = None
        self.api_keys = {
            'lexis_nexis': None,  # Would be set in production
            'legal_api': None     # Would be set in production
        }
        
    async def initialize(self):
        """Initialize the agent with necessary connections."""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            
    async def assess_method(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Main method for legal assessment of a discovered method."""
        try:
            assessment = {
                'timestamp': datetime.now().isoformat(),
                'method_id': method.get('id', 'unknown'),
                'platform_compliance': await self.check_platform_compliance(method),
                'regulatory_compliance': await self.check_regulatory_compliance(method),
                'legal_risks': await self.identify_legal_risks(method),
                'required_documents': await self.generate_required_documents(method),
                'overall_status': 'pending'
            }
            
            # Calculate overall compliance score
            compliance_score = (
                assessment['platform_compliance']['score'] * 0.4 +
                assessment['regulatory_compliance']['score'] * 0.4 +
                (1 - assessment['legal_risks']['risk_score']) * 0.2
            )
            
            assessment['compliance_score'] = compliance_score
            assessment['overall_status'] = 'approved' if compliance_score >= 0.7 else 'rejected'
            
            return assessment
            
        except Exception as e:
            logger.error(f"Legal assessment error: {str(e)}")
            return {'overall_status': 'error', 'error': str(e)}
            
    async def check_platform_compliance(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with platform-specific terms of service."""
        try:
            platform = method.get('platform', '').lower()
            
            # Get platform ToS
            tos = await self._get_platform_tos(platform)
            
            # Check method against ToS
            violations = []
            compliance_score = 1.0
            
            # Common ToS violations to check
            checks = {
                'automation_allowed': self._check_automation_compliance(method, tos),
                'data_usage_allowed': self._check_data_usage_compliance(method, tos),
                'api_limits_respected': self._check_api_limits_compliance(method, tos),
                'content_guidelines_met': self._check_content_guidelines_compliance(method, tos)
            }
            
            for check_name, (passed, details) in checks.items():
                if not passed:
                    violations.append({
                        'type': check_name,
                        'details': details
                    })
                    compliance_score -= 0.25  # Each violation reduces score by 25%
            
            return {
                'score': max(0, compliance_score),
                'violations': violations,
                'tos_version': tos.get('version', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Platform compliance check error: {str(e)}")
            return {'score': 0, 'violations': [{'type': 'error', 'details': str(e)}]}
            
    async def check_regulatory_compliance(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with relevant regulations."""
        try:
            regulations = await self._identify_applicable_regulations(method)
            compliance_checks = []
            compliance_score = 1.0
            
            for regulation in regulations:
                check_result = await self._check_regulation_compliance(method, regulation)
                compliance_checks.append(check_result)
                
                if not check_result['compliant']:
                    compliance_score -= (1.0 / len(regulations))
            
            return {
                'score': max(0, compliance_score),
                'checks': compliance_checks,
                'applicable_regulations': [reg['name'] for reg in regulations],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Regulatory compliance check error: {str(e)}")
            return {'score': 0, 'checks': [], 'error': str(e)}
            
    async def identify_legal_risks(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Identifies potential legal risks associated with the method."""
        try:
            risks = []
            risk_score = 0.0
            
            # Check various risk categories
            risk_categories = {
                'intellectual_property': self._check_ip_risks(method),
                'data_privacy': self._check_privacy_risks(method),
                'financial_regulations': self._check_financial_risks(method),
                'consumer_protection': self._check_consumer_risks(method)
            }
            
            for category, (risk_level, details) in risk_categories.items():
                risks.append({
                    'category': category,
                    'risk_level': risk_level,
                    'details': details
                })
                risk_score += risk_level
            
            risk_score = risk_score / len(risk_categories)  # Normalize to 0-1
            
            return {
                'risk_score': risk_score,
                'risks': risks,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Legal risk identification error: {str(e)}")
            return {'risk_score': 1.0, 'risks': [], 'error': str(e)}
            
    async def generate_required_documents(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates necessary legal documents for the method."""
        try:
            documents = {
                'terms_of_service': await self._generate_tos(method),
                'privacy_policy': await self._generate_privacy_policy(method),
                'disclaimer': await self._generate_disclaimer(method)
            }
            
            if self._requires_additional_documents(method):
                documents.update({
                    'data_processing_agreement': await self._generate_dpa(method),
                    'api_terms': await self._generate_api_terms(method)
                })
            
            return {
                'documents': documents,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document generation error: {str(e)}")
            return {'documents': {}, 'error': str(e)}
            
    async def _get_platform_tos(self, platform: str) -> Dict[str, Any]:
        """Retrieves and caches platform terms of service."""
        if platform in self.tos_cache:
            return self.tos_cache[platform]
            
        try:
            # Platform-specific ToS endpoints
            tos_endpoints = {
                'amazon': 'https://www.amazon.com/gp/help/customer/display.html?nodeId=508088',
                'shopify': 'https://www.shopify.com/legal/terms',
                'youtube': 'https://www.youtube.com/static?template=terms',
                'medium': 'https://medium.com/policy/medium-terms-of-service-9db0094a1e0f'
            }
            
            if platform in tos_endpoints:
                async with self.session.get(tos_endpoints[platform]) as response:
                    if response.status == 200:
                        tos_text = await response.text()
                        tos_data = self._parse_tos(tos_text)
                        self.tos_cache[platform] = tos_data
                        return tos_data
            
            return {'version': 'unknown', 'content': ''}
            
        except Exception as e:
            logger.error(f"ToS retrieval error for {platform}: {str(e)}")
            return {'version': 'error', 'content': ''}
            
    def _parse_tos(self, tos_text: str) -> Dict[str, Any]:
        """Parses terms of service text into structured data."""
        try:
            # Extract version
            version_match = re.search(r'Version[:\s]+([0-9.]+)', tos_text)
            version = version_match.group(1) if version_match else 'unknown'
            
            # Extract key sections
            sections = {
                'automation': self._extract_section(tos_text, 'automation', 'bot', 'script'),
                'data_usage': self._extract_section(tos_text, 'data', 'information', 'privacy'),
                'api_usage': self._extract_section(tos_text, 'api', 'interface', 'endpoint'),
                'content': self._extract_section(tos_text, 'content', 'material', 'submission')
            }
            
            return {
                'version': version,
                'sections': sections,
                'raw_content': tos_text
            }
            
        except Exception as e:
            logger.error(f"ToS parsing error: {str(e)}")
            return {'version': 'error', 'sections': {}}
            
    def _extract_section(self, text: str, *keywords: str) -> str:
        """Extracts relevant section from text based on keywords."""
        try:
            for keyword in keywords:
                pattern = rf'(?i)({keyword}[^.]*(?:[.][^.]*){0,3})'
                matches = re.findall(pattern, text)
                if matches:
                    return ' '.join(matches)
            return ''
        except Exception as e:
            logger.error(f"Section extraction error: {str(e)}")
            return ''
            
    def _check_automation_compliance(self, method: Dict[str, Any], tos: Dict[str, Any]) -> tuple:
        """Checks if method's automation complies with ToS."""
        try:
            automation_rules = tos.get('sections', {}).get('automation', '')
            
            # Check for explicit automation prohibitions
            if any(term in automation_rules.lower() for term in ['prohibited', 'forbidden', 'not allowed']):
                return False, "Automation explicitly prohibited"
                
            # Check for conditional automation permissions
            if 'api' in automation_rules.lower() and 'api' not in method.get('implementation', '').lower():
                return False, "Automation requires API usage"
                
            return True, "Automation compliant"
            
        except Exception as e:
            logger.error(f"Automation compliance check error: {str(e)}")
            return False, f"Error checking automation compliance: {str(e)}"
            
    def _check_data_usage_compliance(self, method: Dict[str, Any], tos: Dict[str, Any]) -> tuple:
        """Checks if method's data usage complies with ToS."""
        try:
            data_rules = tos.get('sections', {}).get('data_usage', '')
            method_data_usage = method.get('data_usage', {})
            
            # Check for data collection compliance
            if method_data_usage.get('collects_personal_data', False) and 'personal' in data_rules.lower():
                return False, "Personal data collection restricted"
                
            # Check for data storage compliance
            if method_data_usage.get('stores_data', False) and 'storage' in data_rules.lower():
                return False, "Data storage restricted"
                
            return True, "Data usage compliant"
            
        except Exception as e:
            logger.error(f"Data usage compliance check error: {str(e)}")
            return False, f"Error checking data usage compliance: {str(e)}"
            
    def _check_api_limits_compliance(self, method: Dict[str, Any], tos: Dict[str, Any]) -> tuple:
        """Checks if method complies with API limits."""
        try:
            api_rules = tos.get('sections', {}).get('api_usage', '')
            method_api_usage = method.get('api_usage', {})
            
            # Check rate limits
            if 'rate limit' in api_rules.lower():
                rate_limit = self._extract_rate_limit(api_rules)
                if method_api_usage.get('requests_per_minute', 0) > rate_limit:
                    return False, f"Exceeds rate limit of {rate_limit} requests per minute"
                    
            return True, "API usage compliant"
            
        except Exception as e:
            logger.error(f"API limits compliance check error: {str(e)}")
            return False, f"Error checking API limits compliance: {str(e)}"
            
    def _check_content_guidelines_compliance(self, method: Dict[str, Any], tos: Dict[str, Any]) -> tuple:
        """Checks if method's content complies with guidelines."""
        try:
            content_rules = tos.get('sections', {}).get('content', '')
            method_content = method.get('content', {})
            
            # Check content restrictions
            restricted_content = ['adult', 'violence', 'hate speech', 'spam']
            for restriction in restricted_content:
                if restriction in content_rules.lower() and method_content.get(restriction, False):
                    return False, f"Contains restricted content: {restriction}"
                    
            return True, "Content compliant"
            
        except Exception as e:
            logger.error(f"Content guidelines compliance check error: {str(e)}")
            return False, f"Error checking content guidelines compliance: {str(e)}"
            
    async def _identify_applicable_regulations(self, method: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifies regulations applicable to the method."""
        try:
            regulations = []
            
            # Check for data privacy regulations
            if self._handles_personal_data(method):
                regulations.extend([
                    {'name': 'GDPR', 'jurisdiction': 'EU', 'type': 'privacy'},
                    {'name': 'CCPA', 'jurisdiction': 'California', 'type': 'privacy'}
                ])
                
            # Check for financial regulations
            if self._handles_financial_data(method):
                regulations.extend([
                    {'name': 'PSD2', 'jurisdiction': 'EU', 'type': 'financial'},
                    {'name': 'PCI-DSS', 'jurisdiction': 'Global', 'type': 'financial'}
                ])
                
            # Check for e-commerce regulations
            if self._is_ecommerce(method):
                regulations.extend([
                    {'name': 'Consumer Rights Directive', 'jurisdiction': 'EU', 'type': 'consumer'},
                    {'name': 'FTC E-commerce Rules', 'jurisdiction': 'US', 'type': 'consumer'}
                ])
                
            return regulations
            
        except Exception as e:
            logger.error(f"Regulation identification error: {str(e)}")
            return []
            
    def _handles_personal_data(self, method: Dict[str, Any]) -> bool:
        """Checks if method handles personal data."""
        data_indicators = ['user', 'personal', 'profile', 'email', 'address']
        method_str = json.dumps(method).lower()
        return any(indicator in method_str for indicator in data_indicators)
        
    def _handles_financial_data(self, method: Dict[str, Any]) -> bool:
        """Checks if method handles financial data."""
        financial_indicators = ['payment', 'credit', 'bank', 'transaction']
        method_str = json.dumps(method).lower()
        return any(indicator in method_str for indicator in financial_indicators)
        
    def _is_ecommerce(self, method: Dict[str, Any]) -> bool:
        """Checks if method involves e-commerce."""
        ecommerce_indicators = ['shop', 'store', 'product', 'sell']
        method_str = json.dumps(method).lower()
        return any(indicator in method_str for indicator in ecommerce_indicators)
        
    async def _check_regulation_compliance(self, method: Dict[str, Any], regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with a specific regulation."""
        try:
            compliance_result = {
                'regulation': regulation['name'],
                'compliant': True,
                'details': []
            }
            
            if regulation['type'] == 'privacy':
                compliance_result.update(await self._check_privacy_compliance(method, regulation))
            elif regulation['type'] == 'financial':
                compliance_result.update(await self._check_financial_compliance(method, regulation))
            elif regulation['type'] == 'consumer':
                compliance_result.update(await self._check_consumer_compliance(method, regulation))
                
            return compliance_result
            
        except Exception as e:
            logger.error(f"Regulation compliance check error: {str(e)}")
            return {'regulation': regulation['name'], 'compliant': False, 'error': str(e)}
            
    async def _check_privacy_compliance(self, method: Dict[str, Any], regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with privacy regulations."""
        try:
            compliant = True
            details = []
            
            # Check data collection practices
            if method.get('data_usage', {}).get('collects_personal_data', False):
                details.append("Requires privacy policy")
                details.append("Requires user consent mechanisms")
                
            # Check data storage practices
            if method.get('data_usage', {}).get('stores_data', False):
                details.append("Requires data retention policy")
                details.append("Requires data encryption")
                
            return {
                'compliant': compliant,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Privacy compliance check error: {str(e)}")
            return {'compliant': False, 'error': str(e)}
            
    async def _check_financial_compliance(self, method: Dict[str, Any], regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with financial regulations."""
        try:
            compliant = True
            details = []
            
            # Check payment processing
            if self._handles_financial_data(method):
                details.append("Requires PCI DSS compliance")
                details.append("Requires financial data handling procedures")
                
            return {
                'compliant': compliant,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Financial compliance check error: {str(e)}")
            return {'compliant': False, 'error': str(e)}
            
    async def _check_consumer_compliance(self, method: Dict[str, Any], regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Checks compliance with consumer protection regulations."""
        try:
            compliant = True
            details = []
            
            # Check e-commerce practices
            if self._is_ecommerce(method):
                details.append("Requires return policy")
                details.append("Requires shipping terms")
                
            return {
                'compliant': compliant,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Consumer compliance check error: {str(e)}")
            return {'compliant': False, 'error': str(e)}
            
    async def _get_tos_template(self) -> Dict[str, Any]:
        """Returns a basic terms of service template."""
        return {
            'version': '1.0',
            'sections': [
                {
                    'title': 'Service Description',
                    'content': 'This section describes the services provided.'
                },
                {
                    'title': 'User Obligations',
                    'content': 'This section outlines user responsibilities.'
                },
                {
                    'title': 'Limitations of Liability',
                    'content': 'This section describes liability limitations.'
                }
            ]
        }
        
    async def _get_privacy_policy_template(self) -> Dict[str, Any]:
        """Returns a basic privacy policy template."""
        return {
            'version': '1.0',
            'sections': [
                {
                    'title': 'Data Collection',
                    'content': 'This section describes what data is collected.'
                },
                {
                    'title': 'Data Usage',
                    'content': 'This section describes how data is used.'
                },
                {
                    'title': 'Data Protection',
                    'content': 'This section describes data protection measures.'
                }
            ]
        }
        
    async def _get_disclaimer_template(self) -> Dict[str, Any]:
        """Returns a basic disclaimer template."""
        return {
            'version': '1.0',
            'sections': [
                {
                    'title': 'No Warranty',
                    'content': 'This section describes warranty limitations.'
                },
                {
                    'title': 'Use At Own Risk',
                    'content': 'This section describes user risk acceptance.'
                }
            ]
        }
        
    async def _get_dpa_template(self) -> Dict[str, Any]:
        """Returns a basic Data Processing Agreement template."""
        return {
            'version': '1.0',
            'sections': [
                {
                    'title': 'Data Processing Terms',
                    'content': 'This section describes data processing terms.'
                },
                {
                    'title': 'Security Measures',
                    'content': 'This section describes security measures.'
                }
            ]
        }
        
    async def _get_api_terms_template(self) -> Dict[str, Any]:
        """Returns a basic API terms template."""
        return {
            'version': '1.0',
            'sections': [
                {
                    'title': 'API Usage Terms',
                    'content': 'This section describes API usage terms.'
                },
                {
                    'title': 'Rate Limits',
                    'content': 'This section describes API rate limits.'
                }
            ]
        }
            
    def _check_ip_risks(self, method: Dict[str, Any]) -> tuple:
        """Checks for intellectual property risks."""
        try:
            risk_level = 0.0
            risks = []
            
            # Check for content copying
            if 'copy' in json.dumps(method).lower():
                risk_level += 0.3
                risks.append("Content reproduction detected")
                
            # Check for trademark usage
            if 'brand' in json.dumps(method).lower() or 'trademark' in json.dumps(method).lower():
                risk_level += 0.3
                risks.append("Potential trademark usage")
                
            return risk_level, risks
            
        except Exception as e:
            logger.error(f"IP risk check error: {str(e)}")
            return 1.0, [f"Error checking IP risks: {str(e)}"]
            
    def _check_privacy_risks(self, method: Dict[str, Any]) -> tuple:
        """Checks for privacy-related risks."""
        try:
            risk_level = 0.0
            risks = []
            
            # Check for personal data handling
            if self._handles_personal_data(method):
                risk_level += 0.4
                risks.append("Handles personal data")
                
            # Check for data retention
            if 'store' in json.dumps(method).lower() or 'save' in json.dumps(method).lower():
                risk_level += 0.3
                risks.append("Data retention detected")
                
            return risk_level, risks
            
        except Exception as e:
            logger.error(f"Privacy risk check error: {str(e)}")
            return 1.0, [f"Error checking privacy risks: {str(e)}"]
            
    def _check_financial_risks(self, method: Dict[str, Any]) -> tuple:
        """Checks for financial regulation risks."""
        try:
            risk_level = 0.0
            risks = []
            
            # Check for payment processing
            if self._handles_financial_data(method):
                risk_level += 0.5
                risks.append("Handles financial data")
                
            # Check for money transmission
            if 'transfer' in json.dumps(method).lower() or 'payment' in json.dumps(method).lower():
                risk_level += 0.4
                risks.append("Money transmission detected")
                
            return risk_level, risks
            
        except Exception as e:
            logger.error(f"Financial risk check error: {str(e)}")
            return 1.0, [f"Error checking financial risks: {str(e)}"]
            
    def _check_consumer_risks(self, method: Dict[str, Any]) -> tuple:
        """Checks for consumer protection risks."""
        try:
            risk_level = 0.0
            risks = []
            
            # Check for e-commerce activities
            if self._is_ecommerce(method):
                risk_level += 0.3
                risks.append("E-commerce activities detected")
                
            # Check for marketing claims
            if 'advertis' in json.dumps(method).lower() or 'market' in json.dumps(method).lower():
                risk_level += 0.3
                risks.append("Marketing activities detected")
                
            return risk_level, risks
            
        except Exception as e:
            logger.error(f"Consumer risk check error: {str(e)}")
            return 1.0, [f"Error checking consumer risks: {str(e)}"]
            
    async def _generate_tos(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates terms of service for the method."""
        try:
            template = await self._get_tos_template()
            
            # Customize template based on method characteristics
            tos = template.copy()
            
            if self._handles_personal_data(method):
                tos['sections'].append(self._get_data_protection_section())
                
            if self._handles_financial_data(method):
                tos['sections'].append(self._get_financial_terms_section())
                
            if self._is_ecommerce(method):
                tos['sections'].append(self._get_ecommerce_terms_section())
                
            return tos
            
        except Exception as e:
            logger.error(f"ToS generation error: {str(e)}")
            return {'error': str(e)}
            
    def _get_data_protection_section(self) -> Dict[str, Any]:
        """Returns data protection section for ToS."""
        return {
            'title': 'Data Protection',
            'content': 'This section outlines data protection measures and compliance.'
        }
        
    def _get_financial_terms_section(self) -> Dict[str, Any]:
        """Returns financial terms section for ToS."""
        return {
            'title': 'Financial Terms',
            'content': 'This section outlines payment and financial terms.'
        }
        
    def _get_ecommerce_terms_section(self) -> Dict[str, Any]:
        """Returns e-commerce section for ToS."""
        return {
            'title': 'E-commerce Terms',
            'content': 'This section outlines e-commerce specific terms.'
        }
        
    def _get_data_collection_section(self) -> Dict[str, Any]:
        """Returns data collection section for privacy policy."""
        return {
            'title': 'Data Collection Practices',
            'content': 'This section details our data collection practices.'
        }
        
    def _get_data_usage_section(self) -> Dict[str, Any]:
        """Returns data usage section for privacy policy."""
        return {
            'title': 'Data Usage',
            'content': 'This section explains how collected data is used.'
        }
        
    def _get_product_disclaimer_section(self) -> Dict[str, Any]:
        """Returns product disclaimer section."""
        return {
            'title': 'Product Disclaimer',
            'content': 'This section outlines product-specific disclaimers.'
        }
        
    def _get_financial_disclaimer_section(self) -> Dict[str, Any]:
        """Returns financial disclaimer section."""
        return {
            'title': 'Financial Disclaimer',
            'content': 'This section outlines financial disclaimers.'
        }
        
    def _customize_dpa(self, template: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
        """Customizes Data Processing Agreement for specific method."""
        dpa = template.copy()
        
        # Add method-specific processing terms
        if method.get('data_usage', {}).get('stores_data', False):
            dpa['sections'].append({
                'title': 'Data Storage Terms',
                'content': 'This section outlines data storage procedures.'
            })
            
        return dpa
        
    def _customize_api_terms(self, template: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
        """Customizes API terms for specific method."""
        api_terms = template.copy()
        
        # Add method-specific API terms
        if 'api' in method.get('implementation', {}).get('tools', []):
            api_terms['sections'].append({
                'title': 'API Usage Terms',
                'content': 'This section outlines API usage terms and limits.'
            })
            
        return api_terms
            
    async def _generate_privacy_policy(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates privacy policy for the method."""
        try:
            template = await self._get_privacy_policy_template()
            
            # Customize template based on method characteristics
            policy = template.copy()
            
            if self._handles_personal_data(method):
                policy['sections'].append(self._get_data_collection_section())
                policy['sections'].append(self._get_data_usage_section())
                
            return policy
            
        except Exception as e:
            logger.error(f"Privacy policy generation error: {str(e)}")
            return {'error': str(e)}
            
    async def _generate_disclaimer(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates disclaimer for the method."""
        try:
            template = await self._get_disclaimer_template()
            
            # Customize template based on method characteristics
            disclaimer = template.copy()
            
            if self._is_ecommerce(method):
                disclaimer['sections'].append(self._get_product_disclaimer_section())
                
            if 'financial' in json.dumps(method).lower():
                disclaimer['sections'].append(self._get_financial_disclaimer_section())
                
            return disclaimer
            
        except Exception as e:
            logger.error(f"Disclaimer generation error: {str(e)}")
            return {'error': str(e)}
            
    def _requires_additional_documents(self, method: Dict[str, Any]) -> bool:
        """Determines if method requires additional legal documents."""
        return (
            self._handles_personal_data(method) or
            self._handles_financial_data(method) or
            'api' in json.dumps(method).lower()
        )
        
    async def _generate_dpa(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates Data Processing Agreement if needed."""
        try:
            if self._handles_personal_data(method):
                template = await self._get_dpa_template()
                return self._customize_dpa(template, method)
            return {}
        except Exception as e:
            logger.error(f"DPA generation error: {str(e)}")
            return {'error': str(e)}
            
    async def _generate_api_terms(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generates API terms if needed."""
        try:
            if 'api' in json.dumps(method).lower():
                template = await self._get_api_terms_template()
                return self._customize_api_terms(template, method)
            return {}
        except Exception as e:
            logger.error(f"API terms generation error: {str(e)}")
            return {'error': str(e)}

async def main():
    """Example usage of the LegalAssessmentAgent."""
    agent = LegalAssessmentAgent()
    await agent.initialize()
    
    try:
        # Example method for assessment
        method = {
            'id': 'test_method_001',
            'platform': 'shopify',
            'type': 'ecommerce',
            'data_usage': {
                'collects_personal_data': True,
                'stores_data': True
            },
            'content': {
                'type': 'product_listings',
                'adult': False,
                'spam': False
            }
        }
        
        # Perform legal assessment
        assessment = await agent.assess_method(method)
        
        # Print results
        print(f"Legal Assessment Results:")
        print(json.dumps(assessment, indent=2))
        
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
