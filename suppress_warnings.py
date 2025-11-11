"""
Utility to suppress Popper.js console warnings in Streamlit apps.
"""
import streamlit.components.v1 as components

def suppress_popper_warnings():
    """Inject JavaScript to suppress Popper.js modifier warnings."""
    components.html(
        """
        <script>
        // Suppress specific Popper.js warnings
        const originalWarn = console.warn;
        console.warn = function(...args) {
            const message = args[0];
            if (typeof message === 'string' &&
                message.includes('preventOverflow') &&
                message.includes('hide')) {
                // Suppress this specific warning
                return;
            }
            originalWarn.apply(console, args);
        };
        </script>
        """,
        height=0
    )
