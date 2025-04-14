import pytest
import asyncio
from datetime import datetime
from src.core.meta_learning import MetaLearningCore

@pytest.fixture
async def meta_learning():
    """Fixture to create and cleanup MetaLearningCore instance."""
    core = MetaLearningCore()
    await core.initialize()
    yield core
    await core.close()

@pytest.mark.asyncio
async def test_meta_learning_initialization(meta_learning):
    """Test MetaLearningCore initialization."""
    assert meta_learning.knowledge_graph == {}
    assert meta_learning.active_swarms == {}
    assert meta_learning.success_metrics['min_profit_threshold'] == 10.0
    assert meta_learning.success_metrics['min_roi_threshold'] == 0.3
    assert meta_learning.success_metrics['reinvestment_rate'] == 0.7

@pytest.mark.asyncio
async def test_generate_swarm_template(meta_learning):
    """Test swarm template generation."""
    test_pattern = {
        'id': 'test_pattern_001',
        'type': 'ecommerce',
        'method': 'dropshipping',
        'implementation': {
            'platform': 'shopify',
            'compute_needs': {
                'cpu': 'minimal',
                'memory': '512MB',
                'storage': '1GB'
            }
        }
    }
    
    template = await meta_learning._generate_swarm_template(test_pattern)
    
    assert template is not None
    assert template['pattern_id'] == test_pattern['id']
    assert 'infrastructure' in template
    assert 'automation' in template
    assert 'monetization' in template
    assert 'compliance' in template

@pytest.mark.asyncio
async def test_select_infrastructure(meta_learning):
    """Test infrastructure selection."""
    test_pattern = {
        'implementation': {
            'compute_needs': {
                'cpu': 'minimal',
                'memory': '512MB',
                'storage': '1GB'
            }
        }
    }
    
    infrastructure = await meta_learning._select_infrastructure(test_pattern)
    
    assert infrastructure is not None
    assert 'compute' in infrastructure
    assert 'storage' in infrastructure
    assert 'network' in infrastructure
    
    # Verify compute configuration
    assert infrastructure['compute']['primary']['provider'] == 'cloudflare_workers'
    assert infrastructure['compute']['primary']['tier'] == 'free'
    
    # Verify storage configuration
    assert infrastructure['storage']['primary']['provider'] == 'cloudflare_kv'
    assert infrastructure['storage']['primary']['tier'] == 'free'

@pytest.mark.asyncio
async def test_generate_automation_config(meta_learning):
    """Test automation configuration generation."""
    test_pattern = {
        'type': 'ecommerce',
        'automation_level': 0.8
    }
    
    automation = await meta_learning._generate_automation_config(test_pattern)
    
    assert automation is not None
    assert 'workflows' in automation
    assert 'monitoring' in automation
    assert 'scaling' in automation
    
    # Verify workflows
    workflows = automation['workflows']
    assert any(w['name'] == 'health_check' for w in workflows)
    assert any(w['name'] == 'backup' for w in workflows)
    assert any(w['name'] == 'scaling' for w in workflows)
    
    # Verify monitoring
    assert 'metrics' in automation['monitoring']
    assert 'alerts' in automation['monitoring']
    
    # Verify scaling
    assert automation['scaling']['min_instances'] == 1
    assert automation['scaling']['max_instances'] == 10

@pytest.mark.asyncio
async def test_generate_monetization_config(meta_learning):
    """Test monetization configuration generation."""
    test_pattern = {
        'success_metrics': {
            'min_profit': 500,
            'min_roi': 0.3
        }
    }
    
    monetization = await meta_learning._generate_monetization_config(test_pattern)
    
    assert monetization is not None
    assert 'primary' in monetization
    assert 'secondary' in monetization
    
    # Verify secondary revenue streams
    secondary = monetization['secondary']
    assert 'affiliate' in secondary
    assert 'ads' in secondary
    assert 'upsells' in secondary

@pytest.mark.asyncio
async def test_generate_compliance_config(meta_learning):
    """Test compliance configuration generation."""
    test_pattern = {
        'type': 'ecommerce',
        'region': 'global'
    }
    
    compliance = await meta_learning._generate_compliance_config(test_pattern)
    
    assert compliance is not None
    assert 'privacy' in compliance
    assert 'terms' in compliance
    assert 'security' in compliance
    assert 'monitoring' in compliance
    
    # Verify privacy settings
    assert compliance['privacy']['gdpr_compliant'] is True
    assert compliance['privacy']['ccpa_compliant'] is True
    
    # Verify security settings
    assert compliance['security']['ssl_required'] is True
    assert compliance['security']['audit_logs'] is True

@pytest.mark.asyncio
async def test_find_related_patterns(meta_learning):
    """Test pattern relationship finding."""
    test_pattern = {
        'id': 'test_001',
        'type': 'ecommerce',
        'method': 'dropshipping',
        'implementation': {
            'platform': 'shopify'
        }
    }
    
    # Add some patterns to the knowledge graph
    meta_learning.knowledge_graph = {
        'pattern_001': {
            'pattern': {
                'id': 'pattern_001',
                'type': 'ecommerce',
                'method': 'affiliate',
                'implementation': {
                    'platform': 'shopify'
                }
            }
        },
        'pattern_002': {
            'pattern': {
                'id': 'pattern_002',
                'type': 'ecommerce',
                'method': 'dropshipping',
                'implementation': {
                    'platform': 'woocommerce'
                }
            }
        }
    }
    
    related = await meta_learning._find_related_patterns(test_pattern)
    
    assert related is not None
    assert len(related) > 0
    
    # Verify relationship types
    relationship_types = [r['relationship'] for r in related]
    assert 'same_type' in relationship_types
    assert 'same_platform' in relationship_types

@pytest.mark.asyncio
async def test_collect_swarm_metrics(meta_learning):
    """Test swarm metrics collection."""
    test_swarm = {
        'id': 'test_swarm_001',
        'status': 'running',
        'resources': {
            'compute': {'usage': 0.4},
            'memory': {'usage': 0.6}
        }
    }
    
    metrics = await meta_learning._collect_swarm_metrics(test_swarm)
    
    assert metrics is not None
    assert 'profit' in metrics
    assert 'roi' in metrics
    assert 'uptime' in metrics
    assert 'cpu' in metrics
    assert 'memory' in metrics
    assert 'requests' in metrics
    assert 'errors' in metrics

@pytest.mark.asyncio
async def test_recover_resources(meta_learning):
    """Test resource recovery."""
    test_swarm = {
        'resources': {
            'compute': {'cost': 50},
            'storage': {'cost': 30}
        }
    }
    
    recovered = await meta_learning._recover_resources(test_swarm)
    
    assert recovered == 80.0  # 50 + 30

@pytest.mark.asyncio
async def test_get_minimum_spawn_cost(meta_learning):
    """Test minimum spawn cost calculation."""
    min_cost = await meta_learning._get_minimum_spawn_cost()
    
    assert min_cost == 10.0  # Default minimum spawn cost

if __name__ == '__main__':
    pytest.main(['-v', __file__])
