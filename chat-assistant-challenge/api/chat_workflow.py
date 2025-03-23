import json
from datetime import date

import dspy
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

from agents.RouterAgent import RootRouterAgent
from agents.BaseAgent import ToolResponse

async def step_conversation(conversation, today: "date"):
    """
    Process the conversation and generate the next response using the router agent.
    
    Args:
        conversation: The conversation history
        today: Today's date
    
    Returns:
        The response from the router agent
    """
    # Get the latest user message
    latest_message = conversation.conversation[-1]
    
    if latest_message.role != "user":
        return "I'm waiting for your input. How can I help you today?"
    
    # Get client and scratchpad from the conversation
    client = latest_message.client if hasattr(latest_message, "client") else None
    scratchpad = []
    
    # Initialize router agent
    router = RootRouterAgent(client, scratchpad)
    
    # Format today's date
    today_str = today.strftime("%Y-%m-%d") if today else None
    
    # Get response from router agent
    response = await router.forward(conversation, latest_message.content, today_str)
    
    # If the response is a ToolResponse object, return it directly
    if isinstance(response, ToolResponse):
        return response
    
    # If it's a dictionary with a response key, return that
    if isinstance(response, dict) and "response" in response:
        return response["response"]
    
    # Default response if nothing else is returned
    return "I'm not sure how to help with that. You can ask me to view your shifts, request time off, or trade shifts."


async def handle_response(
    client,
    conversation,
    scratchpad,
    response_body
) -> bool:
    """
    Handle the response from a tool or LLM and update the conversation.
    
    Args:
        client: The Humanity API client
        conversation: The conversation history
        scratchpad: The scratchpad for storing intermediate data
        response_body: The response body from the tool or LLM
    
    Returns:
        Boolean indicating if the response should be returned to the client
    """
    # If response is already a ToolResponse, process it
    if isinstance(response_body, ToolResponse):
        # Add the user-facing message to the conversation
        if response_body.user_message:
            conversation.handle_message({
                "role": "assistant",
                "content": response_body.user_message
            })
        
        # Update the scratchpad if applicable
        if response_body.scratchpad:
            scratchpad.append(response_body.scratchpad)
        
        # Return whether this response should be sent to the client
        return response_body.return_to_client
    
    # If response is a string, add it directly as an assistant message
    if isinstance(response_body, str):
        conversation.handle_message({
            "role": "assistant",
            "content": response_body
        })
        return True
    
    # If response is a dictionary with specific format
    if isinstance(response_body, dict):
        # Check if there's a tool call in the response
        if "tool_calls" in response_body:
            # Process tool calls
            for tool_call in response_body["tool_calls"]:
                # Add the tool call to the conversation
                conversation.handle_message({
                    "role": "assistant",
                    "content": f"Calling tool: {tool_call['function']['name']}"
                })
                
                # Call the specified function (this would require function mapping logic)
                # For now, just add a placeholder response
                conversation.handle_message({
                    "role": "tool",
                    "content": f"Tool response for {tool_call['function']['name']}"
                })
            
            return True
        
        # If there's a text response
        if "text" in response_body:
            conversation.handle_message({
                "role": "assistant",
                "content": response_body["text"]
            })
            return True
    
    # Default: Add the response as a string and return to client
    conversation.handle_message({
        "role": "assistant",
        "content": str(response_body)
    })
    return True