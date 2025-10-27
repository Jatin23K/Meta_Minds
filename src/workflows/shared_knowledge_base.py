# =========================================================
# shared_knowledge_base.py: Shared Knowledge Base System
# =========================================================
# Central knowledge repository for all automation systems
# Enables context sharing and learning across automations

import json
import logging
import sqlite3
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import threading
from contextlib import contextmanager

@dataclass
class KnowledgeEntry:
    """Individual knowledge entry."""
    entry_id: str
    category: str  # 'context', 'pattern', 'result', 'error', 'best_practice'
    source_system: str
    title: str
    content: Dict[str, Any]
    tags: List[str]
    confidence_score: float  # 0-1
    usage_count: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    
@dataclass
class ContextSnapshot:
    """Snapshot of system context at a point in time."""
    snapshot_id: str
    system_id: str
    timestamp: datetime
    user_context: Dict[str, Any]
    task_context: Dict[str, Any]
    environmental_context: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class SharedKnowledgeBase:
    """Central knowledge repository for automation ecosystem."""
    
    def __init__(self, db_path: str = "shared_knowledge.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self.cache: Dict[str, KnowledgeEntry] = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Initialize database
        self._init_database()
        
        # Load frequently used entries into cache
        self._load_cache()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SharedKnowledgeBase")
    
    def _init_database(self):
        """Initialize SQLite database for knowledge storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    entry_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content BLOB NOT NULL,
                    tags TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    system_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_context BLOB,
                    task_context BLOB,
                    environmental_context BLOB,
                    performance_metrics BLOB
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON knowledge_entries(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_system ON knowledge_entries(source_system)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags ON knowledge_entries(tags)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_time ON context_snapshots(system_id, timestamp)
            """)
    
    def _load_cache(self):
        """Load frequently used entries into memory cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT entry_id, category, source_system, title, content, tags,
                       confidence_score, usage_count, created_at, updated_at, expires_at
                FROM knowledge_entries
                WHERE usage_count > 5
                ORDER BY usage_count DESC
                LIMIT 100
            """)
            
            for row in cursor.fetchall():
                entry = self._row_to_knowledge_entry(row)
                self.cache[entry.entry_id] = entry
    
    def _row_to_knowledge_entry(self, row) -> KnowledgeEntry:
        """Convert database row to KnowledgeEntry."""
        entry_id, category, source_system, title, content_blob, tags_str, \
        confidence_score, usage_count, created_at_str, updated_at_str, expires_at_str = row
        
        content = pickle.loads(content_blob)
        tags = json.loads(tags_str)
        created_at = datetime.fromisoformat(created_at_str)
        updated_at = datetime.fromisoformat(updated_at_str)
        expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None
        
        return KnowledgeEntry(
            entry_id=entry_id,
            category=category,
            source_system=source_system,
            title=title,
            content=content,
            tags=tags,
            confidence_score=confidence_score,
            usage_count=usage_count,
            created_at=created_at,
            updated_at=updated_at,
            expires_at=expires_at
        )
    
    @contextmanager
    def _get_db_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            yield conn
        finally:
            conn.close()
    
    def store_knowledge(self, category: str, source_system: str, title: str,
                       content: Dict[str, Any], tags: List[str],
                       confidence_score: float = 1.0,
                       ttl_hours: Optional[int] = None) -> str:
        """Store new knowledge entry."""
        
        with self.lock:
            # Generate unique ID
            content_hash = hashlib.md5(json.dumps(content, sort_keys=True).encode()).hexdigest()
            entry_id = f"{category}_{source_system}_{content_hash[:8]}"
            
            # Check if entry already exists
            existing = self.get_knowledge(entry_id)
            if existing:
                # Update existing entry
                return self.update_knowledge(entry_id, content, confidence_score)
            
            # Create new entry
            now = datetime.now()
            expires_at = now + timedelta(hours=ttl_hours) if ttl_hours else None
            
            entry = KnowledgeEntry(
                entry_id=entry_id,
                category=category,
                source_system=source_system,
                title=title,
                content=content,
                tags=tags,
                confidence_score=confidence_score,
                usage_count=0,
                created_at=now,
                updated_at=now,
                expires_at=expires_at
            )
            
            # Store in database
            with self._get_db_connection() as conn:
                conn.execute("""
                    INSERT INTO knowledge_entries 
                    (entry_id, category, source_system, title, content, tags,
                     confidence_score, usage_count, created_at, updated_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.entry_id,
                    entry.category,
                    entry.source_system,
                    entry.title,
                    pickle.dumps(entry.content),
                    json.dumps(entry.tags),
                    entry.confidence_score,
                    entry.usage_count,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                    entry.expires_at.isoformat() if entry.expires_at else None
                ))
                conn.commit()
            
            # Add to cache if high confidence
            if confidence_score > 0.7:
                self.cache[entry_id] = entry
            
            self.logger.info(f"Stored knowledge entry: {entry_id}")
            return entry_id
    
    def get_knowledge(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve knowledge entry by ID."""
        
        with self.lock:
            # Check cache first
            if entry_id in self.cache:
                entry = self.cache[entry_id]
                # Check if expired
                if entry.expires_at and datetime.now() > entry.expires_at:
                    del self.cache[entry_id]
                    self._delete_knowledge(entry_id)
                    return None
                
                # Update usage count
                self._increment_usage(entry_id)
                return entry
            
            # Query database
            with self._get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT entry_id, category, source_system, title, content, tags,
                           confidence_score, usage_count, created_at, updated_at, expires_at
                    FROM knowledge_entries
                    WHERE entry_id = ?
                """, (entry_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                entry = self._row_to_knowledge_entry(row)
                
                # Check if expired
                if entry.expires_at and datetime.now() > entry.expires_at:
                    self._delete_knowledge(entry_id)
                    return None
                
                # Update usage count
                self._increment_usage(entry_id)
                
                # Add to cache if frequently used
                if entry.usage_count > 3:
                    self.cache[entry_id] = entry
                
                return entry
    
    def search_knowledge(self, category: Optional[str] = None,
                        source_system: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        min_confidence: float = 0.0,
                        limit: int = 50) -> List[KnowledgeEntry]:
        """Search knowledge entries by criteria."""
        
        query = """
            SELECT entry_id, category, source_system, title, content, tags,
                   confidence_score, usage_count, created_at, updated_at, expires_at
            FROM knowledge_entries
            WHERE confidence_score >= ?
        """
        params = [min_confidence]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if source_system:
            query += " AND source_system = ?"
            params.append(source_system)
        
        if tags:
            # Search for entries containing any of the specified tags
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])
        
        query += " ORDER BY confidence_score DESC, usage_count DESC LIMIT ?"
        params.append(limit)
        
        entries = []
        with self._get_db_connection() as conn:
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                entry = self._row_to_knowledge_entry(row)
                
                # Skip expired entries
                if entry.expires_at and datetime.now() > entry.expires_at:
                    continue
                
                entries.append(entry)
        
        return entries
    
    def get_relevant_context(self, system_id: str, task_type: str,
                            keywords: List[str]) -> Dict[str, Any]:
        """Get relevant context for a specific system and task."""
        
        # Search for relevant knowledge
        relevant_entries = self.search_knowledge(
            tags=keywords + [system_id, task_type],
            min_confidence=0.5,
            limit=20
        )
        
        # Get recent context snapshots
        recent_snapshots = self.get_recent_context_snapshots(system_id, hours=24)
        
        # Compile relevant context
        context = {
            "system_id": system_id,
            "task_type": task_type,
            "keywords": keywords,
            "relevant_knowledge": [
                {
                    "title": entry.title,
                    "content": entry.content,
                    "confidence": entry.confidence_score,
                    "source": entry.source_system
                }
                for entry in relevant_entries[:10]
            ],
            "recent_patterns": self._extract_patterns_from_snapshots(recent_snapshots),
            "best_practices": [
                entry.content for entry in relevant_entries
                if entry.category == "best_practice" and entry.confidence_score > 0.8
            ][:5],
            "common_errors": [
                entry.content for entry in relevant_entries
                if entry.category == "error" and entry.usage_count > 2
            ][:3]
        }
        
        return context
    
    def store_context_snapshot(self, system_id: str, user_context: Dict[str, Any],
                              task_context: Dict[str, Any],
                              environmental_context: Dict[str, Any],
                              performance_metrics: Dict[str, Any]) -> str:
        """Store a context snapshot."""
        
        snapshot_id = f"{system_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        snapshot = ContextSnapshot(
            snapshot_id=snapshot_id,
            system_id=system_id,
            timestamp=datetime.now(),
            user_context=user_context,
            task_context=task_context,
            environmental_context=environmental_context,
            performance_metrics=performance_metrics
        )
        
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT INTO context_snapshots
                (snapshot_id, system_id, timestamp, user_context, task_context,
                 environmental_context, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.snapshot_id,
                snapshot.system_id,
                snapshot.timestamp.isoformat(),
                pickle.dumps(snapshot.user_context),
                pickle.dumps(snapshot.task_context),
                pickle.dumps(snapshot.environmental_context),
                pickle.dumps(snapshot.performance_metrics)
            ))
            conn.commit()
        
        self.logger.info(f"Stored context snapshot: {snapshot_id}")
        return snapshot_id
    
    def get_recent_context_snapshots(self, system_id: str, hours: int = 24) -> List[ContextSnapshot]:
        """Get recent context snapshots for a system."""
        
        since = datetime.now() - timedelta(hours=hours)
        
        snapshots = []
        with self._get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT snapshot_id, system_id, timestamp, user_context, task_context,
                       environmental_context, performance_metrics
                FROM context_snapshots
                WHERE system_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (system_id, since.isoformat()))
            
            for row in cursor.fetchall():
                snapshot_id, system_id, timestamp_str, user_context_blob, \
                task_context_blob, env_context_blob, perf_metrics_blob = row
                
                snapshot = ContextSnapshot(
                    snapshot_id=snapshot_id,
                    system_id=system_id,
                    timestamp=datetime.fromisoformat(timestamp_str),
                    user_context=pickle.loads(user_context_blob),
                    task_context=pickle.loads(task_context_blob),
                    environmental_context=pickle.loads(env_context_blob),
                    performance_metrics=pickle.loads(perf_metrics_blob)
                )
                snapshots.append(snapshot)
        
        return snapshots
    
    def _extract_patterns_from_snapshots(self, snapshots: List[ContextSnapshot]) -> Dict[str, Any]:
        """Extract patterns from context snapshots."""
        if not snapshots:
            return {}
        
        patterns = {
            "common_user_preferences": {},
            "typical_task_parameters": {},
            "performance_trends": {},
            "environmental_factors": {}
        }
        
        # Analyze user preferences
        user_prefs = {}
        for snapshot in snapshots:
            for key, value in snapshot.user_context.items():
                if key not in user_prefs:
                    user_prefs[key] = []
                user_prefs[key].append(value)
        
        # Find most common preferences
        for key, values in user_prefs.items():
            if isinstance(values[0], str):
                most_common = max(set(values), key=values.count)
                patterns["common_user_preferences"][key] = most_common
        
        # Analyze performance trends
        perf_metrics = [s.performance_metrics for s in snapshots if s.performance_metrics]
        if perf_metrics:
            # Calculate averages
            all_keys = set()
            for metrics in perf_metrics:
                all_keys.update(metrics.keys())
            
            for key in all_keys:
                values = [m.get(key, 0) for m in perf_metrics if isinstance(m.get(key), (int, float))]
                if values:
                    patterns["performance_trends"][key] = {
                        "average": sum(values) / len(values),
                        "trend": "improving" if values[-1] > values[0] else "declining" if values[-1] < values[0] else "stable"
                    }
        
        return patterns
    
    def update_knowledge(self, entry_id: str, content: Dict[str, Any],
                        confidence_score: Optional[float] = None) -> str:
        """Update existing knowledge entry."""
        
        with self.lock:
            with self._get_db_connection() as conn:
                update_fields = ["content = ?", "updated_at = ?"]
                params = [pickle.dumps(content), datetime.now().isoformat()]
                
                if confidence_score is not None:
                    update_fields.append("confidence_score = ?")
                    params.append(confidence_score)
                
                params.append(entry_id)
                
                conn.execute(f"""
                    UPDATE knowledge_entries
                    SET {', '.join(update_fields)}
                    WHERE entry_id = ?
                """, params)
                conn.commit()
            
            # Update cache if present
            if entry_id in self.cache:
                self.cache[entry_id].content = content
                self.cache[entry_id].updated_at = datetime.now()
                if confidence_score is not None:
                    self.cache[entry_id].confidence_score = confidence_score
            
            self.logger.info(f"Updated knowledge entry: {entry_id}")
            return entry_id
    
    def _increment_usage(self, entry_id: str):
        """Increment usage count for an entry."""
        with self._get_db_connection() as conn:
            conn.execute("""
                UPDATE knowledge_entries
                SET usage_count = usage_count + 1
                WHERE entry_id = ?
            """, (entry_id,))
            conn.commit()
        
        # Update cache if present
        if entry_id in self.cache:
            self.cache[entry_id].usage_count += 1
    
    def _delete_knowledge(self, entry_id: str):
        """Delete expired or invalid knowledge entry."""
        with self._get_db_connection() as conn:
            conn.execute("DELETE FROM knowledge_entries WHERE entry_id = ?", (entry_id,))
            conn.commit()
        
        if entry_id in self.cache:
            del self.cache[entry_id]
    
    def cleanup_expired_entries(self):
        """Clean up expired knowledge entries."""
        now = datetime.now()
        
        with self._get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT entry_id FROM knowledge_entries
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (now.isoformat(),))
            
            expired_ids = [row[0] for row in cursor.fetchall()]
            
            if expired_ids:
                placeholders = ','.join(['?' for _ in expired_ids])
                conn.execute(f"""
                    DELETE FROM knowledge_entries
                    WHERE entry_id IN ({placeholders})
                """, expired_ids)
                conn.commit()
                
                # Remove from cache
                for entry_id in expired_ids:
                    if entry_id in self.cache:
                        del self.cache[entry_id]
                
                self.logger.info(f"Cleaned up {len(expired_ids)} expired entries")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        with self._get_db_connection() as conn:
            # Total entries by category
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM knowledge_entries
                GROUP BY category
            """)
            categories = dict(cursor.fetchall())
            
            # Total entries by source system
            cursor = conn.execute("""
                SELECT source_system, COUNT(*) as count
                FROM knowledge_entries
                GROUP BY source_system
            """)
            systems = dict(cursor.fetchall())
            
            # Most used entries
            cursor = conn.execute("""
                SELECT title, usage_count
                FROM knowledge_entries
                ORDER BY usage_count DESC
                LIMIT 10
            """)
            most_used = cursor.fetchall()
            
            # Recent activity
            since = datetime.now() - timedelta(days=7)
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM knowledge_entries
                WHERE created_at >= ?
            """, (since.isoformat(),))
            recent_entries = cursor.fetchone()[0]
        
        return {
            "total_entries": sum(categories.values()),
            "entries_by_category": categories,
            "entries_by_system": systems,
            "most_used_entries": most_used,
            "recent_entries_7days": recent_entries,
            "cache_size": len(self.cache)
        }

# Global knowledge base instance
knowledge_base = SharedKnowledgeBase()
