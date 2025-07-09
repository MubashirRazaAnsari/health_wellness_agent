"""
Streaming utilities for real-time agent responses with improved formatting.
"""
from typing import AsyncGenerator, Dict, Any, AsyncIterator
import json
import asyncio
import re
from context import UserSessionContext
from agent import HealthWellnessAgent

class StreamHandler:
    """Handles streaming responses from the agent with improved formatting."""

    def __init__(self):
        self.sentence_endings = re.compile(r'[.!?]+\s*')
        self.numbered_list_pattern = re.compile(r'^\d+\.\s*')
        self.bullet_point_pattern = re.compile(r'^\*\s*')
        self.markdown_header_pattern = re.compile(r'^#{1,6}\s+')
        
    async def stream_response(
        self,
        agent: HealthWellnessAgent,
        user_input: str,
        context: UserSessionContext
    ) -> AsyncGenerator[str, None]:
        """
        Stream the agent's response in real-time with proper formatting.
        
        Args:
            agent: The HealthWellnessAgent instance
            user_input: The user's message
            context: The user's session context
            
        Yields:
            Properly formatted response chunks
        """
        try:
            # Create the response iterator
            response_iterator = await agent.get_streaming_response(user_input, context)
            if not response_iterator:
                yield "I apologize, but I'm having trouble generating a response. Please try again."
                return

            buffer = ""
            last_chunk_time = asyncio.get_event_loop().time()
            
            # Process chunks as they arrive
            async for chunk in response_iterator:
                current_time = asyncio.get_event_loop().time()
                
                if not chunk:  # Skip empty chunks
                    continue
                    
                if isinstance(chunk, dict):
                    # Handle tool calls and their results
                    if "tool_call" in chunk:
                        if buffer.strip():
                            yield self._format_and_flush_buffer(buffer)
                            buffer = ""
                        yield f"\n\n🔧 **Using {chunk['tool_call']}...**\n\n"
                        
                    elif "tool_result" in chunk:
                        if buffer.strip():
                            yield self._format_and_flush_buffer(buffer)
                            buffer = ""
                        # Format tool results nicely
                        result = chunk["tool_result"]
                        formatted_result = self._format_tool_result(result)
                        yield f"\n\n📊 **Results:**\n\n{formatted_result}\n\n"
                        
                elif isinstance(chunk, str) and chunk.strip():
                    # Add chunk to buffer
                    buffer += chunk
                    
                    # Check if we should flush the buffer
                    should_flush = self._should_flush_buffer(buffer, current_time - last_chunk_time)
                    
                    if should_flush:
                        formatted_chunk = self._format_and_flush_buffer(buffer)
                        if formatted_chunk:
                            yield formatted_chunk
                        buffer = ""
                        last_chunk_time = current_time

            # Flush any remaining content
            if buffer.strip():
                final_chunk = self._format_and_flush_buffer(buffer)
                if final_chunk:
                    yield final_chunk

        except Exception as e:
            error_msg = f"Streaming error: {str(e)}"
            print(error_msg)
            yield "\n\n❌ I apologize, but I encountered an error while processing your request. Please try again.\n\n"

    def _should_flush_buffer(self, buffer: str, time_since_last: float) -> bool:
        """Determine if buffer should be flushed based on content and timing."""
        if not buffer.strip():
            return False
            
        # Flush on complete sentences
        if self.sentence_endings.search(buffer):
            return True
            
        # Flush on numbered lists
        if self.numbered_list_pattern.search(buffer.strip()):
            return True
            
        # Flush on bullet points
        if self.bullet_point_pattern.search(buffer.strip()):
            return True
            
        # Flush on markdown headers
        if self.markdown_header_pattern.search(buffer.strip()):
            return True
            
        # Flush on double line breaks (paragraph breaks)
        if '\n\n' in buffer:
            return True
            
        # Flush if buffer is getting too long
        if len(buffer) > 200:
            return True
            
        # Flush if there's been a pause in streaming
        if time_since_last > 0.5:  # 500ms pause
            return True
            
        return False

    def _format_and_flush_buffer(self, buffer: str) -> str:
        """Format the buffer content and return formatted string."""
        if not buffer.strip():
            return ""
            
        # Clean up the buffer
        content = buffer.strip()
        
        # Handle different content types
        if self.numbered_list_pattern.match(content):
            return self._format_numbered_item(content)
        elif self.bullet_point_pattern.match(content):
            return self._format_bullet_point(content)
        elif self.markdown_header_pattern.match(content):
            return self._format_header(content)
        else:
            return self._format_paragraph(content)

    def _format_numbered_item(self, content: str) -> str:
        """Format numbered list items."""
        # Ensure proper spacing around numbered items
        if not content.endswith('\n'):
            content += '\n'
        return f"\n{content}\n"

    def _format_bullet_point(self, content: str) -> str:
        """Format bullet points."""
        if not content.endswith('\n'):
            content += '\n'
        return f"{content}\n"

    def _format_header(self, content: str) -> str:
        """Format markdown headers."""
        if not content.endswith('\n'):
            content += '\n'
        return f"\n{content}\n"

    def _format_paragraph(self, content: str) -> str:
        """Format regular paragraphs."""
        # Split on sentence boundaries and rejoin with proper spacing
        sentences = self.sentence_endings.split(content)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Add the sentence
                formatted_sentences.append(sentence.strip())
                
                # Add punctuation back if it was split
                if i < len(sentences) - 1:
                    # Find the punctuation that was used to split
                    punctuation_match = self.sentence_endings.search(content[len(''.join(sentences[:i+1])):])
                    if punctuation_match:
                        formatted_sentences[-1] += punctuation_match.group().strip()
        
        if formatted_sentences:
            # Join sentences and add proper paragraph spacing
            result = ' '.join(formatted_sentences)
            if not result.endswith('\n'):
                result += '\n\n'
            return result
        
        return content + '\n\n'

    def _format_tool_result(self, result: Any) -> str:
        """Format tool results for better display."""
        try:
            if isinstance(result, str):
                return result
            
            if isinstance(result, dict):
                formatted_parts = []
                for key, value in result.items():
                    if value:  # Only show non-empty values
                        # Format key as title case
                        formatted_key = key.replace('_', ' ').title()
                        formatted_parts.append(f"• **{formatted_key}:** {value}")
                
                return '\n'.join(formatted_parts)
            
            if isinstance(result, list):
                formatted_items = []
                for i, item in enumerate(result, 1):
                    if isinstance(item, dict):
                        formatted_items.append(f"{i}. {self._format_tool_result(item)}")
                    else:
                        formatted_items.append(f"{i}. {item}")
                
                return '\n'.join(formatted_items)
                
            return str(result)
            
        except Exception as e:
            print(f"Error formatting tool result: {e}")
            return str(result)

    @staticmethod
    def format_tool_result(result: Dict[str, Any]) -> str:
        """Static method for formatting tool results (backward compatibility)."""
        handler = StreamHandler()
        return handler._format_tool_result(result)


class ImprovedAsyncResponseIterator:
    """Enhanced async iterator for streaming responses with better formatting."""
    
    def __init__(self, client, messages, model, config):
        """Initialize the async iterator."""
        self.client = client
        self.messages = messages
        self.model = model
        self.config = config
        self.current_tool = None
        self._queue = asyncio.Queue()
        self._done = False
        self._started = False
        self._buffer = ""
        
    async def _process_chunks(self):
        """Process the completion chunks with improved buffering."""
        try:
            # Create completion with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 500),
                stream=True
            )
            
            # Process each chunk
            for chunk in response:
                if not chunk or not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                # Handle function calls
                if hasattr(delta, 'function_call') and delta.function_call:
                    if not self.current_tool:
                        self.current_tool = delta.function_call.name
                        await self._queue.put({"tool_call": self.current_tool})
                
                # Handle content with improved buffering
                if hasattr(delta, 'content') and delta.content:
                    self._buffer += delta.content
                    
                    # Send chunks when we have complete thoughts
                    if self._should_send_chunk():
                        await self._queue.put(self._buffer)
                        self._buffer = ""
                    
            # Send any remaining content
            if self._buffer:
                await self._queue.put(self._buffer)
                
            # Mark as done
            self._done = True
            
        except Exception as e:
            print(f"Stream processing error: {str(e)}")
            await self._queue.put(f"Error: {str(e)}")
            self._done = True
    
    def _should_send_chunk(self) -> bool:
        """Determine if current buffer should be sent."""
        if len(self._buffer) < 10:  # Wait for minimum content
            return False
            
        # Send on sentence endings
        if re.search(r'[.!?]\s', self._buffer):
            return True
            
        # Send on line breaks
        if '\n' in self._buffer:
            return True
            
        # Send on numbered lists
        if re.search(r'\d+\.\s', self._buffer):
            return True
            
        # Send when buffer gets long
        if len(self._buffer) > 100:
            return True
            
        return False
    
    def __aiter__(self):
        """Return self as async iterator."""
        return self
    
    async def __anext__(self):
        """Get next chunk from the stream."""
        try:
            # Start processing if not started
            if not self._started:
                self._started = True
                asyncio.create_task(self._process_chunks())
            
            # Get next chunk with appropriate timeout
            try:
                chunk = await asyncio.wait_for(self._queue.get(), timeout=0.2)
                return chunk
            except asyncio.TimeoutError:
                if self._done and self._queue.empty():
                    raise StopAsyncIteration
                return ""  # Return empty chunk and continue
                
        except Exception as e:
            print(f"Stream iteration error: {str(e)}")
            raise StopAsyncIteration 