from typing import Literal, List

import dspy
from pydantic import BaseModel


class BaseAgent( dspy.Module ):
    def __init__( self, client, scratchpad ):
        super().__init__()
        self.client = client
        self.scratchpad = scratchpad


class ScratchpadEntry(BaseModel):
    entry_type: str
    entry_data: dict | list


class ToolResponse(BaseModel):
    """
    user_message: message to display directly to the user.
    tool_response: data to present to the language model, usually json.
    scratchpad: A scratchpad entry that can be rendered for the user
    """
    user_message: str = ''
    tool_response: str = ''
    scratchpad: ScratchpadEntry | None = None
    return_to_client: bool = False


class Message( BaseModel ):
    role: Literal['system', 'assistant', 'user', 'tool', 'scratchpad']
    content: str
    scratchpad: ScratchpadEntry | None = None


class History( BaseModel ):
    conversation: List[ Message ]

    def handle_message( self, message: Message ):
        self.conversation.append( message )

    def handle_tool_response( self, message: ToolResponse ):
        message = Message(
            role = 'tool',
            content = message.user_message + message.tool_response
        )
        self.handle_message( message )

        if message.scratchpad is not None:
            message = Message(
                role = 'scratchpad',
                content = '',
                scratchpad = message.scratchpad
            )
            self.handle_message( message )

    def format_history( self ):
        # Format conversation for DSPy modules
        formatted_history = []
        
        for message in self.conversation:
            if message.role == "system":
                formatted_history.append({"role": "system", "content": message.content})
            elif message.role == "user":
                formatted_history.append({"role": "user", "content": message.content})
            elif message.role == "assistant":
                formatted_history.append({"role": "assistant", "content": message.content})
            elif message.role == "tool":
                formatted_history.append({"role": "function", "content": message.content})
        
        return formatted_history

    @property
    def text( self ):
        # Concatenate all messages into a single string for text-based LLMs
        outputs = ""
        for entry in self.conversation:
            role = entry.role
            content = entry.content
            outputs += f"{role}: {content}\n\n"
        return outputs
