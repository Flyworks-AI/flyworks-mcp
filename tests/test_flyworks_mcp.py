#!/usr/bin/env python
"""
Test script for testing the two main tools of the Flyworks MCP server:
1. create_lipsync_video_by_text - Create lip-sync video through text
2. create_lipsync_video_by_audio - Create lip-sync video through audio

This script uses files (images, videos, and audio) in the assets directory to test functionality.
Supports running single feature tests or all tests.
"""

import os
import sys
import asyncio
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import importlib.resources

# Set environment variables if needed
if "FLYWORKS_API_TOKEN" not in os.environ:
    os.environ["FLYWORKS_API_TOKEN"] = "2aeda3bcefac46a3"  # Using a sample token, please replace with your valid token when actually using

# Path settings
# Get project root directory (parent directory of tests)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_DIR = PROJECT_ROOT / "test_output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Import Flyworks MCP functionality
sys.path.insert(0, str(PROJECT_ROOT))
from src.flyworks_mcp.server import create_lipsync_video_by_text, create_lipsync_video_by_audio, create_avatar

# Get paths to asset files - works both during development and after installation
try:
    # First try to import from the package after installation
    import flyworks_mcp.assets
    ASSETS_DIR = Path(str(importlib.resources.files('flyworks_mcp') / 'assets'))
except (ImportError, AttributeError):
    # Fallback to development path during development
    ASSETS_DIR = PROJECT_ROOT / "src" / "flyworks_mcp" / "assets"

# File paths for testing
IMAGE_PATH = ASSETS_DIR / "avatar.png"
VIDEO_PATH = ASSETS_DIR / "avatar.mp4"
AUDIO_PATH = ASSETS_DIR / "intro.mp3"

# Specific voice ID
SPECIFIC_VOICE_ID = "UDYhgNAvDTZegmum3Di4Fw"
 

async def test_create_avatar_with_image_and_text() -> Dict[str, Any]:
    """Create a digital human using an image and drive it with text"""
    print("\n=== Test 1: Create a digital human using an image and drive it with text ===")
    
    result = await create_lipsync_video_by_text(
        avatar_image_file=str(IMAGE_PATH),
        text="This is a speech synthesis test using a digital human created from an image. Flyworks MCP is a free, fast zero-sample lip-sync tool.",
        title="Image Avatar Text Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "image_avatar_text.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Created digital human ID: {result.get('created_avatar')}")
        print(f"Selected voice ID: {result.get('selected_voice')}")
    
    return result

async def test_create_avatar_with_video_and_text() -> Dict[str, Any]:
    """Create a digital human using a video and drive it with text"""
    print("\n=== Test 2: Create a digital human using a video and drive it with text ===")
    
    result = await create_lipsync_video_by_text(
        avatar_video_file=str(VIDEO_PATH),
        text="This is a speech synthesis test using a digital human created from a video. Digital humans created from videos typically have better quality but take longer to process.",
        title="Video Avatar Text Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "video_avatar_text.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Created digital human ID: {result.get('created_avatar')}")
        print(f"Selected voice ID: {result.get('selected_voice')}")
    
    return result

async def test_create_avatar_with_image_and_audio() -> Dict[str, Any]:
    """Create a digital human using an image and drive it with audio"""
    print("\n=== Test 3: Create a digital human using an image and drive it with audio ===")
    
    result = await create_lipsync_video_by_audio(
        avatar_image_file=str(IMAGE_PATH),
        audio_file=str(AUDIO_PATH),
        title="Image Avatar Audio Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "image_avatar_audio.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Created digital human ID: {result.get('created_avatar')}")
    
    return result

async def test_create_avatar_with_video_and_audio() -> Dict[str, Any]:
    """Create a digital human using a video and drive it with audio"""
    print("\n=== Test 4: Create a digital human using a video and drive it with audio ===")
    
    result = await create_lipsync_video_by_audio(
        avatar_video_file=str(VIDEO_PATH),
        audio_file=str(AUDIO_PATH),
        title="Video Avatar Audio Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "video_avatar_audio.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Created digital human ID: {result.get('created_avatar')}")
    
    return result

async def test_reuse_avatar_with_text_and_audio() -> Dict[str, Any]:
    """Test using a previously created digital human with text and audio"""
    print("\n=== Test 5: Using an existing digital human ID for text and audio tests ===")
    
    # First, create a digital human and get its ID
    create_result = await create_lipsync_video_by_text(
        avatar_image_file=str(IMAGE_PATH),
        text="This is a short test to get a digital human ID.",
        title="Get Digital Human ID",
        async_mode=True  # Async mode, only need the ID without waiting for video generation
    )
    
    if "error" in create_result:
        print(f"❌ Failed to create digital human: {create_result['error']}")
        return create_result
    
    avatar_id = create_result.get("created_avatar")
    print(f"Created digital human ID: {avatar_id}")
    
    if not avatar_id:
        print("❌ Failed to get digital human ID")
        return {"error": "Failed to get digital human ID"}
    
    # Use the existing digital human ID to create a text-driven video
    text_result = await create_lipsync_video_by_text(
        avatar=avatar_id,
        text="This is a video created using an existing digital human ID, driven by text. Reusing digital human IDs can save creation time.",
        title="Reuse Avatar Text Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "reuse_avatar_text.mp4")
    )
    
    if "error" in text_result:
        print(f"❌ Text test failed: {text_result['error']}")
    else:
        print(f"✅ Text test successful: Video saved to {text_result.get('download_result', {}).get('output_path')}")
    
    # Use the existing digital human ID to create an audio-driven video
    audio_result = await create_lipsync_video_by_audio(
        avatar=avatar_id,
        audio_file=str(AUDIO_PATH),
        title="Reuse Avatar Audio Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "reuse_avatar_audio.mp4")
    )
    
    if "error" in audio_result:
        print(f"❌ Audio test failed: {audio_result['error']}")
    else:
        print(f"✅ Audio test successful: Video saved to {audio_result.get('download_result', {}).get('output_path')}")
    
    return {
        "avatar_id": avatar_id,
        "text_result": text_result,
        "audio_result": audio_result
    }

async def test_async_mode() -> Dict[str, Any]:
    """Test creating video in async mode and checking task status"""
    print("\n=== Test 6: Testing async mode and task query ===")
    
    # Create video in async mode
    result = await create_lipsync_video_by_text(
        avatar_image_file=str(IMAGE_PATH),
        text="This is an async mode test. In async mode, the API immediately returns a task ID without waiting for the video to be generated.",
        title="Async Mode Test",
        async_mode=True  # Enable async mode
    )
    
    if "error" in result:
        print(f"❌ Failed to create task: {result['error']}")
        return result
    
    task_id = result.get("task_id")
    print(f"Received task ID: {task_id}")
    
    if not task_id:
        print("❌ Failed to get task ID")
        return {"error": "Failed to get task ID"}
    
    # Import functions to wait for task completion
    from src.flyworks_mcp.server import wait_for_task_completion, download_video
    
    # Check task status every 10 seconds, wait up to 5 minutes
    print("Waiting for task to complete...")
    task_result = await wait_for_task_completion(task_id, timeout=300, interval=10)
    
    if "error" in task_result:
        print(f"❌ Task execution failed: {task_result['error']}")
        if "details" in task_result:
            print(f"Details: {json.dumps(task_result['details'], indent=2, ensure_ascii=False)}")
        return task_result
    
    print("✅ Task completed")
    
    # Download the video
    video_url = task_result.get("video_Url")
    if not video_url:
        print("❌ Failed to get video URL")
        return {"error": "Failed to get video URL", "task_result": task_result}
    
    output_path = str(OUTPUT_DIR / "async_mode_test.mp4")
    download_result = await download_video(video_url, output_path)
    
    if "error" in download_result:
        print(f"❌ Video download failed: {download_result['error']}")
        return {"error": "Video download failed", "download_error": download_result["error"]}
    
    print(f"✅ Video downloaded to: {download_result.get('output_path')}")
    
    return {
        "task_id": task_id,
        "task_result": task_result,
        "download_result": download_result
    }

async def test_video_with_specific_voice() -> Dict[str, Any]:
    """Test creating a digital human using a video and using a specific voice ID"""
    print("\n=== Test 7: Create a digital human using a video and a specific voice ID ===")
    
   
    # Create digital human using the dedicated function
    create_result = await create_avatar(
        video_file=str(VIDEO_PATH),
        title="Digital Human from Video"    
    )
    
    if "error" in create_result:
        print(f"❌ Failed to create digital human: {create_result['error']}")
        return create_result
    
    avatar_id = create_result.get("avatar")
    print(f"Created digital human ID: {avatar_id}")
    
    if not avatar_id:
        print("❌ Failed to get digital human ID")
        return {"error": "Failed to get digital human ID"}
    
    # Use the created digital human ID and specified voice ID to create a video
    result = await create_lipsync_video_by_text(
        avatar=avatar_id,
        voice=SPECIFIC_VOICE_ID,  # Use specific voice ID
        text="This is a test of a digital human created from a video, driven using a specific voice ID. By specifying a particular voice ID, you can ensure the generated video uses the expected voice.",
        title="Specific Voice ID Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "video_with_specific_voice.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Used digital human ID: {avatar_id}")
        print(f"Used voice ID: {SPECIFIC_VOICE_ID}")
        print(f"Returned voice ID: {result.get('selected_voice')}")  # Verify that the specified voice ID was used
    
    return {
        "avatar_id": avatar_id,
        "voice_id": SPECIFIC_VOICE_ID,
        "result": result
    }

# Single feature test functions
async def test_image_text() -> Dict[str, Any]:
    """Image + Text test"""
    print("\n=== Single Feature Test: Image + Text ===")
    
    result = await create_lipsync_video_by_text(
        avatar_image_file=str(IMAGE_PATH),
        text="This is a test of a digital human created from an image, driven by text. Flyworks MCP is a free, fast zero-sample lip-sync tool.",
        title="Image+Text Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "single_test_image_text.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Digital human ID: {result.get('created_avatar')}")
        print(f"Voice ID: {result.get('selected_voice')}")
    
    return result

async def test_video_text() -> Dict[str, Any]:
    """Video + Text test"""
    print("\n=== Single Feature Test: Video + Text ===")
    
    result = await create_lipsync_video_by_text(
        avatar_video_file=str(VIDEO_PATH),
        text="This is a test of a digital human created from a video, driven by text. Digital humans created from videos typically have better quality but take longer to process.",
        title="Video+Text Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "single_test_video_text.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Digital human ID: {result.get('created_avatar')}")
        print(f"Voice ID: {result.get('selected_voice')}")
    
    return result

async def test_image_audio() -> Dict[str, Any]:
    """Image + Audio test"""
    print("\n=== Single Feature Test: Image + Audio ===")
    
    result = await create_lipsync_video_by_audio(
        avatar_image_file=str(IMAGE_PATH),
        audio_file=str(AUDIO_PATH),
        title="Image+Audio Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "single_test_image_audio.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Digital human ID: {result.get('created_avatar')}")
    
    return result

async def test_video_audio() -> Dict[str, Any]:
    """Video + Audio test"""
    print("\n=== Single Feature Test: Video + Audio ===")
    
    result = await create_lipsync_video_by_audio(
        avatar_video_file=str(VIDEO_PATH),
        audio_file=str(AUDIO_PATH),
        title="Video+Audio Test",
        async_mode=False,
        output_path=str(OUTPUT_DIR / "single_test_video_audio.mp4")
    )
    
    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"✅ Test successful: Video saved to {result.get('download_result', {}).get('output_path')}")
        print(f"Digital human ID: {result.get('created_avatar')}")
    
    return result

async def run_all_tests():
    """Run all tests and collect results"""
    test_results = {}
    
    print("Starting Flyworks MCP Tests...\n")
    print(f"Using image: {IMAGE_PATH}")
    print(f"Using video: {VIDEO_PATH}")
    print(f"Using audio: {AUDIO_PATH}")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Execute tests
    test_results["image_text"] = await test_create_avatar_with_image_and_text()
    test_results["video_text"] = await test_create_avatar_with_video_and_text()
    test_results["image_audio"] = await test_create_avatar_with_image_and_audio()
    test_results["video_audio"] = await test_create_avatar_with_video_and_audio()
    test_results["reuse_avatar"] = await test_reuse_avatar_with_text_and_audio()
    test_results["async_mode"] = await test_async_mode()
    test_results["video_specific_voice"] = await test_video_with_specific_voice()
    
    # Summarize results
    print("\n=== Test Results Summary ===")
    
    success_count = 0
    failed_tests = []
    
    for test_name, result in test_results.items():
        if "error" not in result:
            success_count += 1
        else:
            failed_tests.append(test_name)
    
    print(f"Total tests: {len(test_results)}")
    print(f"Successful tests: {success_count}")
    print(f"Failed tests: {len(test_results) - success_count}")
    
    if failed_tests:
        print(f"Failed tests: {', '.join(failed_tests)}")
    
    print("\nTests completed!")
    
    # Save test results to file
    with open(OUTPUT_DIR / "test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"Test results saved to: {OUTPUT_DIR / 'test_results.json'}")

async def run_single_function_test(test_type):
    """Run a single feature test"""
    print("Starting Flyworks MCP Single Feature Test...\n")
    print(f"Test type: {test_type}")
    print(f"Using image: {IMAGE_PATH}")
    print(f"Using video: {VIDEO_PATH}")
    print(f"Using audio: {AUDIO_PATH}")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    result = {}
    
    if test_type == "image_text" or test_type == "all":
        result = await test_image_text()
    
    if test_type == "video_text" or test_type == "all":
        result = await test_video_text()
    
    if test_type == "image_audio" or test_type == "all":
        result = await test_image_audio()
    
    if test_type == "video_audio" or test_type == "all":
        result = await test_video_audio()
    
    if test_type == "video_specific_voice" or test_type == "all":
        result = await test_video_with_specific_voice()
    
    print("\nTest completed!")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Flyworks MCP functionality")
    parser.add_argument(
        "--mode", 
        choices=["full", "single"],
        default="full",
        help="Test mode: full - comprehensive testing; single - single feature testing"
    )
    parser.add_argument(
        "--test_type", 
        choices=["image_text", "video_text", "image_audio", "video_audio", "video_specific_voice", "all"],
        default="all",
        help="Type of single feature test"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        # Run all tests
        asyncio.run(run_all_tests())
    else:
        # Run single feature test
        asyncio.run(run_single_function_test(args.test_type)) 