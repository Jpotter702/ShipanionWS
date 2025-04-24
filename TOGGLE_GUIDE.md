# REST/Internal Call Toggle Guide

This document explains the implementation of the toggle between REST API calls and internal function calls.

## Overview

The WebSocket server has been updated with a toggle called `USE_INTERNAL` that controls how shipping-related functionality is accessed:

- When `USE_INTERNAL = False` (default): The server makes HTTP requests to the ShipVox API endpoints.
- When `USE_INTERNAL = True`: The server calls internal functions directly from the backend service module.

This toggle is designed to facilitate the transition after the backend merge, allowing for easy switching between the two modes of operation.

## Implementation Details

### 1. Settings Module

A new `settings.py` module has been created to centralize configuration settings, including the `USE_INTERNAL` toggle:

```python
# Toggle for using internal function calls vs REST API
USE_INTERNAL = os.environ.get("USE_INTERNAL", "False").lower() == "true"
```

By default, `USE_INTERNAL` is set to `False`, meaning the server will use REST API calls. This can be changed by setting the `USE_INTERNAL` environment variable to `True`.

### 2. Internal Service Module

A new `shipping_service.py` module has been created to provide internal implementations of the shipping-related functionality:

- `get_shipping_quotes`: Internal implementation of the `/get-rates` endpoint
- `create_shipping_label`: Internal implementation of the `/labels` endpoint

These functions have the same interface as their REST API counterparts, making it easy to switch between the two modes.

### 3. ShipVox Client

The `ShipVoxClient` class in `shipvox_client.py` has been updated to use the toggle:

```python
async def get_rates(self, rate_request: Dict[str, Any], timeout_seconds: float = 10.0) -> Dict[str, Any]:
    # If USE_INTERNAL is True, call the internal function directly
    if USE_INTERNAL:
        logger.info("Using internal get_shipping_quotes function")
        try:
            # Call the internal function
            result = await internal_get_shipping_quotes(rate_request)
            logger.info("Internal get_shipping_quotes call successful")
            return result
        except TimeoutError as e:
            # Handle timeout from internal function
            logger.error(f"Internal get_shipping_quotes call timed out: {str(e)}")
            # Re-raise with the exact error message
            raise Exception("timeout calling rates endpoint")
        # ... other exception handling ...
    else:
        # Use the REST API
        url = f"{self.base_url}/get-rates"
        # ... REST API implementation ...
```

This conditional logic ensures that the appropriate method is used based on the toggle setting.

## How to Use the Toggle

### Setting the Toggle

The toggle can be set in two ways:

1. **Environment Variable**: Set the `USE_INTERNAL` environment variable before starting the server:

```bash
# Use internal function calls
export USE_INTERNAL=true
python -m uvicorn backend.main:app --reload --port 8001

# Use REST API calls (default)
export USE_INTERNAL=false
python -m uvicorn backend.main:app --reload --port 8001
```

2. **Settings File**: Modify the `USE_INTERNAL` value in `backend/settings.py`:

```python
# Toggle for using internal function calls vs REST API
USE_INTERNAL = True  # or False
```

### Verifying the Toggle

When the server starts, it logs the current toggle setting:

```
INFO:backend.main:Starting server with USE_INTERNAL=False
```

You can also verify the toggle by examining the logs during a rate request:

- When `USE_INTERNAL = False`: `INFO:backend.shipvox_client:Sending rate request to http://localhost:8000/api/get-rates with timeout of 10.0 seconds`
- When `USE_INTERNAL = True`: `INFO:backend.shipvox_client:Using internal get_shipping_quotes function`

## Testing the Toggle

A test script `test_toggle.py` has been provided to verify the toggle functionality:

```bash
# Test with USE_INTERNAL=False (default)
python test_toggle.py

# Test with USE_INTERNAL=True
USE_INTERNAL=true python test_toggle.py
```

The test script sends a rate request and verifies that the response contains valid shipping quotes, regardless of which mode is used.

## Benefits

This toggle implementation provides several benefits:

1. **Smooth Transition**: Facilitates a smooth transition after the backend merge
2. **Easy Testing**: Allows for easy testing of both modes of operation
3. **Fallback Option**: Provides a fallback option if one mode encounters issues
4. **Flexibility**: Gives developers the flexibility to choose the most appropriate mode for their needs
5. **Consistency**: Ensures consistent behavior regardless of which mode is used
