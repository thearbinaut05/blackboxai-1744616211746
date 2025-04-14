import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from .meta_learning import MetaLearningCore
from src.agents.discovery_agent import MethodDiscoveryAgent
from src.agents.legal_agent import LegalAssessmentAgent
from src.agents.resource_agent import ResourceMappingAgent
from src.agents.profit_agent import ProfitAnalysisAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwarmController:
    def __init__(self):
        self.meta_learning = MetaLearningCore()
        self.discovery_agent = MethodDiscoveryAgent()
        self.legal_agent = LegalAssessmentAgent()
        self.resource_agent = ResourceMappingAgent()
        self.profit_agent = ProfitAnalysisAgent()
        self.active_swarms = {}
        
    async def initialize(self):
        """Initialize the swarm controller and its components."""
        await self.meta_learning.initialize()
        await self.discovery_agent.initialize()
        await self.legal_agent.initialize()
        await self.resource_agent.initialize()
        
    async def close(self):
        """Clean up resources."""
        await self.meta_learning.close()
        await self.discovery_agent.close()
        await self.legal_agent.close()
        await self.resource_agent.close()
        
    async def run(self):
        """Main swarm control loop."""
        try:
            while True:
                # Run meta-learning discovery cycle
                await self.meta_learning.run_discovery_cycle()
                
                # Process discovered patterns
                patterns = await self.discovery_agent.discover_methods()
                logger.info(f"Discovered {len(patterns)} methods")
                
                for pattern in patterns:
                    # Validate legal compliance
                    legal_assessment = await self.legal_agent.assess_method(pattern)
                    if not legal_assessment['approved']:
                        logger.info(f"Method {pattern['id']} rejected: legal concerns")
                        continue
                        
                    # Map resources
                    resources = await self.resource_agent.map_resources(pattern)
                    if not resources:
                        logger.info(f"Method {pattern['id']} rejected: resource constraints")
                        continue
                        
                    # Analyze profitability
                    profit_analysis = await self.profit_agent.analyze_profits(pattern, resources)
                    if not self._is_profitable(profit_analysis):
                        logger.info(f"Method {pattern['id']} rejected: insufficient profit potential")
                        continue
                        
                    # Deploy swarm
                    swarm = await self._deploy_swarm(pattern, legal_assessment, resources, profit_analysis)
                    if swarm:
                        logger.info(f"Deployed swarm for method {pattern['id']}")
                        
                await asyncio.sleep(3600)  # Run cycle every hour
                
        except Exception as e:
            logger.error(f"Swarm control error: {str(e)}")
            
    async def _deploy_swarm(self, pattern: Dict[str, Any], legal: Dict[str, Any], 
                          resources: Dict[str, Any], profit: Dict[str, Any]) -> Dict[str, Any]:
        """Deploys a new swarm instance."""
        try:
            swarm_id = f"swarm_{len(self.active_swarms)}"
            
            swarm = {
                'id': swarm_id,
                'pattern': pattern,
                'legal_framework': legal,
                'resources': resources,
                'profit_model': profit,
                'status': 'initializing',
                'created_at': datetime.utcnow().isoformat(),
                'metrics': {
                    'profit': 0,
                    'roi': 0,
                    'uptime': 0
                }
            }
            
            # Initialize infrastructure
            swarm['infrastructure'] = await self._initialize_infrastructure(resources)
            
            # Setup monitoring
            swarm['monitoring'] = await self._setup_monitoring(swarm_id)
            
            # Deploy automation
            swarm['automation'] = await self._deploy_automation(pattern)
            
            # Start lifecycle management
            asyncio.create_task(self._manage_lifecycle(swarm_id))
            
            self.active_swarms[swarm_id] = swarm
            return swarm
            
        except Exception as e:
            logger.error(f"Swarm deployment error: {str(e)}")
            return None
            
    async def _manage_lifecycle(self, swarm_id: str):
        """Manages the lifecycle of a swarm."""
        try:
            while True:
                swarm = self.active_swarms.get(swarm_id)
                if not swarm:
                    break
                    
                # Update metrics
                metrics = await self._collect_metrics(swarm)
                swarm['metrics'] = metrics
                
                # Check profitability
                if metrics['profit'] > 0:
                    # Reinvest in growth
                    await self._reinvest_profits(swarm, metrics['profit'])
                elif metrics['roi'] < 0.3:  # Below 30% ROI threshold
                    # Sunset swarm
                    await self._sunset_swarm(swarm_id)
                    break
                    
                await asyncio.sleep(3600)  # Check every hour
                
        except Exception as e:
            logger.error(f"Lifecycle management error: {str(e)}")
            
    def _is_profitable(self, profit_analysis: Dict[str, Any]) -> bool:
        """Determines if a method is profitable enough to deploy."""
        try:
            monthly_profit = profit_analysis.get('monthly', {}).get('net_profit', 0)
            roi = profit_analysis.get('yearly', {}).get('roi', 0)
            
            return monthly_profit >= 100 and roi >= 0.5  # $100/month minimum, 50% ROI
            
        except Exception as e:
            logger.error(f"Profitability check error: {str(e)}")
            return False
            
    async def _reinvest_profits(self, swarm: Dict[str, Any], profit: float):
        """Reinvests profits into growth."""
        try:
            # Allocate profits
            reinvestment = profit * 0.7  # 70% to growth
            hunter_budget = profit * 0.2  # 20% to method hunters
            owner_payout = profit * 0.1   # 10% to owner
            
            # Scale infrastructure
            if reinvestment > 0:
                await self._scale_infrastructure(swarm, reinvestment)
                
            # Fund method discovery
            if hunter_budget > 0:
                await self.discovery_agent.fund_discovery(hunter_budget)
                
            # Process owner payout
            if owner_payout > 0:
                await self._process_payout(owner_payout)
                
        except Exception as e:
            logger.error(f"Profit reinvestment error: {str(e)}")
            
    async def _sunset_swarm(self, swarm_id: str):
        """Gracefully terminates a swarm."""
        try:
            swarm = self.active_swarms.get(swarm_id)
            if not swarm:
                return
                
            # Recover resources
            recovered = await self._recover_resources(swarm)
            
            # Reinvest in discovery
            if recovered > 0:
                await self.discovery_agent.fund_discovery(recovered)
                
            # Remove from active swarms
            del self.active_swarms[swarm_id]
            
            logger.info(f"Sunset swarm {swarm_id}")
            
        except Exception as e:
            logger.error(f"Swarm sunsetting error: {str(e)}")

async def main():
    """Example usage of the SwarmController."""
    controller = SwarmController()
    await controller.initialize()
    
    try:
        await controller.run()
    finally:
        await controller.close()

if __name__ == "__main__":
    asyncio.run(main())
