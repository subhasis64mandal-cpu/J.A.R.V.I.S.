# Next integration wave

The next wave will implement browser and desktop adapters one at a time behind the existing policy boundary.

### Browser
Selenium adapter, domain/action allowlists, cancellation, bounded page extraction, and explicit confirmation for state-changing actions.

### Computer
PyAutoGUI adapter, application/window targeting, bounded mouse/keyboard actions, visible execution state, cancellation, and confirmation for state-changing actions.

### Parsing
BeautifulSoup adapter for bounded HTML parsing. It consumes content from the web layer rather than owning network access.

### Devices
Authenticated paired-device transport with explicit capability negotiation. Android will be the first device family.
