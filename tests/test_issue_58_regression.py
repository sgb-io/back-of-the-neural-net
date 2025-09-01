#!/usr/bin/env python3
"""Regression tests for Issue #58: Fictitious results in news feed before simulation."""

import asyncio
import pytest
import tempfile
import os
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore
from src.neuralnet.config import Config


class TestIssue58Regression:
    """Regression tests for Issue #58 to ensure database reset prevents old reports."""

    @pytest.mark.asyncio
    async def test_fresh_database_has_no_reports(self):
        """Test that a fresh database has no media reports before simulation."""
        # Use temporary database to ensure clean state
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            config = Config()
            config.db_path = temp_db_path
            config.reset_db = False  # No reset needed for fresh file
            
            orchestrator = GameOrchestrator(config=config)
            orchestrator.initialize_world()
            
            # Check for media events
            all_events = orchestrator.event_store.get_events()
            media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
            
            assert len(media_events) == 0, "Fresh database should have no media events"
            
        finally:
            try:
                os.unlink(temp_db_path)
            except:
                pass

    @pytest.mark.asyncio
    async def test_database_reset_clears_old_reports(self):
        """Test that database reset clears old MediaStoryPublished events."""
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            # Step 1: Create data with simulation
            config = Config()
            config.db_path = temp_db_path
            config.reset_db = False
            
            orchestrator1 = GameOrchestrator(config=config)
            orchestrator1.initialize_world()
            
            # Run simulation to create media events
            await orchestrator1.advance_simulation()
            
            all_events = orchestrator1.event_store.get_events()
            media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
            
            # Should have some media events after simulation
            assert len(media_events) > 0, "Should have media events after simulation"
            
            # Step 2: Create new orchestrator with reset=True
            config.reset_db = True
            
            orchestrator2 = GameOrchestrator(config=config)
            orchestrator2.initialize_world()
            
            # Check that media events were cleared
            all_events_after_reset = orchestrator2.event_store.get_events()
            media_events_after_reset = [e for e in all_events_after_reset if e.event_type == "MediaStoryPublished"]
            
            assert len(media_events_after_reset) == 0, "Database reset should clear all media events"
            
        finally:
            try:
                os.unlink(temp_db_path)
            except:
                pass

    @pytest.mark.asyncio
    async def test_persistent_database_without_reset_keeps_old_data(self):
        """Test that persistent database without reset keeps old data (the original issue)."""
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            # Step 1: Create data with simulation
            config = Config()
            config.db_path = temp_db_path
            config.reset_db = False
            
            orchestrator1 = GameOrchestrator(config=config)
            orchestrator1.initialize_world()
            
            # Run simulation to create media events
            await orchestrator1.advance_simulation()
            
            all_events = orchestrator1.event_store.get_events()
            media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
            original_count = len(media_events)
            
            assert original_count > 0, "Should have media events after simulation"
            
            # Step 2: Create new orchestrator WITHOUT reset (simulating server restart)
            config.reset_db = False  # This would cause the original issue
            
            orchestrator2 = GameOrchestrator(config=config)
            orchestrator2.initialize_world()
            
            # Check that old media events are still there
            all_events_after_restart = orchestrator2.event_store.get_events()
            media_events_after_restart = [e for e in all_events_after_restart if e.event_type == "MediaStoryPublished"]
            
            # This demonstrates the original issue - old events persist
            assert len(media_events_after_restart) == original_count, "Without reset, old media events should persist"
            
        finally:
            try:
                os.unlink(temp_db_path)
            except:
                pass

    def test_in_memory_database_is_always_fresh(self):
        """Test that in-memory databases are always fresh (used by regression tests)."""
        # Create orchestrator with in-memory database
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        orchestrator.initialize_world()
        
        # Check for media events
        all_events = orchestrator.event_store.get_events()
        media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
        
        assert len(media_events) == 0, "In-memory database should always be fresh"

    @pytest.mark.asyncio
    async def test_reset_flag_via_environment_variable(self):
        """Test that RESET_DB environment variable works correctly."""
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            # Step 1: Create data without reset
            os.environ.pop("RESET_DB", None)  # Ensure it's not set
            os.environ["DB_PATH"] = temp_db_path
            
            # Force config reload to pick up environment variable
            from src.neuralnet.config import reset_config, load_config
            reset_config()
            
            config = load_config()
            
            orchestrator1 = GameOrchestrator(config=config)
            orchestrator1.initialize_world()
            await orchestrator1.advance_simulation()
            
            all_events = orchestrator1.event_store.get_events()
            media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
            assert len(media_events) > 0, "Should have media events after simulation"
            
            # Step 2: Set environment variable and create new orchestrator
            os.environ["RESET_DB"] = "true"
            
            # Force config reload to pick up environment variable
            reset_config()
            
            config2 = load_config()
            
            orchestrator2 = GameOrchestrator(config=config2)
            orchestrator2.initialize_world()
            
            # Check that database was reset
            all_events_after_reset = orchestrator2.event_store.get_events()
            media_events_after_reset = [e for e in all_events_after_reset if e.event_type == "MediaStoryPublished"]
            
            assert len(media_events_after_reset) == 0, "Environment variable RESET_DB should trigger database reset"
            
        finally:
            # Clean up environment variables
            os.environ.pop("RESET_DB", None)
            os.environ.pop("DB_PATH", None)
            try:
                os.unlink(temp_db_path)
            except:
                pass