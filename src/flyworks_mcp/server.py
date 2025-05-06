import os
import httpx
import time
import asyncio
import random
from typing import Optional, Dict, Any, List, Union, Literal
from mcp.server.fastmcp import FastMCP
import sys
import json
from pathlib import Path

# Initialize MCP server instance
mcp = FastMCP("Flyworks-API")

# Get API key from environment variable
api_key = os.environ.get("FLYWORKS_API_TOKEN")

# Flyworks API base URL (updated to v2)
api_base_url = os.environ.get("FLYWORKS_API_BASE_URL", "https://hfw-api.hifly.cc/api/v2/hifly")

# base path for output files
output_base_path = os.environ.get("FLYWORKS_OUTPUT_BASE_PATH", "./output")

# Default output path for videos
DEFAULT_OUTPUT_PATH = os.path.join(output_base_path, "output.mp4")

def get_auth_headers():
    """Generate authentication headers for API requests"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

async def upload_file(file_path: str) -> Dict[str, Any]:
    """
    Upload a local file to Flyworks server
    
    Args:
        file_path: Path to the local file
        
    Returns:
        Dictionary containing file_id if successful, or error information
    """
    # Get file extension
    file_extension = os.path.splitext(file_path)[1].lstrip('.')
    if not file_extension:
        return {"error": "File has no extension"}
    
    # Get content type based on extension
    content_types = {
        "mp4": "video/mp4",
        "mov": "video/quicktime",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "wav": "audio/wav",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png"
    }
    
    content_type = content_types.get(file_extension.lower())
    if not content_type:
        return {"error": f"Unsupported file extension: {file_extension}"}
    
    try:
        # Step 1: Get upload URL
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/tool/create_upload_url",
                headers=get_auth_headers(),
                json={"file_extension": file_extension},
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"Failed to get upload URL: {response.status_code}",
                    "details": response.json()
                }
            
            upload_data = response.json()
            upload_url = upload_data.get("upload_url")
            content_type = upload_data.get("content_type")
            file_id = upload_data.get("file_id")
            
            if not upload_url or not file_id:
                return {"error": "Invalid response from create_upload_url endpoint"}
            
            # Step 2: Upload file to the URL
            with open(file_path, "rb") as file:
                file_content = file.read()
                
                upload_response = await client.put(
                    upload_url,
                    headers={"Content-Type": content_type},
                    content=file_content
                )
                
                if upload_response.status_code not in [200, 204]:
                    return {
                        "error": f"File upload failed: {upload_response.status_code}",
                        "details": upload_response.text
                    }
                
                return {"file_id": file_id}
                
    except Exception as e:
        return {"error": f"File upload failed: {str(e)}"}

async def wait_for_task_completion(task_id: str, timeout: int = 600, interval: int = 10) -> Dict[str, Any]:
    """
    Wait for a task to complete
    
    Args:
        task_id: ID of the task to wait for
        timeout: Maximum time to wait in seconds
        interval: Polling interval in seconds
        
    Returns:
        Task result or error information
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_base_url}/video/task",
                    headers=get_auth_headers(),
                    params={"task_id": task_id},
                    timeout=30
                )
                
                if response.status_code != 200:
                    return {
                        "error": f"Failed to check task status: {response.status_code}",
                        "details": response.json()
                    }
                
                task_data = response.json()
                status = task_data.get("status")
                
                # Status: 1=Waiting, 2=Processing, 3=Completed, 4=Failed
                if status == 3:  # Completed
                    return task_data
                elif status == 4:  # Failed
                    return {
                        "error": "Task failed",
                        "details": task_data
                    }
                
                # Still processing, wait for next check
                await asyncio.sleep(interval)
                
        except Exception as e:
            return {"error": f"Error checking task status: {str(e)}"}
    
    return {"error": f"Task timed out after {timeout} seconds"}

async def download_video(video_url: str, output_path: str) -> Dict[str, Any]:
    """
    Download a video from URL to a local file
    
    Args:
        video_url: URL of the video to download
        output_path: Where to save the downloaded video
        
    Returns:
        Success message or error information
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=60)
            
            if response.status_code != 200:
                return {
                    "error": f"Video download failed: {response.status_code}",
                    "details": response.text
                }
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return {
                "success": True,
                "message": f"Video downloaded to {output_path}",
                "output_path": output_path
            }
            
    except Exception as e:
        return {"error": f"Video download failed: {str(e)}"}

async def get_voice_list(voice_type: Optional[int] = None) -> Dict[str, Any]:
    """
    Get list of available voices from Flyworks API
    
    Args:
        voice_type: Optional filter for voice type (1=self-cloned, 2=public)
    
    Returns:
        Dictionary containing voice list if successful, or error information
    """
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
    
    try:
        params = {}
        if voice_type is not None:
            params["kind"] = voice_type
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_base_url}/voice/list",
                headers=get_auth_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"Failed to get voice list: {response.status_code}",
                    "details": response.json()
                }
            
            return response.json()
            
    except Exception as e:
        return {"error": f"Failed to get voice list: {str(e)}"}

async def create_avatar(
    video_url: Optional[str] = None,
    image_url: Optional[str] = None,
    video_file: Optional[str] = None,
    image_file: Optional[str] = None,
    title: Optional[str] = None,
    model: int = 2
) -> Dict[str, Any]:
    """
    Create a digital human avatar using video or image
    
    Args:
        video_url: Remote URL of the video file
        image_url: Remote URL of the image file
        video_file: Local path to the video file
        image_file: Local path to the image file
        title: Title for the avatar
        model: Model type, 1: Video 2.0, 2: Video 2.1, default 2
        
    Returns:
        Dictionary containing avatar ID if successful, or error information
    """
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
    
    # Parameter validation
    video_options = sum(1 for x in [video_url, video_file] if x)
    image_options = sum(1 for x in [image_url, image_file] if x)
    
    if video_options + image_options != 1:
        return {"error": "Exactly one of video_url, video_file, image_url, or image_file must be provided"}
    
    # Determine creation method
    create_by_video = video_options > 0
    
    # Prepare payload
    payload = {
        "title": title or "Generated Avatar",
    }
    
    if create_by_video:
        endpoint = f"{api_base_url}/avatar/create_by_video"
        
        if video_file:
            upload_result = await upload_file(video_file)
            if "error" in upload_result:
                return upload_result
            
            file_id = upload_result.get("file_id")
            payload["file_id"] = file_id
        else:
            payload["video_url"] = video_url
    else:
        endpoint = f"{api_base_url}/avatar/create_by_image"
        
        if image_file:
            upload_result = await upload_file(image_file)
            if "error" in upload_result:
                return upload_result
            
            file_id = upload_result.get("file_id")
            payload["file_id"] = file_id
        else:
            payload["image_url"] = image_url
        
        payload["model"] = model
    
    # Create the avatar
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers=get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.json()
                }
            
            response_data = response.json()
            task_id = response_data.get("task_id")
            
            if not task_id:
                return {"error": "No task_id in response", "details": response_data}
            
            # Wait for avatar creation to complete
            avatar_result = await wait_for_avatar_creation(task_id)
            if "error" in avatar_result:
                return avatar_result
            
            return {
                "avatar": avatar_result.get("avatar"),
                "message": f"Avatar created successfully using {'video' if create_by_video else 'image'}"
            }
            
    except httpx.RequestError as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def wait_for_avatar_creation(task_id: str, timeout: int = 600, interval: int = 10) -> Dict[str, Any]:
    """
    Wait for an avatar creation task to complete
    
    Args:
        task_id: ID of the task to wait for
        timeout: Maximum time to wait in seconds
        interval: Polling interval in seconds
        
    Returns:
        Task result or error information
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_base_url}/avatar/task",
                    headers=get_auth_headers(),
                    params={"task_id": task_id},
                    timeout=30
                )
                
                if response.status_code != 200:
                    return {
                        "error": f"Failed to check avatar task status: {response.status_code}",
                        "details": response.json()
                    }
                
                task_data = response.json()
                status = task_data.get("status")
                
                # Status: 1=Waiting, 2=Processing, 3=Completed, 4=Failed
                if status == 3:  # Completed
                    return task_data
                elif status == 4:  # Failed
                    return {
                        "error": "Avatar creation failed",
                        "details": task_data
                    }
                
                # Still processing, wait for next check
                await asyncio.sleep(interval)
                
        except Exception as e:
            return {"error": f"Error checking avatar task status: {str(e)}"}
    
    return {"error": f"Avatar creation timed out after {timeout} seconds"}

@mcp.tool(
    description="""
    Create lipsync video by audio input. The tool will animate a digital human avatar to speak in sync with the provided audio.
    
    Parameters:
    - avatar: Digital human avatar ID. Either this or avatar creation parameters must be provided.
    - avatar_video_url: URL of a video to create the avatar from.
    - avatar_image_url: URL of an image to create the avatar from.
    - avatar_video_file: Local path to a video file to create the avatar from.
    - avatar_image_file: Local path to an image file to create the avatar from.
    - audio_url: Remote URL of the audio file. One of audio_url or audio_file must be provided.
    - audio_file: Local path to the audio file. One of audio_url or audio_file must be provided.
    - title: Optional title for the created video.
    - async_mode: If true, returns task_id immediately. If false, waits for completion and downloads the video. Default is false.
    - output_path: Where to save the downloaded video if async_mode is false. Default is "output.mp4".
    
    Avatar creation: Provide exactly ONE of avatar_video_url, avatar_image_url, avatar_video_file, or avatar_image_file to create a new avatar.
    If avatar ID is directly provided, these parameters will be ignored.
    
    Audio file should be mp3, m4a, or wav format, within 20MB, and between 1 second and 3 minutes.
    
    Returns:
    - If async_mode is true: task_id for checking status later
    - If async_mode is false: downloaded video path and task result
    """
)
async def create_lipsync_video_by_audio(
    avatar: Optional[str] = None,
    avatar_video_url: Optional[str] = None,
    avatar_image_url: Optional[str] = None,
    avatar_video_file: Optional[str] = None,
    avatar_image_file: Optional[str] = None,
    audio_url: Optional[str] = None,
    audio_file: Optional[str] = None,
    title: Optional[str] = None,
    async_mode: bool = False,
    output_path: str = DEFAULT_OUTPUT_PATH
):
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
    
    # Avatar handling
    avatar_created = False
    avatar_options = sum(1 for x in [avatar_video_url, avatar_image_url, avatar_video_file, avatar_image_file] if x)
    
    if not avatar and avatar_options == 0:
        return {"error": "Either avatar ID or avatar creation parameters must be provided"}
    
    if not avatar and avatar_options > 0:
        # Create avatar using provided parameters
        avatar_result = await create_avatar(
            video_url=avatar_video_url,
            image_url=avatar_image_url,
            video_file=avatar_video_file,
            image_file=avatar_image_file,
            title=f"Avatar for {title or 'Lipsync Video'}"
        )
        
        if "error" in avatar_result:
            return avatar_result
        
        avatar = avatar_result.get("avatar")
        avatar_created = True
        
        if not avatar:
            return {"error": "Failed to get avatar ID after creation"}
    
    # Audio parameter validation
    if not audio_url and not audio_file:
        return {"error": "Either audio_url or audio_file must be provided"}
    
    # Prepare payload
    payload = {
        "avatar": avatar,
        "title": title or "Lipsync Video"
    }
    
    # Handle local audio file
    file_id = None
    if audio_file and not audio_url:
        upload_result = await upload_file(audio_file)
        if "error" in upload_result:
            return upload_result
        
        file_id = upload_result.get("file_id")
        payload["file_id"] = file_id
    elif audio_url:
        payload["audio_url"] = audio_url
    
    # Create the lipsync video
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/video/create_by_audio",
                headers=get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.json()
                }
            
            response_data = response.json()
            task_id = response_data.get("task_id")
            
            if not task_id:
                return {"error": "No task_id in response", "details": response_data}
            
            # If async mode, just return the task ID
            if async_mode:
                result = {
                    "task_id": task_id,
                    "message": "Task created successfully. Use task_id to check completion using the /video/task API endpoint.",
                    "async_mode": True
                }
                
                if avatar_created:
                    result["created_avatar"] = avatar
                    
                return result
            
            # If sync mode, wait for completion and download
            task_result = await wait_for_task_completion(task_id)
            if "error" in task_result:
                return task_result
            
            # Get video URL from task result
            video_url = task_result.get("video_Url")
            if not video_url:
                return {"error": "No video URL in task result", "details": task_result}
            
            # Download the video
            download_result = await download_video(video_url, output_path)
            if "error" in download_result:
                return download_result
            
            # Return success response
            result = {
                "async_mode": False,
                "task_id": task_id,
                "task_result": task_result,
                "download_result": download_result
            }
            
            if avatar_created:
                result["created_avatar"] = avatar
                
            return result
            
    except httpx.RequestError as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool(
    description="""
    Create lipsync video by text input. The tool will generate audio from the text and animate a digital human avatar to speak it.
    
    Parameters:
    - avatar: Digital human avatar ID. Either this or avatar creation parameters must be provided.
    - avatar_video_url: URL of a video to create the avatar from.
    - avatar_image_url: URL of an image to create the avatar from.
    - avatar_video_file: Local path to a video file to create the avatar from.
    - avatar_image_file: Local path to an image file to create the avatar from.
    - text: Text content to be spoken by the avatar. Required.
    - voice: Voice ID to use for text-to-speech. If not provided, a random voice will be selected.
    - title: Optional title for the created video.
    - async_mode: If true, returns task_id immediately. If false, waits for completion and downloads the video. Default is false.
    - output_path: Where to save the downloaded video if async_mode is false. Default is "output.mp4".
    
    Avatar creation: Provide exactly ONE of avatar_video_url, avatar_image_url, avatar_video_file, or avatar_image_file to create a new avatar.
    If avatar ID is directly provided, these parameters will be ignored.
    
    Text should be between 1 and 500 characters.
    
    Returns:
    - If async_mode is true: task_id for checking status later, selected voice ID
    - If async_mode is false: downloaded video path, task result, and selected voice ID
    """
)
async def create_lipsync_video_by_text(
    avatar: Optional[str] = None,
    avatar_video_url: Optional[str] = None,
    avatar_image_url: Optional[str] = None,
    avatar_video_file: Optional[str] = None,
    avatar_image_file: Optional[str] = None,
    text: str = "",
    voice: Optional[str] = None,
    title: Optional[str] = None,
    async_mode: bool = False,
    output_path: str = DEFAULT_OUTPUT_PATH
):
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
    
    # Text parameter validation
    if not text:
        return {"error": "text parameter is required"}
    
    # Avatar handling
    avatar_created = False
    avatar_options = sum(1 for x in [avatar_video_url, avatar_image_url, avatar_video_file, avatar_image_file] if x)
    
    if not avatar and avatar_options == 0:
        return {"error": "Either avatar ID or avatar creation parameters must be provided"}
    
    if not avatar and avatar_options > 0:
        # Create avatar using provided parameters
        avatar_result = await create_avatar(
            video_url=avatar_video_url,
            image_url=avatar_image_url,
            video_file=avatar_video_file,
            image_file=avatar_image_file,
            title=f"Avatar for {title or 'Text-driven Lipsync Video'}"
        )
        
        if "error" in avatar_result:
            return avatar_result
        
        avatar = avatar_result.get("avatar")
        avatar_created = True
        
        if not avatar:
            return {"error": "Failed to get avatar ID after creation"}
    
    # If voice is not provided, get a random voice from the voice list
    if not voice:
        # Randomly select a public voice (type=2)
        voice_list_result = await get_voice_list(voice_type=2)
        
        if "error" in voice_list_result:
            return voice_list_result
        
        voices = voice_list_result.get("data", [])
        if not voices:
            return {"error": "No public voices available"}
        
        # Randomly select a public voice
        random_voice = random.choice(voices)
        voice = random_voice.get("voice")
        print(f"Selected voice: {voice}")
        if not voice:
            return {"error": "Failed to get a valid voice ID"}
    
    # Prepare payload
    payload = {
        "avatar": avatar,
        "text": text,
        "voice": voice,
        "title": title or "Text-driven Lipsync Video"
    }
    
    # Create the lipsync video
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/video/create_by_tts",
                headers=get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.json()
                }
            
            response_data = response.json()
            task_id = response_data.get("task_id")
            
            if not task_id:
                return {"error": "No task_id in response", "details": response_data}
            
            # If async mode, just return the task ID
            if async_mode:
                result = {
                    "task_id": task_id,
                    "message": "Task created successfully. Use task_id to check completion using the /video/task API endpoint.",
                    "async_mode": True,
                    "selected_voice": voice
                }
                
                if avatar_created:
                    result["created_avatar"] = avatar
                    
                return result
            
            # If sync mode, wait for completion and download
            task_result = await wait_for_task_completion(task_id)
            if "error" in task_result:
                return task_result
            
            # Get video URL from task result
            video_url = task_result.get("video_Url")
            if not video_url:
                return {"error": "No video URL in task result", "details": task_result}
            
            # Download the video
            download_result = await download_video(video_url, output_path)
            if "error" in download_result:
                return download_result
            
            # Return success response
            result = {
                "async_mode": False,
                "task_id": task_id,
                "task_result": task_result,
                "download_result": download_result,
                "selected_voice": voice
            }
            
            if avatar_created:
                result["created_avatar"] = avatar
                
            return result
            
    except httpx.RequestError as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Start the Flyworks MCP server"""
    if not api_key:
        print("Warning: FLYWORKS_API_TOKEN environment variable not set.", file=os.sys.stderr)
        print("Set it to use the Flyworks API properly.", file=os.sys.stderr)
    
    if "FLYWORKS_API_BASE_URL" not in os.environ:
        print(f"Note: Using default API base URL: {api_base_url}", file=os.sys.stderr)
    
    print("Starting Flyworks MCP server...", file=os.sys.stderr)
    mcp.run()

if __name__ == "__main__":
    main() 