# =========================================================
# performance_optimizer.py: Advanced Performance Optimization System
# =========================================================
# Implements caching, async processing, and performance optimizations
# for Meta Minds to achieve enterprise-grade performance

import asyncio
import hashlib
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from functools import wraps, lru_cache
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp

import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict

# Redis for distributed caching (optional)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.info("Redis not available. Using local caching only.")

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    timestamp: datetime
    expiry: Optional[datetime]
    access_count: int
    size_bytes: int
    tags: List[str]

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    operation: str
    duration: float
    cache_hit: bool
    memory_usage: float
    cpu_usage: float
    timestamp: datetime

class AdvancedCache:
    """High-performance caching system with multiple backends."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, datetime] = {}
        self.lock = threading.RLock()
        
        # Redis connection (if available)
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=0, 
                    decode_responses=False
                )
                self.redis_client.ping()
                logging.info("Connected to Redis for distributed caching")
            except:
                self.redis_client = None
                logging.info("Redis not available, using local cache only")
        
        # Performance tracking
        self.metrics: List[PerformanceMetrics] = []
        self.hit_rate = 0.0
        self.total_requests = 0
        self.cache_hits = 0
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key for function calls."""
        # Create a deterministic hash of function name and arguments
        key_data = {
            'function': func_name,
            'args': str(args),
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logging.warning(f"Failed to serialize value: {e}")
            return pickle.dumps(str(value))
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            return pickle.loads(data)
        except Exception as e:
            logging.warning(f"Failed to deserialize value: {e}")
            return None
    
    def _cleanup_expired(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.expiry and now > entry.expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _evict_lru(self):
        """Evict least recently used entries when cache is full."""
        if len(self.cache) <= self.max_size:
            return
        
        # Sort by access time and remove oldest
        sorted_keys = sorted(
            self.access_times.items(), 
            key=lambda x: x[1]
        )
        
        to_remove = len(self.cache) - self.max_size + 10  # Remove extra for efficiency
        for key, _ in sorted_keys[:to_remove]:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            self.total_requests += 1
            
            # Check local cache first
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if entry.expiry and datetime.now() > entry.expiry:
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
                else:
                    # Update access time and count
                    self.access_times[key] = datetime.now()
                    entry.access_count += 1
                    self.cache_hits += 1
                    self._update_hit_rate()
                    return entry.value
            
            # Check Redis cache if available
            if self.redis_client:
                try:
                    data = self.redis_client.get(f"metamind:{key}")
                    if data:
                        value = self._deserialize_value(data)
                        # Store in local cache for faster access
                        self.set(key, value, ttl=self.default_ttl)
                        self.cache_hits += 1
                        self._update_hit_rate()
                        return value
                except Exception as e:
                    logging.warning(f"Redis get error: {e}")
            
            self._update_hit_rate()
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache."""
        with self.lock:
            try:
                # Cleanup expired entries
                self._cleanup_expired()
                
                # Evict if necessary
                self._evict_lru()
                
                # Calculate expiry
                expiry = None
                if ttl:
                    expiry = datetime.now() + timedelta(seconds=ttl)
                elif self.default_ttl:
                    expiry = datetime.now() + timedelta(seconds=self.default_ttl)
                
                # Serialize and calculate size
                serialized = self._serialize_value(value)
                size_bytes = len(serialized)
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    timestamp=datetime.now(),
                    expiry=expiry,
                    access_count=1,
                    size_bytes=size_bytes,
                    tags=tags or []
                )
                
                # Store in local cache
                self.cache[key] = entry
                self.access_times[key] = datetime.now()
                
                # Store in Redis if available
                if self.redis_client:
                    try:
                        redis_ttl = ttl or self.default_ttl
                        self.redis_client.setex(
                            f"metamind:{key}", 
                            redis_ttl, 
                            serialized
                        )
                    except Exception as e:
                        logging.warning(f"Redis set error: {e}")
                
                return True
                
            except Exception as e:
                logging.error(f"Cache set error: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self.lock:
            deleted = False
            
            # Delete from local cache
            if key in self.cache:
                del self.cache[key]
                deleted = True
            
            if key in self.access_times:
                del self.access_times[key]
            
            # Delete from Redis
            if self.redis_client:
                try:
                    self.redis_client.delete(f"metamind:{key}")
                except Exception as e:
                    logging.warning(f"Redis delete error: {e}")
            
            return deleted
    
    def clear(self, tags: Optional[List[str]] = None) -> int:
        """Clear cache entries, optionally by tags."""
        with self.lock:
            if not tags:
                # Clear everything
                count = len(self.cache)
                self.cache.clear()
                self.access_times.clear()
                
                if self.redis_client:
                    try:
                        for key in self.redis_client.scan_iter(match="metamind:*"):
                            self.redis_client.delete(key)
                    except Exception as e:
                        logging.warning(f"Redis clear error: {e}")
                
                return count
            else:
                # Clear by tags
                to_delete = []
                for key, entry in self.cache.items():
                    if any(tag in entry.tags for tag in tags):
                        to_delete.append(key)
                
                for key in to_delete:
                    self.delete(key)
                
                return len(to_delete)
    
    def _update_hit_rate(self):
        """Update cache hit rate."""
        if self.total_requests > 0:
            self.hit_rate = self.cache_hits / self.total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            
            return {
                'entries': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': self.hit_rate,
                'total_requests': self.total_requests,
                'cache_hits': self.cache_hits,
                'total_size_bytes': total_size,
                'redis_available': self.redis_client is not None,
                'average_entry_size': total_size / len(self.cache) if self.cache else 0
            }

# Global cache instance
cache = AdvancedCache()

def cached(ttl: int = 3600, tags: List[str] = None, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:" + cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            start_time = time.time()
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                duration = time.time() - start_time
                logging.debug(f"Cache HIT for {func.__name__} ({duration:.3f}s)")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl, tags=tags)
            
            logging.debug(f"Cache MISS for {func.__name__} ({duration:.3f}s)")
            return result
        
        return wrapper
    return decorator

async def async_cached(ttl: int = 3600, tags: List[str] = None, key_prefix: str = ""):
    """Async version of cached decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:" + cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            start_time = time.time()
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                duration = time.time() - start_time
                logging.debug(f"Async Cache HIT for {func.__name__} ({duration:.3f}s)")
                return cached_result
            
            # Execute async function
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl, tags=tags)
            
            logging.debug(f"Async Cache MISS for {func.__name__} ({duration:.3f}s)")
            return result
        
        return wrapper
    return decorator

class ParallelProcessor:
    """Advanced parallel processing for CPU and I/O intensive tasks."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count() or 1)
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run function in thread pool for I/O intensive tasks."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
    
    async def run_in_process(self, func: Callable, *args, **kwargs) -> Any:
        """Run function in process pool for CPU intensive tasks."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args, **kwargs)
    
    async def map_parallel(self, func: Callable, items: List[Any], 
                          use_processes: bool = False) -> List[Any]:
        """Map function over items in parallel."""
        if use_processes:
            # CPU intensive - use processes
            tasks = [self.run_in_process(func, item) for item in items]
        else:
            # I/O intensive - use threads
            tasks = [self.run_in_thread(func, item) for item in items]
        
        return await asyncio.gather(*tasks)
    
    def close(self):
        """Close executor pools."""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

# Global parallel processor
parallel_processor = ParallelProcessor()

class PerformanceMonitor:
    """Monitor and track system performance."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()
    
    def record_metric(self, operation: str, duration: float, 
                     cache_hit: bool = False, 
                     memory_usage: float = 0.0, 
                     cpu_usage: float = 0.0):
        """Record a performance metric."""
        metric = PerformanceMetrics(
            operation=operation,
            duration=duration,
            cache_hit=cache_hit,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            timestamp=datetime.now()
        )
        self.metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-5000:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics:
            return {}
        
        # Group by operation
        by_operation = {}
        for metric in self.metrics:
            if metric.operation not in by_operation:
                by_operation[metric.operation] = []
            by_operation[metric.operation].append(metric)
        
        summary = {}
        for operation, metrics in by_operation.items():
            durations = [m.duration for m in metrics]
            cache_hits = sum(1 for m in metrics if m.cache_hit)
            
            summary[operation] = {
                'count': len(metrics),
                'avg_duration': np.mean(durations),
                'min_duration': np.min(durations),
                'max_duration': np.max(durations),
                'cache_hit_rate': cache_hits / len(metrics) if metrics else 0.0,
                'total_time': np.sum(durations)
            }
        
        return summary

# Global performance monitor
performance_monitor = PerformanceMonitor()

def performance_tracked(operation_name: str = None):
    """Decorator to track function performance."""
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Check if result came from cache (simple heuristic)
                cache_hit = hasattr(result, '_from_cache') if hasattr(result, '_from_cache') else False
                
                performance_monitor.record_metric(
                    operation=op_name,
                    duration=duration,
                    cache_hit=cache_hit
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record_metric(
                    operation=f"{op_name}_error",
                    duration=duration,
                    cache_hit=False
                )
                raise e
        
        return wrapper
    return decorator

async def batch_process_datasets(datasets: List[Tuple[str, pd.DataFrame]], 
                                processor_func: Callable,
                                batch_size: int = 4) -> List[Any]:
    """Process datasets in batches for optimal performance."""
    results = []
    
    # Process in batches to avoid overwhelming the system
    for i in range(0, len(datasets), batch_size):
        batch = datasets[i:i + batch_size]
        
        # Process batch in parallel
        batch_tasks = [
            parallel_processor.run_in_thread(processor_func, name, df)
            for name, df in batch
        ]
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Small delay between batches to prevent resource exhaustion
        if i + batch_size < len(datasets):
            await asyncio.sleep(0.1)
    
    return results

@lru_cache(maxsize=128)
def cached_dataframe_summary(df_hash: str, df_shape: Tuple[int, int]) -> Dict[str, Any]:
    """Cached summary for dataframes (using hash for identity)."""
    # This is a placeholder - actual implementation would need dataframe
    return {
        'rows': df_shape[0],
        'columns': df_shape[1],
        'cached': True
    }

def optimize_dataframe_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize dataframe for faster operations."""
    # Convert to more efficient dtypes where possible
    optimized_df = df.copy()
    
    for col in optimized_df.select_dtypes(include=['object']).columns:
        try:
            # Try to convert to category if it has few unique values
            if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                optimized_df[col] = optimized_df[col].astype('category')
        except:
            pass
    
    # Downcast numeric types
    for col in optimized_df.select_dtypes(include=['int64']).columns:
        try:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
        except:
            pass
    
    for col in optimized_df.select_dtypes(include=['float64']).columns:
        try:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        except:
            pass
    
    return optimized_df

class AsyncQueueProcessor:
    """Asynchronous queue processor for handling background tasks."""
    
    def __init__(self, max_workers: int = 4):
        self.queue = asyncio.Queue()
        self.workers = []
        self.max_workers = max_workers
        self.running = False
    
    async def add_task(self, coro, priority: int = 0):
        """Add a coroutine task to the queue."""
        await self.queue.put((priority, coro))
    
    async def worker(self, worker_id: int):
        """Worker coroutine to process queue items."""
        while self.running:
            try:
                # Get task from queue (with timeout to allow shutdown)
                priority, coro = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                
                # Execute the coroutine
                start_time = time.time()
                await coro
                duration = time.time() - start_time
                
                logging.debug(f"Worker {worker_id} completed task in {duration:.3f}s")
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
    
    async def start(self):
        """Start the queue processor."""
        self.running = True
        self.workers = [
            asyncio.create_task(self.worker(i))
            for i in range(self.max_workers)
        ]
    
    async def stop(self):
        """Stop the queue processor."""
        self.running = False
        
        # Wait for all workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
    
    async def wait_for_completion(self):
        """Wait for all queued tasks to complete."""
        await self.queue.join()

# Global async queue processor
async_queue_processor = AsyncQueueProcessor()

def get_performance_report() -> Dict[str, Any]:
    """Get comprehensive performance report."""
    return {
        'cache_stats': cache.get_stats(),
        'performance_summary': performance_monitor.get_performance_summary(),
        'system_info': {
            'cpu_count': mp.cpu_count(),
            'max_workers': parallel_processor.max_workers,
            'redis_available': REDIS_AVAILABLE and cache.redis_client is not None,
            'uptime_seconds': time.time() - performance_monitor.start_time
        }
    }

async def preload_common_operations():
    """Preload and cache common operations for faster startup."""
    logging.info("Preloading common operations...")
    
    # Preload ML models if they exist
    try:
        from ml_learning_system import learning_system
        await parallel_processor.run_in_thread(learning_system.load_models)
        logging.info("ML models preloaded")
    except Exception as e:
        logging.warning(f"Could not preload ML models: {e}")
    
    # Preload context templates
    try:
        from context_collector import ContextCollector
        collector = ContextCollector()
        cache.set("predefined_contexts", collector.predefined_contexts, ttl=86400)  # 24 hours
        logging.info("Context templates preloaded")
    except Exception as e:
        logging.warning(f"Could not preload context templates: {e}")

# Initialize performance optimization
async def initialize_performance_system():
    """Initialize the performance optimization system."""
    await async_queue_processor.start()
    await preload_common_operations()
    logging.info("Performance optimization system initialized")

def cleanup_performance_system():
    """Cleanup performance system resources."""
    try:
        parallel_processor.close()
        # Note: async_queue_processor.stop() should be called in async context
    except Exception as e:
        logging.warning(f"Error during performance system cleanup: {e}")

# Performance optimization context manager
class PerformanceContext:
    """Context manager for performance-optimized operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            performance_monitor.record_metric(
                operation=self.operation_name,
                duration=duration,
                cache_hit=False
            )
            
            if exc_type:
                logging.error(f"Performance context {self.operation_name} failed: {exc_val}")
            else:
                logging.debug(f"Performance context {self.operation_name} completed in {duration:.3f}s")
