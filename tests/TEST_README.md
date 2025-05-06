# Flyworks MCP Testing Guide

This directory contains test scripts for validating Flyworks MCP functionality. These scripts are used to verify that digital human creation and lip-sync features work correctly.

## Preparation

1. Ensure that test dependencies are installed:
   ```bash
   uvx install -e ".[test]"
   ```

2. Set environment variables (or use the default values in the scripts):
   ```bash
   # Linux/macOS
   export FLYWORKS_API_TOKEN="your_api_token_here"
   
   # Windows (CMD)
   set FLYWORKS_API_TOKEN=your_api_token_here
   
   # Windows (PowerShell)
   $env:FLYWORKS_API_TOKEN="your_api_token_here"
   ```

3. Make sure the following files are in the `src/flyworks_mcp/assets` directory:
   - `avatar.png` - Image for creating a digital human
   - `avatar.mp4` - Video for creating a digital human
   - `intro.mp3` - Audio file for audio-driven tests

   Note: After installation as a package, the assets will be accessed automatically from the installed package.

## Test Script Structure

The project uses a single comprehensive test script `test_flyworks_mcp.py` that supports both full testing and single-feature testing modes.

### Comprehensive Test Features

The comprehensive test includes the following scenarios:
- Creating a digital human from an image and driving it with text
- Creating a digital human from a video and driving it with text
- Creating a digital human from an image and driving it with audio
- Creating a digital human from a video and driving it with audio
- Reusing an existing digital human ID
- Testing async mode
- Testing with a specific voice ID

### Running Tests

#### Full Test Mode

Run all test scenarios at once:
```bash
# Run from the project root directory
python -m pytest tests/test_flyworks_mcp.py

# Or use the project-provided command
uvx run flyworks-test tests/test_flyworks_mcp.py

# Alternatively, use the script's command line argument
python tests/test_flyworks_mcp.py --mode full
```

#### Single Feature Test Mode

Run a specific test feature:
```bash
# Test creating a digital human from an image and driving with text
python tests/test_flyworks_mcp.py --mode single --test_type image_text

# Test creating a digital human from a video and driving with text
python tests/test_flyworks_mcp.py --mode single --test_type video_text

# Test creating a digital human from an image and driving with audio
python tests/test_flyworks_mcp.py --mode single --test_type image_audio

# Test creating a digital human from a video and driving with audio
python tests/test_flyworks_mcp.py --mode single --test_type video_audio

# Test creating a digital human from a video and using a specific voice
python tests/test_flyworks_mcp.py --mode single --test_type video_specific_voice

# Run all single feature tests
python tests/test_flyworks_mcp.py --mode single --test_type all
```

Test results will be saved in the `test_output` directory, and for full tests, a `test_results.json` file will be generated to record all test results.

## Running Specific Tests with pytest

```bash
# Run a single test function
python -m pytest tests/test_flyworks_mcp.py::test_create_avatar_with_image_and_text

# Run tests containing specific keywords
python -m pytest -k "audio"

# View detailed output
python -m pytest -v
```

## Notes

1. The testing process may take a long time, especially for digital human creation and video generation parts.
2. The default token used (`2aeda3bcefac46a3`) has usage limitations:
   - Limited daily quota
   - Generated videos have watermarks
   - Video length is limited to 45 seconds
3. All test-generated video files are saved in the `test_output` directory in the project root.
4. For failed tests, error messages and details will be displayed. Please troubleshoot based on these error messages.

## Troubleshooting

Common errors and solutions:
- `API key not found`: Check if the environment variable `FLYWORKS_API_TOKEN` is correctly set
- `Insufficient credits`: The free token's quota has been used up, please try again later or use another token
- `File type not supported`: Check if the file format is supported
- `File size exceeds the limit`: The file size is over the limit, try using a smaller file
- `Invalid Token`: The token is invalid or expired, please obtain a new token

## Contact Support

If you encounter problems during testing, please contact the Flyworks team:
- Email: bd@flyworks.ai
- Official documentation: https://api.hifly.cc/hifly_en.html 