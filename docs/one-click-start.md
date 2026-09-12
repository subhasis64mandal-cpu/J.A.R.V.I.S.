# One-click J.A.R.V.I.S. startup

The repository includes `Start-JARVIS.bat` for Windows.

Double-clicking it:

1. Starts the loopback-only Local Agent on `127.0.0.1:8766`.
2. Waits for the agent health check.
3. Starts the J.A.R.V.I.S. runtime and Home Base gateway on `127.0.0.1:8787`.
4. Opens Home Base in the default browser.
5. Stops child services when the launcher exits.

The launcher does not enable arbitrary shell commands, arbitrary Python, arbitrary URLs, or third-party browser automation.

## First use

After pulling `main`, open `Start-JARVIS.bat` from the J.A.R.V.I.S. folder.

Home Base should open automatically after the local services become ready.

## Later packaging

A future release can replace the batch launcher with a Windows executable or installer without changing the runtime architecture.
