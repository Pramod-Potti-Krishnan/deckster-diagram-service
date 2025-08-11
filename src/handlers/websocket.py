"""
WebSocket handler for Deckster.
"""
print("[DEBUG] Starting websocket.py imports")
import json
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List
from fastapi import WebSocket

print("[DEBUG] Importing logger")
from src.utils.logger import setup_logger

print("[DEBUG] Importing agents")
from src.agents.intent_router import IntentRouter
from src.agents.director import DirectorAgent
from src.agents.content_orchestrator import ContentOrchestrator

print("[DEBUG] Importing utils")
from src.utils.session_manager import SessionManager
from src.utils.message_packager import MessagePackager
from src.utils.streamlined_packager import StreamlinedMessagePackager

print("[DEBUG] Importing storage and models")
from src.storage.supabase import get_supabase_client
from src.models.agents import UserIntent, StateContext
from src.models.websocket_messages import StreamlinedMessage

print("[DEBUG] Importing workflows and settings")
from src.workflows.state_machine import WorkflowOrchestrator
from config.settings import get_settings

print("[DEBUG] Setting up logger")
logger = setup_logger(__name__)
print("[DEBUG] websocket.py imports complete")


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""
    
    def __init__(self):
        """Initialize handler components."""
        print("[DEBUG WebSocketHandler] Starting __init__")
        logger.info("Initializing WebSocketHandler...")
        
        # Get settings
        print("[DEBUG WebSocketHandler] Getting settings")
        self.settings = get_settings()
        print(f"[DEBUG WebSocketHandler] Settings loaded: streamlined={self.settings.USE_STREAMLINED_PROTOCOL}")
        logger.info(f"Settings loaded: streamlined={self.settings.USE_STREAMLINED_PROTOCOL}, percentage={self.settings.STREAMLINED_PROTOCOL_PERCENTAGE}")
        
        # Initialize Supabase client
        print("[DEBUG WebSocketHandler] Initializing Supabase client")
        try:
            self.supabase = get_supabase_client()
            print("[DEBUG WebSocketHandler] Supabase client created")
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            print(f"[DEBUG WebSocketHandler] Failed to initialize Supabase: {str(e)}")
            logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
            raise
        
        # Initialize components
        print("[DEBUG WebSocketHandler] Initializing components")
        logger.info("Initializing handler components...")
        
        print("[DEBUG WebSocketHandler] Creating IntentRouter")
        self.intent_router = IntentRouter()
        
        print("[DEBUG WebSocketHandler] Creating DirectorAgent")
        self.director = DirectorAgent()
        
        print("[DEBUG WebSocketHandler] Creating SessionManager")
        self.sessions = SessionManager(self.supabase)
        
        print("[DEBUG WebSocketHandler] Creating MessagePackager")
        self.packager = MessagePackager()
        
        print("[DEBUG WebSocketHandler] Creating StreamlinedMessagePackager")
        self.streamlined_packager = StreamlinedMessagePackager()
        
        print("[DEBUG WebSocketHandler] Creating WorkflowOrchestrator")
        self.workflow = WorkflowOrchestrator()
        
        print("[DEBUG WebSocketHandler] Creating ContentOrchestrator for content generation")
        self.content_orchestrator = None  # Will be initialized when needed
        
        print("[DEBUG WebSocketHandler] All components initialized")
        logger.info("WebSocketHandler initialized successfully with streamlined protocol: %s", 
                   self.settings.USE_STREAMLINED_PROTOCOL)
    
    def _should_use_streamlined(self, session_id: str) -> bool:
        """
        Determine if this session should use streamlined protocol.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if streamlined protocol should be used
        """
        # If feature is disabled globally, always use old protocol
        if not self.settings.USE_STREAMLINED_PROTOCOL:
            return False
        
        # If percentage is 100, always use streamlined
        if self.settings.STREAMLINED_PROTOCOL_PERCENTAGE >= 100:
            return True
        
        # If percentage is 0, never use streamlined
        if self.settings.STREAMLINED_PROTOCOL_PERCENTAGE <= 0:
            return False
        
        # Use session ID for consistent A/B testing
        # Hash the session ID to get a number between 0-99
        hash_value = hash(session_id) % 100
        return hash_value < self.settings.STREAMLINED_PROTOCOL_PERCENTAGE
    
    async def _send_messages(self, websocket: WebSocket, messages: List[StreamlinedMessage]):
        """
        Send multiple streamlined messages with small delays.
        
        Args:
            websocket: WebSocket connection
            messages: List of streamlined messages to send
        """
        for i, message in enumerate(messages):
            # Use model_dump with mode='json' for proper serialization
            message_data = message.model_dump(mode='json')
            logger.debug(f"Sending message {i+1}/{len(messages)}: {message_data.get('type')}")
            await websocket.send_json(message_data)
            
            # Add small delay between messages for better UX
            if i < len(messages) - 1:
                await asyncio.sleep(0.1)
    
    async def send_message(self, message: Dict[str, Any]):
        """
        Send a message through the current WebSocket connection.
        Used by Director OUT for progressive updates.
        """
        logger.info(f"[DEBUG WebSocketHandler] send_message called with type: {message.get('type', 'unknown')}")
        
        if hasattr(self, 'current_websocket'):
            logger.info(f"[DEBUG WebSocketHandler] Has current_websocket attribute: {self.current_websocket is not None}")
            if self.current_websocket:
                try:
                    await self.current_websocket.send_json(message)
                    logger.info(f"[DEBUG WebSocketHandler] Successfully sent {message['type']} message")
                except Exception as e:
                    logger.error(f"[DEBUG WebSocketHandler] Failed to send message: {e}", exc_info=True)
            else:
                logger.error("[DEBUG WebSocketHandler] current_websocket is None")
        else:
            logger.error("[DEBUG WebSocketHandler] No current_websocket attribute")
    
    async def handle_connection(self, websocket: WebSocket, session_id: str, user_id: str):
        """
        Handle a WebSocket connection for a session.
        
        Args:
            websocket: The WebSocket connection
            session_id: The session ID from query parameter
            user_id: The user ID from query parameter
        """
        print(f"[DEBUG handle_connection] Started with session_id={session_id}, user_id={user_id}")
        
        try:
            # Store user_id and websocket for use in other methods
            self.current_user_id = user_id
            self.current_websocket = websocket
            print(f"[DEBUG handle_connection] Set current_user_id={self.current_user_id}")
            logger.info(f"[DEBUG WebSocketHandler] WebSocket connection stored: {self.current_websocket is not None}")
        
            print("[DEBUG handle_connection] About to log info message")
            logger.info(f"Starting handle_connection for user: {user_id}, session: {session_id}")
            print("[DEBUG handle_connection] Logger info called successfully")
            
            # Get or create session with user_id
            print("[DEBUG handle_connection] About to get_or_create session")
            try:
                session = await self.sessions.get_or_create(session_id, user_id)
                print(f"[DEBUG handle_connection] Session created/retrieved: state={session.current_state}")
                logger.info(f"Session {session_id} initialized for user {user_id} with state: {session.current_state}")
            except Exception as session_error:
                print(f"[DEBUG handle_connection] Session error: {str(session_error)}")
                logger.error(f"Failed to create/get session {session_id} for user {user_id}: {str(session_error)}", exc_info=True)
                raise  # Re-raise the exception to properly handle the error
            
            # Send initial greeting if new session
            if session.current_state == "PROVIDE_GREETING":
                logger.info(f"Session {session_id} is new, sending greeting")
                try:
                    await self._send_greeting(websocket, session)
                    logger.info(f"Greeting sent successfully for session {session_id}")
                except Exception as greeting_error:
                    logger.error(f"Failed to send greeting for session {session_id}: {str(greeting_error)}", exc_info=True)
                    raise
            else:
                logger.info(f"Session {session_id} already in state: {session.current_state}, no greeting needed")
            
            # Main message loop
            logger.info(f"Entering message loop for session {session_id}")
            while True:
                # Receive message
                logger.debug(f"Waiting for message from session {session_id}")
                data = await websocket.receive_text()
                logger.debug(f"Received raw data: {data[:100]}...")  # First 100 chars
                message = json.loads(data)
                logger.info(f"Received message for session {session_id}: type={message.get('type')}, data keys={list(message.get('data', {}).keys())}")
                
                # Process message
                await self._handle_message(websocket, session, message)
                
        except Exception as e:
            print(f"[DEBUG handle_connection] Inner exception: {str(e)}")
            logger.error(f"Error in WebSocket handler for session {session_id}: {str(e)}", exc_info=True)
            # Don't try to close if already disconnected
            if websocket.client_state.value <= 2:  # CONNECTING=0, CONNECTED=1, DISCONNECTED=2
                try:
                    await websocket.close()
                except Exception:
                    pass  # Ignore errors when closing
        except Exception as outer_e:
            print(f"[DEBUG handle_connection] OUTER EXCEPTION: {str(outer_e)}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _send_greeting(self, websocket: WebSocket, session: Any):
        """Send initial greeting message."""
        logger.info(f"Starting _send_greeting for session {session.id}")
        try:
            use_streamlined = self._should_use_streamlined(session.id)
            logger.info(f"Session {session.id} using streamlined protocol: {use_streamlined}")
            
            if use_streamlined:
                # Use streamlined protocol
                logger.info(f"Packaging greeting messages for session {session.id}")
                messages = self.streamlined_packager.package_messages(
                    session_id=session.id,
                    state="PROVIDE_GREETING",
                    agent_output=None,  # Greeting doesn't need agent output
                    context=None
                )
                logger.info(f"Packaged {len(messages)} messages for greeting")
                await self._send_messages(websocket, messages)
            else:
                # Use legacy protocol
                state_context = StateContext(
                    current_state="PROVIDE_GREETING",
                    user_intent=None,  # No intent for greeting
                    conversation_history=[],
                    session_data={}
                )
                
                # Get greeting from director
                greeting = await self.director.process(state_context)
                
                # Package and send
                message = self.packager.package(
                    response=greeting,
                    session_id=session.id,
                    current_state="PROVIDE_GREETING"
                )
                
                await websocket.send_json(message)
            
            logger.info(f"Sent greeting for session {session.id}")
            
        except Exception as e:
            logger.error(f"Error sending greeting: {str(e)}", exc_info=True)
            # Re-raise to ensure connection handler knows about the failure
            raise
    
    async def _handle_message(self, websocket: WebSocket, session: Any, message: Dict[str, Any]):
        """
        Handle an incoming message.
        
        Args:
            websocket: The WebSocket connection
            session: The session object
            message: The incoming message
        """
        try:
            # Validate we have user_id
            if not hasattr(self, 'current_user_id') or not self.current_user_id:
                raise RuntimeError("User ID not set in handler - connection not properly initialized")
            # Extract user input
            user_input = message.get('data', {}).get('text', '')
            logger.info(f"[DEBUG WebSocketHandler] Extracted user input: '{user_input}'")
            logger.info(f"[DEBUG WebSocketHandler] Message data keys: {list(message.get('data', {}).keys())}")
            logger.info(f"[DEBUG WebSocketHandler] Current session state: {session.current_state}")
            
            # STEP 1: Classify user intent - all messages go through the router
            logger.info(f"[DEBUG WebSocketHandler] Classifying intent for text: '{user_input}' in state: {session.current_state}")
            intent = await self.intent_router.classify(
                user_message=user_input,
                context={
                    'current_state': session.current_state,
                    'recent_history': session.conversation_history[-3:] if session.conversation_history else []
                }
            )
            logger.info(f"[DEBUG WebSocketHandler] Intent classified as: {intent.intent_type}")
            logger.info(f"[DEBUG WebSocketHandler] Intent confidence: {intent.confidence}")
            logger.info(f"[DEBUG WebSocketHandler] Intent extracted_info: {intent.extracted_info}")
            
            logger.info(f"Classified intent: {intent.intent_type} with confidence {intent.confidence}")
            
            # STEP 2: Handle intent-based actions
            if intent.intent_type == "Change_Topic":
                # Clear context and reset to questions
                await self.sessions.clear_context(session.id, self.current_user_id)
                session = await self.sessions.get_or_create(session.id, self.current_user_id)  # Refresh session
                session.current_state = "ASK_CLARIFYING_QUESTIONS"
                # extracted_info now contains the new topic as a string
                session.user_initial_request = intent.extracted_info or user_input
            
            elif intent.intent_type == "Change_Parameter":
                # Update specific parameters without full reset
                # For now, we'll need to parse the parameter from the user input
                # since extracted_info is now a string
                parameters = {}
                if intent.extracted_info:
                    # Simple parsing - could be improved
                    if "audience" in intent.extracted_info.lower():
                        parameters["audience"] = intent.extracted_info
                    elif "slide" in intent.extracted_info.lower():
                        parameters["slide_count"] = intent.extracted_info
                await self.sessions.update_parameters(session.id, self.current_user_id, parameters)
                session = await self.sessions.get_or_create(session.id, self.current_user_id)  # Refresh session
            
            elif intent.intent_type == "Submit_Initial_Topic":
                # Save the initial topic
                await self.sessions.save_session_data(
                    session.id,
                    self.current_user_id,
                    'user_initial_request',
                    user_input
                )
                logger.info(f"Saved initial topic for session {session.id}: {user_input}")
                session = await self.sessions.get_or_create(session.id, self.current_user_id)  # Refresh session
                logger.debug(f"After refresh - user_initial_request: {session.user_initial_request}")
                
            elif intent.intent_type == "Submit_Clarification_Answers":
                # Save clarifying answers
                await self.sessions.save_session_data(
                    session.id,
                    self.current_user_id,
                    'clarifying_answers',
                    {
                        "raw_answers": user_input,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                logger.info(f"Saved clarifying answers for session {session.id}")
                session = await self.sessions.get_or_create(session.id, self.current_user_id)  # Refresh session
            
            # STEP 3: Determine next state BEFORE processing (for intent-based routing)
            logger.info(f"[DEBUG WebSocketHandler] Determining next state: current={session.current_state}, intent={intent.intent_type}")
            next_state = self._determine_next_state(
                session.current_state, 
                intent, 
                None,  # No response yet
                session  # Pass session to check if questions have been asked
            )
            logger.info(f"[DEBUG WebSocketHandler] Next state determined: {next_state}")
            
            # Update state if it changed
            if next_state != session.current_state:
                logger.info(f"[DEBUG WebSocketHandler] Pre-processing state change: {session.current_state} -> {next_state}")
                await self.sessions.update_state(session.id, self.current_user_id, next_state)
                session.current_state = next_state
                logger.info(f"[DEBUG WebSocketHandler] State successfully changed to: {session.current_state}")
            else:
                logger.info(f"[DEBUG WebSocketHandler] State remains: {session.current_state}")
            
            # STEP 4: Build state context with the NEW state
            logger.debug(f"Building StateContext - user_initial_request: {session.user_initial_request}")
            state_context = StateContext(
                current_state=session.current_state,
                user_intent=intent,
                conversation_history=session.conversation_history or [],
                session_data={
                    'user_initial_request': session.user_initial_request,
                    'clarifying_answers': session.clarifying_answers,
                    'confirmation_plan': session.confirmation_plan,
                    'presentation_strawman': session.presentation_strawman
                }
            )
            
            # STEP 4.5: Send pre-generation status for long-running states
            use_streamlined = self._should_use_streamlined(session.id)
            if use_streamlined and session.current_state in ["GENERATE_STRAWMAN", "REFINE_STRAWMAN", "CONTENT_GENERATION"]:
                pre_status = self.streamlined_packager.create_pre_generation_status(
                    session_id=session.id,
                    state=session.current_state
                )
                await websocket.send_json(pre_status.model_dump(mode='json'))
                await asyncio.sleep(0.1)  # Small delay before processing
            
            # STEP 5: Process with Director based on NEW state and intent
            # Special handling for CONTENT_GENERATION state
            logger.info(f"[DEBUG WebSocketHandler] About to process state: {session.current_state}")
            logger.info(f"[DEBUG WebSocketHandler] Strawman data available: {session.presentation_strawman is not None}")
            if session.presentation_strawman:
                logger.info(f"[DEBUG WebSocketHandler] Strawman has {len(session.presentation_strawman.get('slides', []))} slides")
            
            if session.current_state == "CONTENT_GENERATION":
                logger.info("[DEBUG WebSocketHandler] Entering CONTENT_GENERATION state handler")
                # Initialize Content Orchestrator if needed
                if not self.content_orchestrator:
                    logger.info("[DEBUG WebSocketHandler] Creating ContentOrchestrator")
                    self.content_orchestrator = ContentOrchestrator()
                    logger.info("[DEBUG WebSocketHandler] ContentOrchestrator created")
                
                # Process content generation
                logger.info(f"[DEBUG WebSocketHandler] Starting content generation for session {session.id}")
                try:
                    # Get strawman from session
                    from src.models.agents import PresentationStrawman
                    strawman_data = session.presentation_strawman
                    if isinstance(strawman_data, dict):
                        strawman = PresentationStrawman(**strawman_data)
                    else:
                        strawman = strawman_data
                    
                    # Get director metadata if available
                    director_metadata = {
                        'formality_level': 'medium',  # Could extract from session history
                        'complexity_allowance': 'detailed'
                    }
                    
                    # Generate content
                    if use_streamlined:
                        # Stream updates as they happen
                        async for update in self.content_orchestrator.generate_content_streaming(
                            strawman=strawman,
                            session_id=session.id,
                            director_metadata=director_metadata,
                            generate_images=True
                        ):
                            # Convert update to WebSocket message
                            if update["type"] == "theme_ready":
                                msg = self.streamlined_packager.create_status_update(
                                    session_id=session.id,
                                    status="generating",
                                    text="Theme generated successfully"
                                )
                                await websocket.send_json(msg.model_dump(mode='json'))
                            elif update["type"] == "content_ready":
                                msg = self.streamlined_packager.create_status_update(
                                    session_id=session.id,
                                    status="generating",
                                    text=f"Generated content for slide {update['slide_index'] + 1}",
                                    progress=update.get('progress', 0)
                                )
                                await websocket.send_json(msg.model_dump(mode='json'))
                            elif update["type"] == "complete":
                                response = {
                                    'status': 'complete',
                                    'message': 'Content generation complete'
                                }
                    else:
                        # Non-streaming generation
                        result = await self.content_orchestrator.generate_content(
                            strawman=strawman,
                            session_id=session.id,
                            director_metadata=director_metadata,
                            generate_images=True
                        )
                        response = {
                            'status': 'complete',
                            'message': 'Content generation complete',
                            'content': result
                        }
                    
                    logger.info(f"[DEBUG WebSocketHandler] Content generation completed")
                except Exception as e:
                    logger.error(f"[DEBUG WebSocketHandler] Content generation failed: {e}", exc_info=True)
                    # Create error response
                    response = {
                        'status': 'error',
                        'message': f'Content generation failed: {str(e)}',
                        'error_type': type(e).__name__
                    }
                    # Send error status to client
                    if use_streamlined:
                        error_msg = self.streamlined_packager.create_status_update(
                            session_id=session.id,
                            status="error",
                            text=f"Content generation failed: {str(e)}"
                        )
                        await websocket.send_json(error_msg.model_dump(mode='json'))
            else:
                # Normal Director processing
                logger.info(f"[DEBUG WebSocketHandler] Processing with Director for state: {session.current_state}")
                response = await self.director.process(state_context)
            
            # Store in history
            await self.sessions.add_to_history(session.id, self.current_user_id, {
                'role': 'user',
                'content': user_input,
                'intent': intent.dict()
            })
            await self.sessions.add_to_history(session.id, self.current_user_id, {
                'role': 'assistant',
                'state': session.current_state,
                'content': response
            })
            
            # Save strawman to session if it was generated or refined
            if session.current_state in ["GENERATE_STRAWMAN", "REFINE_STRAWMAN"]:
                # Check if response is a PresentationStrawman object
                if response.__class__.__name__ == 'PresentationStrawman':
                    logger.warning(f"[DEBUG WebSocketHandler] Detected PresentationStrawman with {len(response.slides)} slides")
                    await self.sessions.save_session_data(
                        session.id,
                        self.current_user_id,
                        'presentation_strawman',
                        response.dict()
                    )
                    # Refresh session to get updated data
                    session = await self.sessions.get_or_create(session.id, self.current_user_id)
                    logger.warning(f"[DEBUG WebSocketHandler] Strawman saved and session refreshed")
                else:
                    logger.warning(f"[DEBUG WebSocketHandler] Response is not PresentationStrawman, it's {response.__class__.__name__}")
            
            # Package and send response based on protocol
            use_streamlined = self._should_use_streamlined(session.id)
            
            if use_streamlined:
                # Use streamlined protocol
                messages = self.streamlined_packager.package_messages(
                    session_id=session.id,
                    state=session.current_state,
                    agent_output=response,
                    context=state_context
                )
                await self._send_messages(websocket, messages)
            else:
                # Use legacy protocol
                ws_message = self.packager.package(
                    response=response,
                    session_id=session.id,
                    current_state=session.current_state
                )
                await websocket.send_json(ws_message)
            
            logger.info(f"Sent response for session {session.id} in state {session.current_state}")
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            # Send error message based on protocol
            use_streamlined = self._should_use_streamlined(session.id)
            
            if use_streamlined:
                error_messages = self.streamlined_packager.create_error_message(
                    session_id=session.id,
                    error_text=str(e)
                )
                await self._send_messages(websocket, error_messages)
            else:
                error_message = self.packager.package_error(
                    error=str(e),
                    session_id=session.id
                )
                await websocket.send_json(error_message)
    
    def _determine_next_state(self, current_state: str, intent: UserIntent, 
                             response: Any, session: Any = None) -> str:
        """
        Determine next state based on directional intent.
        Each intent now unambiguously implies the next state.
        
        Args:
            current_state: Current workflow state
            intent: Classified user intent
            response: Response from director (can be None for pre-processing)
            session: Session object to check state details
            
        Returns:
            Next state name
        """
        # Map directional intents to next states
        intent_to_next_state = {
            "Submit_Initial_Topic": "ASK_CLARIFYING_QUESTIONS",
            "Submit_Clarification_Answers": "CREATE_CONFIRMATION_PLAN",
            "Accept_Plan": "GENERATE_STRAWMAN",
            "Reject_Plan": "CREATE_CONFIRMATION_PLAN",  # Loop back
            "Accept_Strawman": "CONTENT_GENERATION",  # Trigger content generation
            "Submit_Refinement_Request": "REFINE_STRAWMAN",
            "Change_Topic": "ASK_CLARIFYING_QUESTIONS",  # Reset
            "Change_Parameter": "CREATE_CONFIRMATION_PLAN",  # Regenerate
            "Ask_Help_Or_Question": current_state  # No state change
        }
        
        # Get next state from mapping
        next_state = intent_to_next_state.get(intent.intent_type, current_state)
        logger.info(f"[DEBUG _determine_next_state] Intent: {intent.intent_type} -> Next state: {next_state}")
        
        # Log the transition
        if next_state != current_state:
            logger.info(f"State transition: {current_state} -> {next_state} (intent: {intent.intent_type})")
        else:
            logger.info(f"State remains: {current_state} (intent: {intent.intent_type})")
            
        return next_state