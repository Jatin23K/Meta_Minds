# =========================================================
# realtime_collaboration.py: Real-Time Collaboration System
# =========================================================
# WebRTC-based real-time collaboration for live data analysis
# Enables multiple users to collaborate on analysis in real-time

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import websockets
import aiortc
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from aiortc.contrib.media import MediaPlayer, MediaRecorder
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
import threading
import queue

@dataclass
class CollaborationSession:
    """Real-time collaboration session."""
    session_id: str
    name: str
    description: str
    host_user_id: str
    created_at: datetime
    participants: List[str] = None
    shared_context: Dict[str, Any] = None
    analysis_state: Dict[str, Any] = None
    active_datasets: List[str] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = [self.host_user_id]
        if self.shared_context is None:
            self.shared_context = {}
        if self.analysis_state is None:
            self.analysis_state = {}
        if self.active_datasets is None:
            self.active_datasets = []

@dataclass
class RealtimeMessage:
    """Real-time message between collaborators."""
    message_id: str
    session_id: str
    sender_id: str
    message_type: str  # 'analysis_update', 'context_change', 'question_added', 'chat', 'cursor_move'
    content: Dict[str, Any]
    timestamp: datetime

@dataclass
class LiveAnalysisState:
    """Live analysis state shared among collaborators."""
    current_dataset: str
    analysis_progress: float
    generated_questions: List[Dict[str, Any]]
    quality_metrics: Dict[str, Any]
    user_annotations: Dict[str, List[Dict[str, Any]]]  # user_id -> annotations
    active_filters: Dict[str, Any]
    visualization_settings: Dict[str, Any]

class RealtimeCollaborationManager:
    """Manages real-time collaboration sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.rtc_connections: Dict[str, RTCPeerConnection] = {}
        self.data_channels: Dict[str, RTCDataChannel] = {}
        self.message_history: Dict[str, List[RealtimeMessage]] = {}
        
        # Live analysis states
        self.live_states: Dict[str, LiveAnalysisState] = {}
        
        # Event handlers
        self.event_handlers = {
            'user_joined': [],
            'user_left': [],
            'analysis_updated': [],
            'question_added': [],
            'context_changed': []
        }
        
        self.logger = logging.getLogger("RealtimeCollaboration")
        
        # Start WebSocket server
        self.websocket_server = None
        self.start_websocket_server()
    
    def start_websocket_server(self):
        """Start WebSocket server for real-time communication."""
        async def websocket_handler(websocket, path):
            try:
                await self.handle_websocket_connection(websocket, path)
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
        
        # Start server in background thread
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            start_server = websockets.serve(websocket_handler, "localhost", 8765)
            loop.run_until_complete(start_server)
            loop.run_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        self.logger.info("WebSocket server started on ws://localhost:8765")
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection."""
        user_id = None
        try:
            # Wait for authentication message
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            user_id = auth_data.get('user_id')
            session_id = auth_data.get('session_id')
            
            if not user_id or not session_id:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
            
            # Register connection
            self.websocket_connections[user_id] = websocket
            
            # Join session
            if session_id in self.sessions:
                await self.join_session(user_id, session_id)
            
            # Handle messages
            async for message in websocket:
                await self.handle_realtime_message(user_id, json.loads(message))
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"User {user_id} disconnected")
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        finally:
            if user_id:
                await self.handle_user_disconnect(user_id)
    
    async def create_session(self, host_user_id: str, name: str, 
                           description: str = "") -> str:
        """Create a new collaboration session."""
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            name=name,
            description=description,
            host_user_id=host_user_id,
            created_at=datetime.now()
        )
        
        self.sessions[session_id] = session
        self.user_sessions[host_user_id] = session_id
        self.message_history[session_id] = []
        
        # Initialize live analysis state
        self.live_states[session_id] = LiveAnalysisState(
            current_dataset="",
            analysis_progress=0.0,
            generated_questions=[],
            quality_metrics={},
            user_annotations={},
            active_filters={},
            visualization_settings={}
        )
        
        self.logger.info(f"Created collaboration session: {name} ({session_id})")
        return session_id
    
    async def join_session(self, user_id: str, session_id: str) -> bool:
        """Join an existing collaboration session."""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if user_id not in session.participants:
            session.participants.append(user_id)
        
        self.user_sessions[user_id] = session_id
        
        # Notify other participants
        await self.broadcast_to_session(session_id, {
            'type': 'user_joined',
            'user_id': user_id,
            'participants': session.participants
        }, exclude_user=user_id)
        
        # Send current state to new user
        if user_id in self.websocket_connections:
            await self.websocket_connections[user_id].send(json.dumps({
                'type': 'session_state',
                'session': asdict(session),
                'live_state': asdict(self.live_states[session_id]),
                'recent_messages': [asdict(msg) for msg in self.message_history[session_id][-50:]]
            }))
        
        # Trigger event handlers
        await self.trigger_event('user_joined', {
            'user_id': user_id,
            'session_id': session_id
        })
        
        self.logger.info(f"User {user_id} joined session {session_id}")
        return True
    
    async def leave_session(self, user_id: str) -> bool:
        """Leave current collaboration session."""
        if user_id not in self.user_sessions:
            return False
        
        session_id = self.user_sessions[user_id]
        session = self.sessions[session_id]
        
        if user_id in session.participants:
            session.participants.remove(user_id)
        
        del self.user_sessions[user_id]
        
        # Notify other participants
        await self.broadcast_to_session(session_id, {
            'type': 'user_left',
            'user_id': user_id,
            'participants': session.participants
        })
        
        # If host left and others remain, transfer host
        if user_id == session.host_user_id and session.participants:
            session.host_user_id = session.participants[0]
            await self.broadcast_to_session(session_id, {
                'type': 'host_changed',
                'new_host': session.host_user_id
            })
        
        # If no participants left, cleanup session
        if not session.participants:
            await self.cleanup_session(session_id)
        
        # Trigger event handlers
        await self.trigger_event('user_left', {
            'user_id': user_id,
            'session_id': session_id
        })
        
        self.logger.info(f"User {user_id} left session {session_id}")
        return True
    
    async def handle_realtime_message(self, sender_id: str, message_data: Dict[str, Any]):
        """Handle incoming real-time message."""
        try:
            message_type = message_data.get('type')
            content = message_data.get('content', {})
            
            if sender_id not in self.user_sessions:
                return
            
            session_id = self.user_sessions[sender_id]
            
            # Create message object
            message = RealtimeMessage(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                sender_id=sender_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now()
            )
            
            # Store message
            self.message_history[session_id].append(message)
            
            # Handle specific message types
            if message_type == 'analysis_update':
                await self.handle_analysis_update(message)
            elif message_type == 'context_change':
                await self.handle_context_change(message)
            elif message_type == 'question_added':
                await self.handle_question_added(message)
            elif message_type == 'chat':
                await self.handle_chat_message(message)
            elif message_type == 'cursor_move':
                await self.handle_cursor_move(message)
            elif message_type == 'annotation_added':
                await self.handle_annotation_added(message)
            
            # Broadcast to other participants
            await self.broadcast_to_session(session_id, {
                'type': 'message',
                'message': asdict(message)
            }, exclude_user=sender_id)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def handle_analysis_update(self, message: RealtimeMessage):
        """Handle analysis progress update."""
        session_id = message.session_id
        live_state = self.live_states[session_id]
        
        content = message.content
        
        if 'progress' in content:
            live_state.analysis_progress = content['progress']
        
        if 'dataset' in content:
            live_state.current_dataset = content['dataset']
        
        if 'questions' in content:
            live_state.generated_questions = content['questions']
        
        if 'quality_metrics' in content:
            live_state.quality_metrics = content['quality_metrics']
        
        # Trigger event handlers
        await self.trigger_event('analysis_updated', {
            'session_id': session_id,
            'live_state': live_state
        })
    
    async def handle_context_change(self, message: RealtimeMessage):
        """Handle context/settings change."""
        session_id = message.session_id
        session = self.sessions[session_id]
        
        # Update shared context
        content = message.content
        if 'context_updates' in content:
            session.shared_context.update(content['context_updates'])
        
        # Update visualization settings
        live_state = self.live_states[session_id]
        if 'visualization_settings' in content:
            live_state.visualization_settings.update(content['visualization_settings'])
        
        # Trigger event handlers
        await self.trigger_event('context_changed', {
            'session_id': session_id,
            'changes': content
        })
    
    async def handle_question_added(self, message: RealtimeMessage):
        """Handle new question added."""
        session_id = message.session_id
        live_state = self.live_states[session_id]
        
        question = message.content.get('question')
        if question:
            live_state.generated_questions.append({
                'question': question,
                'added_by': message.sender_id,
                'timestamp': message.timestamp.isoformat()
            })
        
        # Trigger event handlers
        await self.trigger_event('question_added', {
            'session_id': session_id,
            'question': question,
            'user_id': message.sender_id
        })
    
    async def handle_chat_message(self, message: RealtimeMessage):
        """Handle chat message."""
        # Chat messages are just stored and broadcast, no special handling needed
        pass
    
    async def handle_cursor_move(self, message: RealtimeMessage):
        """Handle cursor movement for live collaboration."""
        # Cursor positions are just broadcast for real-time feedback
        pass
    
    async def handle_annotation_added(self, message: RealtimeMessage):
        """Handle user annotation."""
        session_id = message.session_id
        live_state = self.live_states[session_id]
        sender_id = message.sender_id
        
        if sender_id not in live_state.user_annotations:
            live_state.user_annotations[sender_id] = []
        
        annotation = message.content.get('annotation')
        if annotation:
            live_state.user_annotations[sender_id].append(annotation)
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any], 
                                 exclude_user: str = None):
        """Broadcast message to all session participants."""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        message_str = json.dumps(message)
        
        for user_id in session.participants:
            if user_id == exclude_user:
                continue
            
            if user_id in self.websocket_connections:
                try:
                    await self.websocket_connections[user_id].send(message_str)
                except Exception as e:
                    self.logger.error(f"Failed to send message to {user_id}: {e}")
    
    async def handle_user_disconnect(self, user_id: str):
        """Handle user disconnection."""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]
        
        await self.leave_session(user_id)
    
    async def cleanup_session(self, session_id: str):
        """Clean up empty session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if session_id in self.live_states:
            del self.live_states[session_id]
        
        if session_id in self.message_history:
            del self.message_history[session_id]
        
        self.logger.info(f"Cleaned up session: {session_id}")
    
    async def trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
    
    def register_event_handler(self, event_type: str, handler):
        """Register event handler."""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        live_state = self.live_states[session_id]
        
        return {
            'session': asdict(session),
            'live_state': asdict(live_state),
            'participant_count': len(session.participants),
            'message_count': len(self.message_history[session_id])
        }
    
    def list_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List available sessions."""
        sessions = []
        
        for session in self.sessions.values():
            if user_id and user_id not in session.participants:
                continue
            
            sessions.append({
                'session_id': session.session_id,
                'name': session.name,
                'description': session.description,
                'host': session.host_user_id,
                'participant_count': len(session.participants),
                'created_at': session.created_at.isoformat()
            })
        
        return sessions

class RealtimeAnalysisInterface:
    """Streamlit interface for real-time collaborative analysis."""
    
    def __init__(self, collaboration_manager: RealtimeCollaborationManager):
        self.collaboration_manager = collaboration_manager
        
        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
        
        if 'websocket_connected' not in st.session_state:
            st.session_state.websocket_connected = False
    
    def render_collaboration_interface(self):
        """Render the main collaboration interface."""
        st.markdown("# 🔄 Real-Time Collaboration")
        
        # Session management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.current_session_id:
                self.render_active_session()
            else:
                self.render_session_selection()
        
        with col2:
            self.render_session_controls()
    
    def render_session_selection(self):
        """Render session selection interface."""
        st.markdown("## Join or Create Session")
        
        # List available sessions
        sessions = self.collaboration_manager.list_sessions()
        
        if sessions:
            st.markdown("### Available Sessions")
            
            for session in sessions:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**{session['name']}**")
                        st.write(session['description'])
                    
                    with col2:
                        st.write(f"👥 {session['participant_count']} participants")
                        st.write(f"🕒 {session['created_at'][:16]}")
                    
                    with col3:
                        if st.button("Join", key=f"join_{session['session_id']}"):
                            asyncio.run(self.join_session(session['session_id']))
        
        # Create new session
        st.markdown("### Create New Session")
        
        with st.form("create_session"):
            session_name = st.text_input("Session Name")
            session_description = st.text_area("Description")
            
            if st.form_submit_button("Create Session"):
                if session_name:
                    session_id = asyncio.run(
                        self.collaboration_manager.create_session(
                            st.session_state.user_id,
                            session_name,
                            session_description
                        )
                    )
                    asyncio.run(self.join_session(session_id))
                    st.rerun()
    
    def render_active_session(self):
        """Render active collaboration session."""
        session_id = st.session_state.current_session_id
        session_info = self.collaboration_manager.get_session_info(session_id)
        
        if not session_info:
            st.error("Session not found")
            st.session_state.current_session_id = None
            st.rerun()
            return
        
        session = session_info['session']
        live_state = session_info['live_state']
        
        st.markdown(f"## 🔄 {session['name']}")
        st.markdown(f"👥 **Participants:** {', '.join(session['participants'])}")
        
        # Real-time analysis area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.render_live_analysis(live_state)
        
        with col2:
            self.render_chat_panel(session_id)
    
    def render_live_analysis(self, live_state: Dict[str, Any]):
        """Render live analysis interface."""
        st.markdown("### 📊 Live Analysis")
        
        # Progress indicator
        if live_state['analysis_progress'] > 0:
            st.progress(live_state['analysis_progress'])
            st.write(f"Analysis Progress: {live_state['analysis_progress']:.1%}")
        
        # Current dataset
        if live_state['current_dataset']:
            st.write(f"**Current Dataset:** {live_state['current_dataset']}")
        
        # Generated questions
        if live_state['generated_questions']:
            st.markdown("#### 🤔 Generated Questions")
            
            for i, q in enumerate(live_state['generated_questions']):
                with st.expander(f"Question {i+1}"):
                    st.write(q.get('question', ''))
                    
                    if 'added_by' in q:
                        st.caption(f"Added by: {q['added_by']}")
        
        # Quality metrics
        if live_state['quality_metrics']:
            st.markdown("#### 📈 Quality Metrics")
            
            metrics = live_state['quality_metrics']
            if 'average_score' in metrics:
                st.metric("Average Quality", f"{metrics['average_score']:.2f}")
        
        # User annotations
        if live_state['user_annotations']:
            st.markdown("#### 📝 Annotations")
            
            for user_id, annotations in live_state['user_annotations'].items():
                st.write(f"**{user_id}:**")
                for annotation in annotations:
                    st.write(f"- {annotation}")
    
    def render_chat_panel(self, session_id: str):
        """Render real-time chat panel."""
        st.markdown("### 💬 Live Chat")
        
        # Chat messages (would be populated from message history)
        chat_container = st.container()
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            message = st.text_input("Message", placeholder="Type a message...")
            
            if st.form_submit_button("Send"):
                if message:
                    # Send chat message
                    asyncio.run(self.send_chat_message(session_id, message))
    
    def render_session_controls(self):
        """Render session control panel."""
        st.markdown("### ⚙️ Session Controls")
        
        if st.session_state.current_session_id:
            if st.button("🚪 Leave Session"):
                asyncio.run(self.leave_session())
                st.rerun()
            
            st.markdown("#### 🎛️ Analysis Controls")
            
            # File upload for collaborative analysis
            uploaded_file = st.file_uploader("Upload Dataset", type=['csv', 'xlsx', 'json'])
            
            if uploaded_file and st.button("Start Analysis"):
                # Trigger collaborative analysis
                asyncio.run(self.start_collaborative_analysis(uploaded_file))
            
            # Context sharing
            st.markdown("#### 📋 Shared Context")
            
            with st.expander("Update Context"):
                subject_area = st.text_input("Subject Area")
                target_audience = st.text_input("Target Audience")
                
                if st.button("Update Context"):
                    context_updates = {
                        'subject_area': subject_area,
                        'target_audience': target_audience
                    }
                    asyncio.run(self.update_context(context_updates))
        
        # Connection status
        status_color = "🟢" if st.session_state.websocket_connected else "🔴"
        st.write(f"{status_color} Connection Status")
    
    async def join_session(self, session_id: str):
        """Join a collaboration session."""
        success = await self.collaboration_manager.join_session(
            st.session_state.user_id, session_id
        )
        
        if success:
            st.session_state.current_session_id = session_id
            st.success("Joined session successfully!")
        else:
            st.error("Failed to join session")
    
    async def leave_session(self):
        """Leave current session."""
        if st.session_state.current_session_id:
            await self.collaboration_manager.leave_session(st.session_state.user_id)
            st.session_state.current_session_id = None
    
    async def send_chat_message(self, session_id: str, message: str):
        """Send chat message."""
        # In real implementation, this would send via WebSocket
        pass
    
    async def start_collaborative_analysis(self, uploaded_file):
        """Start collaborative analysis."""
        # In real implementation, this would trigger Meta Minds analysis
        # and broadcast updates to all participants
        pass
    
    async def update_context(self, context_updates: Dict[str, Any]):
        """Update shared context."""
        # In real implementation, this would broadcast context changes
        pass

# Global collaboration manager
collaboration_manager = RealtimeCollaborationManager()

def create_collaboration_interface():
    """Create Streamlit collaboration interface."""
    interface = RealtimeAnalysisInterface(collaboration_manager)
    interface.render_collaboration_interface()

if __name__ == "__main__":
    create_collaboration_interface()
