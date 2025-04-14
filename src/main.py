import asyncio
import logging
from typing import Dict, List, Any
from src.core.swarm_controller import SwarmController
from src.core.meta_learning import MetaLearningCore
from src.agents.discovery_agent import MethodDiscoveryAgent
from src.agents.legal_agent import LegalAssessmentAgent
from src.agents.resource_agent import ResourceMappingAgent
from src.agents.profit_agent import ProfitAnalysisAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutonomousMethodSystem:
    def __init__(self):
        self.swarm_controller = SwarmController()
        self.meta_learning = MetaLearningCore()
        self.discovery_agent = MethodDiscoveryAgent()
        self.legal_agent = LegalAssessmentAgent()
        self.resource_agent = ResourceMappingAgent()
        self.profit_agent = ProfitAnalysisAgent()
        
    async def initialize(self):
        """Initialize all system components."""
        try:
            logger.info("Initializing Autonomous Method System...")
            
            # Initialize core components
            await self.swarm_controller.initialize()
            await self.meta_learning.initialize()
            
            # Initialize agents
            await self.discovery_agent.initialize()
            await self.legal_agent.initialize()
            await self.resource_agent.initialize()
            
            logger.info("System initialization complete")
            
        except Exception as e:
            logger.error(f"System initialization error: {str(e)}")
            raise
            
    async def close(self):
        """Clean up system resources."""
        try:
            logger.info("Shutting down Autonomous Method System...")
            
            # Close core components
            await self.swarm_controller.close()
            await self.meta_learning.close()
            
            # Close agents
            await self.discovery_agent.close()
            await self.legal_agent.close()
            await self.resource_agent.close()
            
            logger.info("System shutdown complete")
            
        except Exception as e:
            logger.error(f"System shutdown error: {str(e)}")
            raise
            
    async def run(self):
        """Main system execution loop."""
        try:
            logger.info("Starting Autonomous Method System...")
            
            while True:
                # Run meta-learning cycle
                logger.info("Starting meta-learning cycle...")
                await self.meta_learning.run_discovery_cycle()
                
                # Run swarm controller cycle
                logger.info("Starting swarm control cycle...")
                await self.swarm_controller.run()
                
                # Log system status
                await self._log_system_status()
                
                # Wait before next cycle
                await asyncio.sleep(3600)  # Run full cycle every hour
                
        except Exception as e:
            logger.error(f"System execution error: {str(e)}")
            raise
            
    async def _log_system_status(self):
        """Logs current system status."""
        try:
            # Get active swarms
            active_swarms = len(self.swarm_controller.active_swarms)
            
            # Calculate total profits
            total_profit = sum(
                swarm['metrics']['profit'] 
                for swarm in self.swarm_controller.active_swarms.values()
            )
            
            # Get discovered methods
            discovered_methods = len(await self.discovery_agent.discover_methods())
            
            logger.info(f"""
System Status:
-------------
Active Swarms: {active_swarms}
Total Profit: ${total_profit:.2f}
Discovered Methods: {discovered_methods}
            """)
            
        except Exception as e:
            logger.error(f"Status logging error: {str(e)}")

async def main():
    """Main entry point."""
    system = AutonomousMethodSystem()
    
    try:
        # Initialize system
        await system.initialize()
        
        # Run system
        await system.run()
        
    except KeyboardInterrupt:
        logger.info("System shutdown requested...")
    except Exception as e:
        logger.error(f"System error: {str(e)}")
    finally:
        # Cleanup
        await system.close()

if __name__ == "__main__":
    # Run the system
    asyncio.run(main())
