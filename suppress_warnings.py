"""
Utility to suppress console warnings in Streamlit apps.
"""
import streamlit.components.v1 as components

def suppress_popper_warnings():
    """Inject JavaScript to suppress various console warnings."""
    components.html(
        """
        <script>
        // Suppress Popper.js warnings
        const originalWarn = console.warn;
        console.warn = function(...args) {
            const message = args[0];
            if (typeof message === 'string') {
                // Suppress Popper.js warnings
                if (message.includes('preventOverflow') && message.includes('hide')) {
                    return;
                }
                // Suppress Streamlit theme color warnings
                if (message.includes('Invalid color passed') && message.includes('theme.sidebar')) {
                    return;
                }
            }
            originalWarn.apply(console, args);
        };
        
        // Suppress "Unrecognized feature" errors
        const originalError = console.error;
        console.error = function(...args) {
            const message = args[0];
            if (typeof message === 'string' && message.includes('Unrecognized feature')) {
                return;
            }
            originalError.apply(console, args);
        };
        </script>
        """,
        height=0
    )
