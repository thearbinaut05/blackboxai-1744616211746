import pytest
from src.core.pattern_discovery import PatternDiscoveryEngine

@pytest.fixture
async def pattern_engine():
    """Fixture to create and cleanup PatternDiscoveryEngine instance."""
    engine = PatternDiscoveryEngine()
    await engine.initialize()
    yield engine
    await engine.close()

@pytest.mark.asyncio
async def test_pattern_discovery(pattern_engine):
    """Test pattern discovery functionality."""
    patterns = await pattern_engine.discover_patterns()
    
    assert patterns is not None
    assert len(patterns) > 0
    
    # Verify pattern structure
    for pattern in patterns:
        assert 'id' in pattern
        assert 'type' in pattern
        assert 'method' in pattern
        assert 'success_metrics' in pattern
        assert 'implementation' in pattern

@pytest.mark.asyncio
async def test_pattern_validation(pattern_engine):
    """Test pattern validation."""
    test_pattern = {
        'id': 'test_001',
        'type': 'ecommerce',
        'method': 'dropshipping',
        'success_metrics': {
            'min_profit': 500,
            'min_roi': 0.3,
            'automation_level': 0.85
        },
        'implementation': {
            'platform': 'shopify',
            'traffic_source': 'tiktok',
            'compute_needs': {
                'cpu': 'minimal',
                'memory': '512MB',
                'storage': '1GB'
            }
        }
    }
    
    is_valid = await pattern_engine._validate_pattern(test_pattern)
    assert is_valid is True

@pytest.mark.asyncio
async def test_invalid_pattern_validation(pattern_engine):
    """Test validation of invalid patterns."""
    invalid_patterns = [
        # Missing required fields
        {
            'id': 'test_002',
            'type': 'ecommerce'
        },
        # Missing success metrics
        {
            'id': 'test_003',
            'type': 'ecommerce',
            'method': 'dropshipping',
            'implementation': {}
        },
        # Missing implementation details
        {
            'id': 'test_004',
            'type': 'ecommerce',
            'method': 'dropshipping',
            'success_metrics': {
                'min_profit': 500,
                'min_roi': 0.3,
                'automation_level': 0.85
            }
        }
    ]
    
    for pattern in invalid_patterns:
        is_valid = await pattern_engine._validate_pattern(pattern)
        assert is_valid is False

@pytest.mark.asyncio
async def test_pattern_analysis(pattern_engine):
    """Test pattern analysis functionality."""
    test_pattern = {
        'id': 'test_005',
        'type': 'saas',
        'method': 'api_service',
        'success_metrics': {
            'min_profit': 800,
            'min_roi': 0.4,
            'automation_level': 0.95
        },
        'implementation': {
            'platform': 'vercel',
            'traffic_source': 'api_marketplace',
            'compute_needs': {
                'cpu': 'moderate',
                'memory': '1GB',
                'storage': '5GB'
            }
        }
    }
    
    analysis = await pattern_engine.analyze_pattern(test_pattern)
    
    assert analysis is not None
    assert 'pattern_id' in analysis
    assert 'metrics' in analysis
    assert 'implementation' in analysis
    assert 'risks' in analysis

@pytest.mark.asyncio
async def test_metrics_analysis(pattern_engine):
    """Test metrics analysis."""
    test_metrics = {
        'min_profit': 1000,
        'min_roi': 0.5,
        'automation_level': 0.9
    }
    
    analysis = await pattern_engine._analyze_metrics({'success_metrics': test_metrics})
    
    assert analysis is not None
    assert 'profit_potential' in analysis
    assert 'roi_potential' in analysis
    assert 'automation_potential' in analysis
    
    # Verify metric calculations
    assert analysis['profit_potential'] == 1.0  # Max score for $1000
    assert analysis['roi_potential'] == 0.5
    assert analysis['automation_potential'] == 0.9

@pytest.mark.asyncio
async def test_implementation_analysis(pattern_engine):
    """Test implementation analysis."""
    test_implementation = {
        'platform': 'shopify',
        'traffic_source': 'tiktok',
        'compute_needs': {
            'cpu': 'minimal',
            'memory': '512MB',
            'storage': '1GB'
        }
    }
    
    analysis = await pattern_engine._analyze_implementation({'implementation': test_implementation})
    
    assert analysis is not None
    assert 'platform_viability' in analysis
    assert 'traffic_potential' in analysis
    assert 'resource_efficiency' in analysis
    
    # Verify platform scores
    assert analysis['platform_viability'] == 0.9  # Shopify score
    assert analysis['traffic_potential'] == 0.9   # TikTok score

@pytest.mark.asyncio
async def test_risk_analysis(pattern_engine):
    """Test risk analysis."""
    test_pattern = {
        'type': 'ecommerce',
        'method': 'dropshipping',
        'success_metrics': {
            'automation_level': 0.95
        },
        'implementation': {
            'platform': 'shopify',
            'dependencies': ['payment_gateway', 'inventory_system']
        }
    }
    
    risks = await pattern_engine._analyze_risks(test_pattern)
    
    assert risks is not None
    assert 'platform_risk' in risks
    assert 'market_risk' in risks
    assert 'technical_risk' in risks
    
    # Verify risk assessments
    platform_risk = risks['platform_risk']
    assert 'level' in platform_risk
    assert 'factors' in platform_risk
    
    market_risk = risks['market_risk']
    assert 'level' in market_risk
    assert 'factors' in market_risk
    
    technical_risk = risks['technical_risk']
    assert 'level' in technical_risk
    assert 'factors' in technical_risk

@pytest.mark.asyncio
async def test_resource_efficiency_assessment(pattern_engine):
    """Test resource efficiency assessment."""
    test_implementations = [
        {
            'compute_needs': {
                'cpu': 'minimal',
                'memory': '256MB',
                'storage': '500MB'
            }
        },
        {
            'compute_needs': {
                'cpu': 'high',
                'memory': '2GB',
                'storage': '10GB'
            }
        }
    ]
    
    for impl in test_implementations:
        score = pattern_engine._assess_resource_efficiency(impl)
        assert 0 <= score <= 1
        
        if impl['compute_needs']['cpu'] == 'minimal':
            assert score > 0.7  # Higher score for minimal resources
        else:
            assert score < 0.5  # Lower score for high resource usage

@pytest.mark.asyncio
async def test_platform_risk_assessment(pattern_engine):
    """Test platform risk assessment."""
    test_patterns = [
        {
            'implementation': {'platform': 'shopify'},
            'success_metrics': {'automation_level': 0.7}
        },
        {
            'implementation': {'platform': 'twitter'},
            'success_metrics': {'automation_level': 0.95}
        }
    ]
    
    for pattern in test_patterns:
        risk = pattern_engine._assess_platform_risk(pattern)
        assert risk['level'] in ['low', 'medium', 'high']
        assert isinstance(risk['factors'], list)
        
        if pattern['implementation']['platform'] == 'twitter':
            assert risk['level'] == 'high'
            assert any('API changes' in factor for factor in risk['factors'])

if __name__ == '__main__':
    pytest.main(['-v', __file__])
