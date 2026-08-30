#!/bin/sh
set -e

echo "=== [IBVAP AI Processing Engine] Starting Container Startup Sequence ==="

# 1. Wait for M1 Backend health
echo "--> Checking Backend service readiness..."
python -c "
import time, urllib.request, os, sys

backend_url = os.environ.get('AI_BACKEND_URL', 'http://backend:8000')
health_url = f'{backend_url}/health'

max_retries = 30
for attempt in range(1, max_retries + 1):
    try:
        with urllib.request.urlopen(health_url, timeout=3) as resp:
            if resp.status == 200:
                print('--> Backend is healthy and accepting requests.')
                sys.exit(0)
    except Exception as e:
        print(f'--> Waiting for Backend ({attempt}/{max_retries})... Error: {e}')
        time.sleep(1)

print('ERROR: Backend healthcheck timed out after 30 seconds.')
sys.exit(1)
"

# 2. Determine Video Source Mode
SOURCE_TYPE="${AI_SOURCE_TYPE:-VIDEO_FILE}"
VIDEO_PATH="${AI_VIDEO_PATH:-/app/data/videos/test/sample_test.mp4}"

echo "--> Configured Source Type: ${SOURCE_TYPE}"
if [ "$SOURCE_TYPE" = "VIDEO_FILE" ]; then
    echo "--> Video File Path: ${VIDEO_PATH}"
fi

# 3. Launch Unified AI Pipeline in Headless Mode
echo "--> Starting Unified AI Pipeline Runner..."
if [ "$SOURCE_TYPE" = "VIDEO_FILE" ]; then
    exec python -m ai.pipeline.runner --source video_file --path "$VIDEO_PATH" --headless
else
    exec python -m ai.pipeline.runner --source webcam --index "${AI_CAMERA_INDEX:-0}" --headless
fi
