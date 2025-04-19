# Flyworks MCP: Free & Fast Zeroshot Lipsync Tool
<div align="left">
  <a href="https://discord.gg/YappgYYYFD" target="_blank">
    <img src="https://img.shields.io/badge/Flyworks-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
  </a>
  <a href="https://x.com/flyworks_ai" target="_blank">
    <img src="https://img.shields.io/badge/Flyworks%20AI-%23000000.svg?style=for-the-badge&logo=X&logoColor=white" alt="Flyworks AI">
  </a>
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
- More features coming soon...

### Requirements

- Python 3.8+
- Dependencies: `httpx`, `mcp[cli]`

### Installation

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

### Configuration

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

> **Note:** We offer free trial access to our tool with the token `2aeda3bcefac46a3`. However, please be aware that the daily quota for this free access is limited. Additionally, the generated videos will be watermarked and restricted to a duration of 45 seconds. For full access, please contact us at bd@flyworks.ai to acquire your token.

### Usage

#### Running the Server

Run the `server.py` file directly:

```bash
python server.py
```

#### Integration with Claude or Other MCP Clients

##### Using in Claude Desktop

1. Install the server using the `mcp` tool:
   ```bash
   mcp install /path/to/server.py
   ```

2. Add server configuration in Claude Desktop's configuration file:
   Edit the `claude_desktop_config.json` file and add the following:

   ```json
   {
     "mcpServers": {
       "flyworks": {
         "command": "python",
         "args": ["/path/to/server.py"],
         "env": {
           "FLYWORKS_API_TOKEN": "your_api_token_here"
         }
       }
     }
   }
   ```

##### Using in Cursor

Add the following to the Cursor MCP configuration:

```json
{
  "mcpServers": {
    "flyworks": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "FLYWORKS_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### Tool Description

#### 1. Create Lipsync Video (`create_lipsync_video`)

Create a digital avatar lipsync video. Inputs are a digital avatar video and an audio file, and the output is a lipsynced video with the same length as the audio.

**Parameters**:
- `video_url`: Video file URL, required for video-driven creation, supports mp4, mov formats
- `audio_url`: Audio file URL, required for audio-driven creation, supports mp3, m4a, wav formats

**Return**:
- `job_id`: The job ID of the video creation

#### 2. Inspect Job Status (`inspect_job_status`)

Query the video creation status. Returns the video URL for download if successful.

**Parameters**:
- `job_id`: Job ID, required. Returned when creating a work.

**Response Parameters**:
- `message`: String, error message returned when failed
- `code`: Int, error code when failed
- `status`: Int, job status, 1: Waiting, 2: Processing, 3: Completed, 4: Failed
- `video_Url`: URL, the URL of the generated video. This is a temporary URL, please save it promptly. The URL contains query parameters, ensure compatibility when downloading.
- `duration`: Int, duration of the video in seconds
- `request_id`: String, request code

### Notes

- Job processing may take some time, please be patient
- Video file URLs are temporary, please download and save them promptly

### Related Links

- [Flyworks AI Open Platform Documentation](https://api.lingverse.co/hifly.html)
- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/llms-full.txt)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
