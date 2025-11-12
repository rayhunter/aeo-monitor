#!/usr/bin/env python3
"""
Test script to verify graceful shutdown functionality.
This simulates the async task cleanup without running the full Streamlit app.
"""

import asyncio
import signal
import sys
import time

# Simulate the cleanup mechanism
active_tasks = set()

def cleanup_resources():
    """Cleanup function to cancel tasks."""
    print("\n🧹 Starting cleanup of resources...")
    
    if active_tasks:
        print(f"   Cancelling {len(active_tasks)} active tasks...")
        for task in active_tasks:
            if not task.done():
                task.cancel()
                print(f"   ✓ Task cancelled: {task.get_name()}")
    
    print("✅ Cleanup complete")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(signum).name
    print(f"\n⚠️  Received signal {signal_name}, initiating graceful shutdown...")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

async def long_running_task(name, duration):
    """Simulate a long-running API call."""
    try:
        print(f"   🚀 Starting task: {name} (will run for {duration}s)")
        await asyncio.sleep(duration)
        print(f"   ✅ Completed task: {name}")
    except asyncio.CancelledError:
        print(f"   ❌ Cancelled task: {name}")
        raise

async def main():
    """Run test tasks and handle cleanup."""
    print("=" * 60)
    print("🧪 TESTING GRACEFUL SHUTDOWN")
    print("=" * 60)
    print("\nCreating multiple long-running tasks...")
    print("Press Ctrl+C at any time to test graceful shutdown!\n")
    
    # Create several long-running tasks
    task1 = asyncio.create_task(long_running_task("API Call 1", 30), name="task-1")
    task2 = asyncio.create_task(long_running_task("API Call 2", 30), name="task-2")
    task3 = asyncio.create_task(long_running_task("API Call 3", 30), name="task-3")
    
    # Track them
    active_tasks.add(task1)
    active_tasks.add(task2)
    active_tasks.add(task3)
    
    print(f"📊 Tracking {len(active_tasks)} tasks\n")
    
    try:
        # Wait for all tasks
        await asyncio.gather(task1, task2, task3)
        print("\n✅ All tasks completed normally")
    except asyncio.CancelledError:
        print("\n⚠️  Tasks were cancelled")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Signal handlers registered:")
    print("  • SIGINT  (Ctrl+C)")
    print("  • SIGTERM (kill command)")
    print("=" * 60 + "\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        cleanup_resources()
    
    print("\n👋 Test completed\n")

