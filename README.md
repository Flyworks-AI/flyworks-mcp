# Flyworks MCP: Free & Fast Zeroshot Lipsync Tool
<div align="left">
  <a href="https://discord.gg/YappgYYYFD" target="_blank">
    <img src="https://img.shields.io/badge/Flyworks-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
  </a>
  <a href="https://x.com/flyworks_ai" target="_blank">
    <img src="https://img.shields.io/badge/Flyworks%20AI-%23000000.svg?style=for-the-badge&logo=X&logoColor=white" alt="Flyworks AI">
  </a>
  <a href="https://smithery.ai/server/@Flyworks-AI/flyworks-mcp"><img alt="Smithery Badge" src="https://smithery.ai/badge/@Flyworks-AI/flyworks-mcp"></a>
</div>

### Overview

The Flyworks MCP is a Model Context Protocol (MCP) server that provides a convenient interface for interacting with the Flyworks API. It facilitates fast and free lipsync video creation for a wide range of digital avatars, including realistic and cartoon styles.

### Demo

Input avatar video (footage):
<div align="center">
  <video src="https://github.com/user-attachments/assets/2a062560-024a-43bc-9d91-9caa70fae2f4"> </video>
</div>

Audio clip with TTS saying `我是一个飞影数字人。Welcome to Flyworks MCP server demo. This tool enables fast and free lipsync video creation for a wide range of digital avatars, including realistic and cartoon styles.`:
<div align="center">
<video src="https://github.com/user-attachments/assets/8a529c16-acc7-42ad-bacf-fafefea9cf25"></video>
</div>



Generated lipsync video:
<div align="center">
<video src="https://github.com/user-attachments/assets/52dbdd27-e345-49c2-8f46-586335248b9b"></video>
</div>

### Features

- Create lipsynced videos using digital avatar video and audio as inputs
- Create lipsynced videos by text (with text-to-speech)
- Create digital human avatars from images or videos
- Support for both async and sync modes of operation
- More features coming soon...

### Requirements

- Python 3.8+
- Dependencies: `httpx`, `mcp[cli]`

### Usage

#### Integration with Claude or Other MCP Clients

##### Using in Claude Desktop

Go to `Claude > Settings > Developer > Edit Config > claude_desktop_config.json` to include the following:

```json
{
  "mcpServers": {
    "flyworks": {
      "command": "uvx",
      "args": [
        "flyworks-mcp",
        "-y"
      ],
      "env": {
        "FLYWORKS_API_TOKEN": "your_api_token_here",
        "FLYWORKS_API_BASE_URL": "https://hfw-api.hifly.cc/api/v2/hifly",
        "FLYWORKS_MCP_BASE_PATH": "/path/to/your/output/directory"
      }
    }
  }
}
```

##### Using in Cursor
Go to `Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP Server` to add above config.

Make sure to replace `your_api_token_here` with your actual API token, and update the `FLYWORKS_MCP_BASE_PATH` to a valid directory on your system where output files will be saved.

> **Note:** We offer free trial access to our tool with the token `2aeda3bcefac46a3`. However, please be aware that the daily quota for this free access is limited. Additionally, the generated videos will be watermarked and restricted to a duration of 45 seconds. For full access, please contact us at bd@flyworks.ai to acquire your token.



#### Installing via Smithery

To install flyworks-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@Flyworks-AI/flyworks-mcp):

```bash
npx -y @smithery/cli install @Flyworks-AI/flyworks-mcp --client claude
```
#### Install locally
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/flyworks-mcp.git
   cd flyworks-mcp
   ```

2. Install dependencies:
   ```bash
   pip install httpx "mcp[cli]>=1.6.0"
   ```
   
   Or using `uv`:
   ```bash
   uv pip install httpx "mcp[cli]>=1.6.0"
   ```

   To avoid timeout issues during server startup, we recommend pre-installing all dependencies:
   ```bash
   pip install pygments pydantic-core httpx "mcp[cli]>=1.6.0"
   ```

3. Configuration

Set your Flyworks API token as an environment variable:

```bash
# Linux/macOS
export FLYWORKS_API_TOKEN="your_token_here"

# Windows (Command Prompt)
set FLYWORKS_API_TOKEN=your_token_here

# Windows (PowerShell)
$env:FLYWORKS_API_TOKEN="your_token_here"
```

Alternatively, you can create a `.env` file.


4. Running the Server

Run the `server.py` file directly:

```bash
python server.py
```

##### spawn uvx ENOENT issue:
Please confirm its absolute path by running this command in your terminal:
```sh
which uvx
```
Once you obtain the absolute path (e.g., /usr/local/bin/uvx), update your configuration to use that path (e.g., "command": "/usr/local/bin/uvx"). 

### Tool Description

#### 1. Create Lipsync Video by Audio (`create_lipsync_video_by_audio`)

Create a lipsync video with audio input. Animates a digital human avatar to speak in sync with the provided audio.

**Parameters**:
- `avatar`: Digital human avatar ID. Either this or avatar creation parameters must be provided.
- `avatar_video_url`: URL of a video to create the avatar from.
- `avatar_image_url`: URL of an image to create the avatar from.
- `avatar_video_file`: Local path to a video file to create the avatar from.
- `avatar_image_file`: Local path to an image file to create the avatar from.
- `audio_url`: Remote URL of the audio file. One of audio_url or audio_file must be provided.
- `audio_file`: Local path to the audio file. One of audio_url or audio_file must be provided.
- `title`: Optional title for the created video.
- `async_mode`: If true, returns task_id immediately. If false, waits for completion and downloads the video. Default is true.
- `output_path`: Where to save the downloaded video if async_mode is false. Default is "output.mp4".

**Notes**:
- For avatar creation, provide exactly ONE of avatar_video_url, avatar_image_url, avatar_video_file, or avatar_image_file.
- If avatar ID is directly provided, these parameters will be ignored.

**Returns**:
- If async_mode is true: task_id for checking status later and created_avatar (if a new avatar was created)
- If async_mode is false: downloaded video path, task result, and created_avatar (if applicable)

#### 2. Create Lipsync Video by Text (`create_lipsync_video_by_text`)

Create a lipsync video with text input. Generates audio from the text and animates a digital human avatar to speak it.

**Parameters**:
- `avatar`: Digital human avatar ID. Either this or avatar creation parameters must be provided.
- `avatar_video_url`: URL of a video to create the avatar from.
- `avatar_image_url`: URL of an image to create the avatar from.
- `avatar_video_file`: Local path to a video file to create the avatar from.
- `avatar_image_file`: Local path to an image file to create the avatar from.
- `text`: Text content to be spoken by the avatar. Required.
- `voice`: Voice ID to use for text-to-speech. If not provided, a random voice will be selected automatically.
- `title`: Optional title for the created video.
- `async_mode`: If true, returns task_id immediately. If false, waits for completion and downloads the video. Default is true.
- `output_path`: Where to save the downloaded video if async_mode is false. Default is "output.mp4".

**Notes**:
- For avatar creation, provide exactly ONE of avatar_video_url, avatar_image_url, avatar_video_file, or avatar_image_file.
- If avatar ID is directly provided, these parameters will be ignored.

**Returns**:
- If async_mode is true: task_id for checking status later, selected voice ID, and created_avatar (if applicable)
- If async_mode is false: downloaded video path, task result, selected voice ID, and created_avatar (if applicable)

### Checking Task Status

For tasks run in async mode, you can check their status using the Flyworks API's `/creation/task` endpoint with the task_id returned by the tool.

### Notes

- Job processing may take some time, please be patient
- Video file URLs are temporary, please download and save them promptly
- When using local files, the server will automatically upload them to Flyworks servers
- In sync mode, the tool will wait for the task to complete and automatically download the video
- Maximum allowed wait time for sync mode is 10 minutes (600 seconds)
- Avatar creation through videos usually provides better quality but takes longer
- For quick testing, avatar creation through images is faster but may have lower quality

### Related Links

- [Flyworks AI Open Platform Documentation](https://api.hifly.cc/hifly_en.html)
- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/llms-full.txt)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
