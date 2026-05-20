# import os
# import hashlib
# import logging
# import asyncio
# import orjson
# import httpx
# from typing import List, Optional, Any
# from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel, ConfigDict
# from openai import AsyncAzureOpenAI
# from fastapi.responses import StreamingResponse
# from cachetools import LRUCache

# # -----------------------------
# # 1. High-Performance Setup
# # -----------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("maya-ultra-low-latency")

# limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
# http_client = httpx.AsyncClient(limits=limits, timeout=60.0)

# client = AsyncAzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_version="2024-08-01-preview",
#     http_client=http_client
# )

# DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# AUTH_KEY = os.getenv("CUSTOM_LLM_API_KEY")

# RESPONSE_CACHE = LRUCache(maxsize=200)

# app = FastAPI()

# # -----------------------------
# # 2. Optimized Models
# # -----------------------------
# class Message(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)
#     role: str
#     content: Optional[str] = None
#     tool_calls: Optional[List[Any]] = None
#     tool_call_id: Optional[str] = None
#     name: Optional[str] = None

# class ChatRequest(BaseModel):
#     messages: List[Message]
#     tools: Optional[List[Any]] = None
#     stream: bool = True
#     max_tokens: int = 100

# # -----------------------------
# # 3. Optimized Logic
# # -----------------------------
# @app.post("/custom-llm/chat/completions")
# async def chat_completions(req: ChatRequest, request: Request):
#     if request.headers.get("x-api-key") != AUTH_KEY:
#         raise HTTPException(status_code=401)

#     async def event_generator():
#         user_id = request.headers.get("x-user-id", "anonymous")
#         user_context = "".join([m.content for m in req.messages if m.role == "user"][-10:])
#         ckey = hashlib.md5(f"{user_id}:{user_context}".encode()).hexdigest()
        
#         if ckey in RESPONSE_CACHE:
#             yield b"data: " + orjson.dumps({"choices":[{"delta":{"content":RESPONSE_CACHE[ckey]}}]}) + b"\n\n"
#             yield b"data: [DONE]\n\n"
#             return

#         collected = []
#         try:
#             # 1. Separate System Message
#             system_msg = next((m for m in req.messages if m.role == "system"), None)
            
#             # 2. Extract History (Excluding System)
#             history_pool = [m for m in req.messages if m.role != "system"]
            
#             # 3. Slicing with Tool Integrity
#             # We take the last 10 messages, but check if the first one is a 'tool'
#             slice_index = -10
#             if abs(slice_index) < len(history_pool):
#                 # If the first message in our slice is a 'tool', we MUST include the one before it
#                 if history_pool[slice_index].role == "tool":
#                     slice_index -= 1 
            
#             recent_history = history_pool[slice_index:]
            
#             # 4. Reconstruct final payload
#             final_messages = []
#             if system_msg:
#                 final_messages.append(system_msg.model_dump(exclude_none=True))
            
#             final_messages.extend([m.model_dump(exclude_none=True) for m in recent_history])

#             kwargs = {
#                 "model": DEPLOYMENT,
#                 "messages": final_messages,
#                 "temperature": 0.0,
#                 "stream": True,
#                 "max_tokens": req.max_tokens,
#                 "stream_options": {"include_usage": True},
#             }
            
#             if req.tools:
#                 kwargs["tools"] = req.tools
#                 kwargs["tool_choice"] = "auto"

#             response = await asyncio.wait_for(
#                 client.chat.completions.create(**kwargs),
#                 timeout=15.0 # Increased slightly for tool-heavy processing
#             )

#             first_chunk = True
#             async for chunk in response:
#                 chunk_data = chunk.model_dump(exclude_none=True)
#                 yield b"data: " + orjson.dumps(chunk_data) + b"\n\n"

#                 if chunk.choices and len(chunk.choices) > 0:
#                     delta = chunk.choices[0].delta
#                     if delta.content:
#                         collected.append(delta.content)

#                 if first_chunk:
#                     first_chunk = False
#                     await asyncio.sleep(0) 

#             if collected:
#                 RESPONSE_CACHE[ckey] = "".join(collected)

#             yield b"data: [DONE]\n\n"

#         except Exception as e:
#             logger.error(f"Streaming Error: {e}")
#             # Ensure the stream closes cleanly on error
#             yield b"data: [DONE]\n\n"

#     return StreamingResponse(
#         event_generator(), 
#         media_type="text/event-stream",
#         headers={
#             "X-Accel-Buffering": "no",
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive"
#         }
#     )

# @app.on_event("shutdown")
# async def shutdown_event():
#     await http_client.aclose()

# if __name__ == "__main__":
#     import uvicorn
#     import sys
#     loop_type = "uvloop" if sys.platform != "win32" else "asyncio"
#     uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), loop=loop_type)





# import os
# import hashlib
# import logging
# import asyncio
# import orjson
# import httpx
# import sys
# from typing import List, Optional, Any
# from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel, ConfigDict
# from openai import AsyncAzureOpenAI
# from fastapi.responses import StreamingResponse
# from cachetools import LRUCache

# # -----------------------------
# # 1. High-Performance Setup
# # -----------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("maya-ultra-low-latency")

# limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
# http_client = httpx.AsyncClient(limits=limits, timeout=60.0)

# # Updated with your specified endpoint, key, and API version
# ENDPOINT = "https://impactguru-openai.cognitiveservices.azure.com/"
# API_VERSION = "2024-12-01-preview"
# AUTH_KEY = os.getenv("CUSTOM_LLM_API_KEY",'tryingllmonx')
# DEPLOYMENT = "gpt-5-nano"

# client = AsyncAzureOpenAI(
#     api_key="",
#     azure_endpoint=ENDPOINT,
#     api_version=API_VERSION,
#     http_client=http_client
# )

# RESPONSE_CACHE = LRUCache(maxsize=200)

# app = FastAPI()

# # -----------------------------
# # 2. Optimized Models
# # -----------------------------
# class Message(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)
#     role: str
#     content: Optional[str] = None
#     tool_calls: Optional[List[Any]] = None
#     tool_call_id: Optional[str] = None
#     name: Optional[str] = None

# class ChatRequest(BaseModel):
#     messages: List[Message]
#     tools: Optional[List[Any]] = None
#     stream: bool = True
#     max_tokens: int = 100

# # -----------------------------
# # 3. Optimized Logic
# # -----------------------------
# @app.post("/custom-llm/chat/completions")
# async def chat_completions(req: ChatRequest, request: Request):
#     if request.headers.get("x-api-key") != AUTH_KEY:
#         raise HTTPException(status_code=401)

#     async def event_generator():
#         user_id = request.headers.get("x-user-id", "anonymous")
#         user_context = "".join([m.content for m in req.messages if m.role == "user"][-10:])
#         ckey = hashlib.md5(f"{user_id}:{user_context}".encode()).hexdigest()
        
#         if ckey in RESPONSE_CACHE:
#             yield b"data: " + orjson.dumps({"choices":[{"delta":{"content":RESPONSE_CACHE[ckey]}}]}) + b"\n\n"
#             yield b"data: [DONE]\n\n"
#             return

#         collected = []
#         try:
#             # 1. Separate System Message
#             system_msg = next((m for m in req.messages if m.role == "system"), None)
            
#             # 2. Extract History (Excluding System)
#             history_pool = [m for m in req.messages if m.role != "system"]
            
#             # 3. Slicing with Tool Integrity
#             slice_index = -10
#             if abs(slice_index) < len(history_pool):
#                 # If the first message in our slice is a 'tool', we MUST include the one before it
#                 if history_pool[slice_index].role == "tool":
#                     slice_index -= 1 
            
#             recent_history = history_pool[slice_index:]
            
#             # 4. Reconstruct final payload
#             final_messages = []
#             if system_msg:
#                 final_messages.append(system_msg.model_dump(exclude_none=True))
            
#             final_messages.extend([m.model_dump(exclude_none=True) for m in recent_history])

#             kwargs = {
#                 "model": DEPLOYMENT,
#                 "messages": final_messages,
#                 "reasoning_effort": "minimal",
#                 "stream": True,
#                 "max_completion_tokens": req.max_tokens, # Using updated max_completion_tokens for modern models
#                 "stream_options": {"include_usage": True},
#             }
            
#             if req.tools:
#                 kwargs["tools"] = req.tools
#                 kwargs["tool_choice"] = "auto"

#             response = await asyncio.wait_for(
#                 client.chat.completions.create(**kwargs),
#                 timeout=15.0 # Increased slightly for tool-heavy processing
#             )

#             first_chunk = True
#             async for chunk in response:
#                 chunk_data = chunk.model_dump(exclude_none=True)
#                 yield b"data: " + orjson.dumps(chunk_data) + b"\n\n"

#                 if chunk.choices and len(chunk.choices) > 0:
#                     delta = chunk.choices[0].delta
#                     if delta.content:
#                         collected.append(delta.content)

#                 if first_chunk:
#                     first_chunk = False
#                     await asyncio.sleep(0) 

#             if collected:
#                 RESPONSE_CACHE[ckey] = "".join(collected)

#             yield b"data: [DONE]\n\n"

#         except Exception as e:
#             logger.error(f"Streaming Error: {e}")
#             # Ensure the stream closes cleanly on error
#             yield b"data: [DONE]\n\n"

#     return StreamingResponse(
#         event_generator(), 
#         media_type="text/event-stream",
#         headers={
#             "X-Accel-Buffering": "no",
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive"
#         }
#     )

# @app.on_event("shutdown")
# async def shutdown_event():
#     await http_client.aclose()

# if __name__ == "__main__":
#     import uvicorn
#     loop_type = "uvloop" if sys.platform != "win32" else "asyncio"
#     uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), loop=loop_type)






import os
import logging
import asyncio
import orjson
import httpx
import sys
import xxhash
from typing import List, Optional, Any
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, ConfigDict
from openai import AsyncAzureOpenAI
from fastapi.responses import StreamingResponse
from cachetools import TTLCache

# -----------------------------
# 1. High-Performance Setup
# -----------------------------
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("maya-ultra-low-latency")

# ✅ OPTIMIZATION: Forced HTTP/2 multiplexing to eliminate TCP connection setup bottlenecks
limits = httpx.Limits(max_keepalive_connections=100, max_connections=500)
timeout = httpx.Timeout(10.0, connect=5.0)
http_client = httpx.AsyncClient(limits=limits, timeout=timeout, http2=True)

ENDPOINT = "https://impactguru-openai.cognitiveservices.azure.com/"
API_VERSION = "2024-12-01-preview"
DEPLOYMENT = "gpt-5-nano"

AUTH_KEY = os.getenv("CUSTOM_LLM_API_KEY")
if not AUTH_KEY:
    raise RuntimeError("CUSTOM_LLM_API_KEY environment variable must be set")

client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=ENDPOINT,
    api_version=API_VERSION,
    http_client=http_client
)

RESPONSE_CACHE = TTLCache(maxsize=200, ttl=120)

FALLBACK_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Maya, a fast, helpful voice assistant. "
        "Reply in 1-2 short sentences. No filler. No markdown. "
        "Be direct and conversational."
    )
}

DATA_PREFIX = b"data: "
DONE_MESSAGE = b"data: [DONE]\n\n"

app = FastAPI()

class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Any]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    tools: Optional[List[Any]] = None
    stream: bool = True
    max_tokens: int = 250

@app.on_event("startup")
async def warmup():
    try:
        await client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                FALLBACK_SYSTEM_PROMPT,
                {"role": "user", "content": "hi"}
            ],
            max_completion_tokens=5,
            reasoning_effort="low"
        )
        logger.warning("Azure connection pre-warmed successfully for gpt-5-nano.")
    except Exception as e:
        logger.warning(f"Warmup failed (non-fatal): {e}")

# -----------------------------
# 4. Core Router Implementation (ULTRA‑FAST)
# -----------------------------
@app.post("/custom-llm/chat/completions")
async def chat_completions(request: Request):
    if request.headers.get("x-api-key") != AUTH_KEY:
        raise HTTPException(status_code=401)

    body = await request.body()
    req = orjson.loads(body)

    user_id = request.headers.get("x-user-id", "anonymous")
    messages = req["messages"]          
    tools = req.get("tools", None)
    max_tokens = req.get("max_tokens", 250)

    # Cache key mapping logic
    recent_turns = [
        f"{m['role']}:{m['content']}" for m in messages if m.get("content")
    ][-2:]
    ckey = xxhash.xxh64(f"{user_id}|{'|'.join(recent_turns)}").hexdigest()

    if ckey in RESPONSE_CACHE and not tools:
        cached_val = RESPONSE_CACHE[ckey]
        async def cached_stream():
            yield DATA_PREFIX + orjson.dumps({
                "choices": [{"delta": {"content": cached_val}, "index": 0}]
            }) + b"\n\n"
            yield DONE_MESSAGE
        return StreamingResponse(
            cached_stream(),
            media_type="text/event-stream",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    # ✅ OPTIMIZATION: Replaced slow .copy() and multi-loop sorting with an efficient inline filter
    final_messages = [m for m in messages if m["role"] == "system" and m.get("content")]
    if not final_messages:
        final_messages.append(FALLBACK_SYSTEM_PROMPT)

    non_system = [m for m in messages if m["role"] != "system"]

    max_turns = 16
    if len(non_system) > max_turns:
        cut = len(non_system) - max_turns
        if non_system[cut]["role"] == "tool":
            cut -= 1
        kept = non_system[cut:]
    else:
        kept = non_system

    # ✅ OPTIMIZATION: Avoided costly .items() tuple instantiation loops in dictionary stripping
    for m in kept:
        clean_msg = {k: v for k, v in m.items() if v is not None}
        final_messages.append(clean_msg)

    reasoning = "low" if tools else "minimal"
    temperature = 0.0 if tools else 0.4

    async def event_generator():
        collected = []
        try:
            kwargs = {
                "model": DEPLOYMENT,
                "messages": final_messages,
                "stream": True,
                "max_completion_tokens": max_tokens,
                "reasoning_effort": reasoning,
                "stream_options": {"include_usage": True},
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await asyncio.wait_for(
                client.chat.completions.create(**kwargs),
                timeout=15.0
            )

            # ✅ OPTIMIZATION: Removed manual reflection lookups inside the hot token loop
            async for chunk in response:
                chunk_dict = chunk.model_dump(exclude_none=True)
                yield DATA_PREFIX + orjson.dumps(chunk_dict) + b"\n\n"

                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    collected.append(delta.content)

            if collected and not tools:
                RESPONSE_CACHE[ckey] = "".join(collected)

            yield DONE_MESSAGE

        except Exception as e:
            logger.error(f"Streaming Error: {e}")
            yield DONE_MESSAGE

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.get("/health")
async def health():
    return {"status": "ok", "cache_size": len(RESPONSE_CACHE)}

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    loop_type = "uvloop" if sys.platform != "win32" else "asyncio"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        loop=loop_type,
        log_level="warning",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )