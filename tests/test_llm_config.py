#!/usr/bin/env python3
"""Test the LM Studio integration and configuration."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.config import load_config, validate_llm_config, reset_config
from neuralnet.orchestrator import GameOrchestrator
from neuralnet.llm_lmstudio import LMStudioProvider


async def test_mock_config():
    """Test default mock configuration."""
    print("🧪 Testing mock configuration...")
    
    # Reset config to ensure clean state
    reset_config()
    
    try:
        config = load_config()
        validate_llm_config(config)
        
        orchestrator = GameOrchestrator(config=config)
        orchestrator.initialize_world()
        
        print(f"✓ Provider: {config.llm.provider}")
        print(f"✓ Use tools: {config.use_tools}")
        print(f"✓ World initialized with {len(orchestrator.world.teams)} teams")
        
        # Test simulation step
        result = await orchestrator.advance_simulation()
        print(f"✓ Simulation step completed: {result['status']}")
        
    except Exception as e:
        print(f"❌ Mock configuration test failed: {e}")
        return False
    
    return True


async def test_lmstudio_config():
    """Test LM Studio configuration (without requiring actual LM Studio)."""
    print("\n🧪 Testing LM Studio configuration...")
    
    # Reset and set environment for LM Studio
    reset_config()
    os.environ["LLM_PROVIDER"] = "lmstudio"
    os.environ["LMSTUDIO_MODEL"] = "test-model"
    os.environ["LMSTUDIO_BASE_URL"] = "http://localhost:1234/v1"
    
    try:
        config = load_config()
        validate_llm_config(config)
        
        print(f"✓ Provider: {config.llm.provider}")
        print(f"✓ Model: {config.llm.lmstudio_model}")
        print(f"✓ Base URL: {config.llm.lmstudio_base_url}")
        
        # Test LM Studio provider creation
        provider = LMStudioProvider(config.llm)
        print("✓ LM Studio provider created successfully")
        
        # Test orchestrator with LM Studio config
        orchestrator = GameOrchestrator(config=config)
        orchestrator.initialize_world()
        print(f"✓ World initialized with {len(orchestrator.world.teams)} teams")
        
        # Test simulation step (will fail LLM call but should continue)
        result = await orchestrator.advance_simulation()
        print(f"✓ Simulation step completed with LM Studio provider: {result['status']}")
        
    except Exception as e:
        print(f"❌ LM Studio configuration test failed: {e}")
        return False
    finally:
        # Clean up environment
        for key in ["LLM_PROVIDER", "LMSTUDIO_MODEL", "LMSTUDIO_BASE_URL"]:
            if key in os.environ:
                del os.environ[key]
    
    return True


async def test_invalid_config():
    """Test that invalid configurations are properly rejected."""
    print("\n🧪 Testing invalid configuration handling...")
    
    # Reset and set invalid environment
    reset_config()
    
    # Store original env value
    original_provider = os.environ.get("LLM_PROVIDER")
    original_model = os.environ.get("LMSTUDIO_MODEL")
    
    try:
        os.environ["LLM_PROVIDER"] = "lmstudio"
        # Missing LMSTUDIO_MODEL intentionally
        if "LMSTUDIO_MODEL" in os.environ:
            del os.environ["LMSTUDIO_MODEL"]
        
        config = load_config()
        validate_llm_config(config)
        print("❌ Should have failed validation!")
        return False
        
    except ValueError as e:
        if "LM Studio model must be specified" in str(e):
            print("✓ Invalid configuration properly rejected")
            print(f"✓ Error message: {e}")
            return True
        else:
            print(f"❌ Unexpected error message: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected exception: {e}")
        return False
    finally:
        # Restore original environment
        if original_provider is not None:
            os.environ["LLM_PROVIDER"] = original_provider
        elif "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]
            
        if original_model is not None:
            os.environ["LMSTUDIO_MODEL"] = original_model
        elif "LMSTUDIO_MODEL" in os.environ:
            del os.environ["LMSTUDIO_MODEL"]


async def main():
    """Run all configuration tests."""
    print("🚀 Testing LLM Provider Configuration\n")
    
    tests = [
        test_mock_config(),
        test_lmstudio_config(),
        test_invalid_config()
    ]
    
    results = await asyncio.gather(*tests)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))