from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import os
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained('facebook/opt-125m')
tokenizer = AutoTokenizer.from_pretrained('facebook/opt-125m')

# Load chat template
template_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('template.jinja')

class ChatRequest(BaseModel):
    messages: list
    tools: list = []

def format_function_call(tool_name: str, arguments: dict) -> str:
    return f"<function_call>{tool_name}\n{json.dumps(arguments, indent=2)}</function_call>"

@app.get("/")
async def root():
    return {"status": "ok", "message": "LLM server is running"}

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    try:
        # Convert messages to a format the model can understand
        messages = []
        for message in request.messages:
            if message["role"] == "user":
                messages.append({"role": "user", "content": message["content"]})
            elif message["role"] == "assistant":
                messages.append({"role": "assistant", "content": message["content"]})
        
        # Format the prompt using the template
        prompt = template.render(
            messages=messages,
            tools=request.tools,
            format_function_call=format_function_call,
            bos_token="",  # Empty string for BOS token
            add_generation_prompt=True  # Add generation prompt at the end
        )
        
        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200,
            num_return_sequences=1,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        response = response.split("Assistant: ")[-1].strip()
        
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1694268190,
            "model": "facebook/opt-125m",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 