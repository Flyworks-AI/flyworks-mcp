import os
import httpx
from mcp.server.fastmcp import FastMCP
import sys

# Initialize MCP server instance
mcp = FastMCP("Flyworks-API")

# Get API key from environment variable
api_key = os.environ.get("FLYWORKS_API_TOKEN")

# Flyworks API base URL
api_base_url = "https://api.flyworks.ai/api/v1"

def get_auth_headers():
    """Generate authentication headers for API requests"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

@mcp.tool(
    description="""
    Create digital avatar lipsync video. Inputs are a digital avatar video and an audio file, and output is a lipsynced video with the same length of the audio.
    
    Parameters:
    - video_url: URL of the source video, which contains at least 5-second video of a digital avatar.   
    - audio_url: URL of the source audio, which contains the audio to be lipsynced.
    
    Returns:
    - job id and status information. A job id will be returned immediately, and the status can be checked using the inspect_work_status tool.
   
    """
)
async def create_lipsync_video(
    video_url: str = None,
    audio_url: str = None,
):
    
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
        
    # Construct payload based on provided parameters
    payload = {}

    if video_url:
        payload["video_url"] = video_url
    

    if audio_url:
        payload["audio_url"] = audio_url
        
    # Make API request
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/task/create",
                headers=get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code != 200:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response_data
                }
            
            return response_data
    
    except httpx.RequestError as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool(
    description="""
    Query the status of a created job.
    
    Parameters:
    - job_id: ID of the job to query
    
    Returns:
    - Status information of the job
    """
)
async def inspect_job_status(job_id: str):
    
    # API key validation
    if not api_key:
        return {"error": "API key not found. Please set FLYWORKS_API_TOKEN environment variable."}
    
    # job_id validation
    if not job_id:
        return {"error": "job_id is required."}
    
    # Status code descriptions
    status_descriptions = {
        1: "Queuing",
        2: "Processing",
        3: "Completed",
        4: "Failed"
    }
    
    # Make API request
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/task/inspect",
                headers=get_auth_headers(),
                json={"job_id": job_id},
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code != 200:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response_data
                }
            
            # Add status description to the response
            if "status" in response_data and response_data["status"] in status_descriptions:
                response_data["status_description"] = status_descriptions[response_data["status"]]
            
            return response_data
    
    except httpx.RequestError as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Start the Flyworks MCP server"""
    if not api_key:
        print("Warning: FLYWORKS_API_TOKEN environment variable not set.", file=os.sys.stderr)
        print("Set it to use the Flyworks API properly.", file=os.sys.stderr)
    
    print("Starting Flyworks MCP server...", file=os.sys.stderr)
    mcp.run()

if __name__ == "__main__":
    main()
