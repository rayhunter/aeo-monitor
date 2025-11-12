# AEO Monitor Management Guide

## Graceful Shutdown & Process Management

This project now includes comprehensive process management and graceful shutdown capabilities.

## Features

### ✅ Implemented
1. **Process-Level Signal Handlers** - Management script handles Ctrl+C (SIGINT) and termination signals (SIGTERM)
2. **Async Task Cleanup** - Cancels all in-progress API calls gracefully
3. **PostHog Cleanup** - Properly shuts down analytics connections
4. **Management Script** - Easy start/stop/restart commands with graceful shutdown
5. **Process Tracking** - PID file tracking and status monitoring
6. **Exit Cleanup** - Automatic cleanup on normal app exit

### ⚠️ Important: Streamlit Threading Limitations
Due to Streamlit's architecture, signal handlers cannot be registered directly in the app code (it runs in a non-main thread). Instead:
- **Use `manage_app.sh` for production** - Handles signals at the process level
- **Ctrl+C in terminal** - Streamlit will exit, triggering `atexit` cleanup
- **Task tracking still works** - All async tasks are tracked and cancelled on exit

## Management Script Usage

### Basic Commands

```bash
# Start the app
./manage_app.sh start

# Stop the app (graceful shutdown)
./manage_app.sh stop

# Restart the app
./manage_app.sh restart

# Check app status
./manage_app.sh status

# View live logs
./manage_app.sh logs

# Force cleanup all processes (nuclear option)
./manage_app.sh cleanup
```

### What Happens on Shutdown

#### Using Management Script (`./manage_app.sh stop`)
1. Script sends SIGTERM to the Streamlit process
2. Waits up to 10 seconds for graceful shutdown
3. Python's `atexit` handlers trigger cleanup:
   - Cancels all active async tasks (API calls)
   - Shuts down all PostHog client connections
   - Logs cleanup activities
4. If process doesn't exit in 10 seconds, forces SIGKILL

#### Manual Ctrl+C in Terminal (when running `streamlit run app.py`)
When you press Ctrl+C:
- Streamlit catches the signal and begins shutdown
- Python's `atexit` cleanup triggers automatically
- All tracked tasks and connections are cleaned up
- Note: Logging may be limited during rapid shutdown

#### Force Cleanup (`./manage_app.sh cleanup`)
Use this if the app is stuck or processes are orphaned:
- Stops via PID file
- Kills any remaining Streamlit processes
- Cleans up ports 8501-8505
- Removes PID file

## Files Created

- `manage_app.sh` - Management script
- `.streamlit.pid` - Process ID file (auto-managed)
- `streamlit.log` - Application logs

## Logging

All cleanup actions are logged with INFO level:
- Signal reception
- Task cancellation counts
- PostHog shutdowns
- Any errors during cleanup

Check the logs:
```bash
./manage_app.sh logs
# or
tail -f streamlit.log
```

## Troubleshooting

### App won't stop
```bash
./manage_app.sh cleanup
```

### Check if processes are running
```bash
ps aux | grep streamlit
lsof -ti:8501  # or whatever port you're using
```

### View all app status
```bash
./manage_app.sh status
```

## Technical Details

### Python Cleanup Mechanism
- `atexit.register()` - Cleanup function called on normal exit
- Note: Signal handlers can't be used in Streamlit (non-main thread limitation)
- Management script handles signals at the OS process level

### Async Task Management
- All tasks tracked in global `_active_tasks` set
- Tasks auto-remove themselves on completion via callback
- Tasks cancelled on shutdown if still active
- Proper `asyncio.CancelledError` handling

### PostHog Cleanup
- All clients tracked in global `_posthog_clients` list
- Clients shut down properly after each query run
- Forced shutdown via `atexit` on app termination
- Error handling for cleanup failures

## Best Practices

1. **Development**: 
   - `streamlit run app.py` - Direct run, Ctrl+C works and triggers cleanup
   - Cleanup happens automatically via `atexit` handlers
   
2. **Production**: 
   - `./manage_app.sh start` - Background operation with full process control
   - `./manage_app.sh stop` - Graceful shutdown with 10-second timeout
   - Better logging and monitoring capabilities
   
3. **Troubleshooting**:
   - `./manage_app.sh status` - Check if app is running
   - `./manage_app.sh logs` - View live logs
   - `./manage_app.sh cleanup` - Force cleanup as last resort
   
4. **Task Cleanup**:
   - All async API calls are tracked automatically
   - Tasks cancelled if app exits during execution
   - PostHog clients properly shut down after each run

## Example Session

```bash
# Start the app
$ ./manage_app.sh start
Starting AEO Monitor...
✓ App started successfully (PID: 12345)
✓ Log file: /path/to/streamlit.log
✓ Check http://localhost:8501

# Check status
$ ./manage_app.sh status
✓ App is running (PID: 12345)
  Memory usage: 156 MB
  CPU usage: 2.3%

# View logs
$ ./manage_app.sh logs
2025-11-12 10:00:00 - INFO - Signal handlers registered
2025-11-12 10:01:00 - INFO - Starting batch queries...

# Stop when done
$ ./manage_app.sh stop
Stopping AEO Monitor (PID: 12345)...
✓ App stopped gracefully
```

## Notes

- The management script requires bash
- Works on macOS and Linux
- PID file ensures only one instance runs
- 10-second graceful shutdown timeout before force kill

