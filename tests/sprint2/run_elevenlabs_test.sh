#!/bin/bash

# Run the ElevenLabs full flow test
# This script runs the test_elevenlabs_full_flow.py script

# Set environment variables
export WS_SERVER_URL="ws://localhost:8000/ws"
export API_SERVER_URL="http://localhost:8000"

# Activate the virtual environment if it exists
if [ -d "../../venv" ]; then
    echo "Activating virtual environment..."
    source ../../venv/bin/activate
fi

# Run the test
echo "Running ElevenLabs full flow test..."
python test_elevenlabs_full_flow.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
else
    echo "Test failed!"
fi
