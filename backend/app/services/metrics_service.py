"""
Metrics Service for monitoring system performance and health
Provides structured logging, metrics tracking, and performance monitoring
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from loguru import logger
import json


@dataclass
class AIMetrics:
    """Metrics for AI service performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    # Latency tracking (in seconds)
    total_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0

    # Confidence tracking
    total_confidence: float = 0.0
    low_confidence_count: int = 0  # confidence < 0.6

    # Fallback tracking
    fallback_count: int = 0

    # Time window
    window_start: datetime = field(default_factory=datetime.now)

    def record_request(
        self,
        success: bool,
        latency: float,
        confidence: Optional[float] = None,
        timeout: bool = False,
        from_cache: bool = False,
        used_fallback: bool = False
    ):
        """Record a single AI request"""
        self.total_requests += 1

        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if timeout:
            self.timeout_requests += 1
            self.failed_requests += 1
            return

        if success:
            self.successful_requests += 1

            # Track latency
            self.total_latency += latency
            self.min_latency = min(self.min_latency, latency)
            self.max_latency = max(self.max_latency, latency)

            # Track confidence
            if confidence is not None:
                self.total_confidence += confidence
                if confidence < 0.6:
                    self.low_confidence_count += 1
        else:
            self.failed_requests += 1

        if used_fallback:
            self.fallback_count += 1

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def average_latency(self) -> float:
        """Calculate average latency in seconds"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_confidence / self.successful_requests

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

    @property
    def timeout_rate(self) -> float:
        """Calculate timeout rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.timeout_requests / self.total_requests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'timeout_requests': self.timeout_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'success_rate': round(self.success_rate, 2),
            'cache_hit_rate': round(self.cache_hit_rate, 2),
            'timeout_rate': round(self.timeout_rate, 2),
            'average_latency_seconds': round(self.average_latency, 2),
            'min_latency_seconds': round(self.min_latency, 2) if self.min_latency != float('inf') else 0,
            'max_latency_seconds': round(self.max_latency, 2),
            'average_confidence': round(self.average_confidence, 2),
            'low_confidence_count': self.low_confidence_count,
            'fallback_count': self.fallback_count,
            'window_start': self.window_start.isoformat()
        }


@dataclass
class TransactionMetrics:
    """Metrics for transaction processing"""
    total_created: int = 0
    total_validated: int = 0
    total_corrected: int = 0

    # By category
    by_category: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # By payment method
    by_payment_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Time window
    window_start: datetime = field(default_factory=datetime.now)

    def record_transaction(
        self,
        category: str,
        payment_method: str,
        action: str = 'created'
    ):
        """Record a transaction"""
        if action == 'created':
            self.total_created += 1
        elif action == 'validated':
            self.total_validated += 1
        elif action == 'corrected':
            self.total_corrected += 1

        self.by_category[category] += 1
        self.by_payment_method[payment_method] += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_created': self.total_created,
            'total_validated': self.total_validated,
            'total_corrected': self.total_corrected,
            'by_category': dict(self.by_category),
            'by_payment_method': dict(self.by_payment_method),
            'window_start': self.window_start.isoformat()
        }


class MetricsService:
    """Service for tracking and reporting system metrics"""

    def __init__(self):
        self.ai_metrics = AIMetrics()
        self.transaction_metrics = TransactionMetrics()
        self._last_reset = datetime.now()
        self.reset_interval = timedelta(hours=1)  # Reset metrics every hour

    def check_reset(self):
        """Check if metrics should be reset based on time window"""
        if datetime.now() - self._last_reset > self.reset_interval:
            logger.info("Resetting metrics window")
            self.reset_metrics()

    def reset_metrics(self):
        """Reset all metrics (called periodically)"""
        # Log current metrics before reset
        self.log_metrics_summary()

        self.ai_metrics = AIMetrics()
        self.transaction_metrics = TransactionMetrics()
        self._last_reset = datetime.now()

    def log_metrics_summary(self):
        """Log a summary of current metrics"""
        logger.info("=" * 80)
        logger.info("METRICS SUMMARY")
        logger.info("=" * 80)

        # AI Metrics
        logger.info("AI Service Performance:")
        logger.info(f"  Total Requests: {self.ai_metrics.total_requests}")
        logger.info(f"  Success Rate: {self.ai_metrics.success_rate:.2f}%")
        logger.info(f"  Cache Hit Rate: {self.ai_metrics.cache_hit_rate:.2f}%")
        logger.info(f"  Timeout Rate: {self.ai_metrics.timeout_rate:.2f}%")
        logger.info(f"  Avg Latency: {self.ai_metrics.average_latency:.2f}s")
        logger.info(f"  Avg Confidence: {self.ai_metrics.average_confidence:.2f}")
        logger.info(f"  Fallback Count: {self.ai_metrics.fallback_count}")

        # Transaction Metrics
        logger.info("\nTransaction Processing:")
        logger.info(f"  Total Created: {self.transaction_metrics.total_created}")
        logger.info(f"  Total Validated: {self.transaction_metrics.total_validated}")
        logger.info(f"  Total Corrected: {self.transaction_metrics.total_corrected}")

        if self.transaction_metrics.by_category:
            logger.info("\n  By Category:")
            for cat, count in sorted(self.transaction_metrics.by_category.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"    {cat}: {count}")

        if self.transaction_metrics.by_payment_method:
            logger.info("\n  By Payment Method:")
            for method, count in sorted(self.transaction_metrics.by_payment_method.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"    {method}: {count}")

        logger.info("=" * 80)

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status with metrics"""
        self.check_reset()

        # Determine overall health
        health_status = "healthy"
        issues = []

        # Check AI service health
        if self.ai_metrics.total_requests > 10:  # Only check if we have enough data
            if self.ai_metrics.timeout_rate > 30:
                health_status = "degraded"
                issues.append(f"High timeout rate: {self.ai_metrics.timeout_rate:.1f}%")

            if self.ai_metrics.success_rate < 70:
                health_status = "unhealthy"
                issues.append(f"Low success rate: {self.ai_metrics.success_rate:.1f}%")

            if self.ai_metrics.average_latency > 30:
                health_status = "degraded"
                issues.append(f"High latency: {self.ai_metrics.average_latency:.1f}s")

        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self._last_reset).total_seconds(),
            'issues': issues,
            'ai_metrics': self.ai_metrics.to_dict(),
            'transaction_metrics': self.transaction_metrics.to_dict()
        }


# Global metrics service instance
_metrics_service = MetricsService()


def get_metrics_service() -> MetricsService:
    """Get the global metrics service instance"""
    return _metrics_service
