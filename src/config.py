"""
Centralized Configuration for Revenium FinOps Showcase

This module contains all configuration constants used throughout the application.
"""

# Data Generation Configuration
TARGET_SIZE_MB = 50.0  # Target size for simulated data CSV file in megabytes
DATA_CSV_PATH = 'data/simulated_calls.csv'  # Default path to CSV data file
REPORT_DIR = 'reports/html'  # Default directory for HTML reports

# Viewer Configuration
VIEWER_PORT = 8000  # HTTP server port for the live viewer

# Performance Thresholds
SLA_THRESHOLD_MS = 2000  # SLA threshold in milliseconds for latency analysis
P95_THRESHOLD_MS = 1500  # P95 latency threshold
P99_THRESHOLD_MS = 2500  # P99 latency threshold

# Profitability Thresholds
HIGH_MARGIN_THRESHOLD_PCT = 50.0  # Customers above this margin are "high margin"
MEDIUM_MARGIN_THRESHOLD_PCT = 20.0  # Customers above this are "medium margin"
LOW_MARGIN_THRESHOLD_PCT = 0.0  # Below this are "low margin"
UNPROFITABLE_THRESHOLD_PCT = 0.0  # Below this are unprofitable

# Cost Analysis Thresholds
HIGH_COST_THRESHOLD_USD = 100.0  # Daily cost threshold for high spenders
ANOMALY_MULTIPLIER = 3.0  # Multiplier for anomaly detection (3x normal)

# Efficiency Thresholds
EFFICIENCY_HIGH_THRESHOLD = 0.8  # 80%+ efficiency is "high"
EFFICIENCY_MEDIUM_THRESHOLD = 0.6  # 60-80% efficiency is "medium"
# Below 60% is "low"

# Feature Analysis
MIN_FEATURE_CALLS = 100  # Minimum calls for feature to be considered in analysis

# Customer Archetypes (expected distribution)
CUSTOMER_ARCHETYPES = {
    'light': 0.70,  # 70% light users
    'power': 0.20,  # 20% power users
    'heavy': 0.10   # 10% heavy users
}

# Subscription Tiers
SUBSCRIPTION_TIERS = {
    'starter': {'price': 49, 'weight': 0.40},
    'pro': {'price': 199, 'weight': 0.45},
    'enterprise': {'price': 999, 'weight': 0.15}
}

# Provider Distribution (market share simulation)
PROVIDER_WEIGHTS = {
    'openai': 0.40,
    'anthropic': 0.25,
    'google': 0.15,
    'aws-bedrock': 0.10,
    'azure': 0.07,
    'mistral': 0.02,
    'cohere': 0.01
}

# Regional Distribution
REGIONS = ['us-east', 'us-west', 'eu-west', 'ap-southeast']

# Products
PRODUCTS = ['saas-platform', 'api-service', 'mobile-app']

# Features
FEATURES = ['chat', 'summarization', 'translation', 'code-generation', 'analysis']

# Simulation Configuration
DEFAULT_CALLS_PER_HOUR = 1000  # Default rate for simulators
BATCH_SIZE = 5000  # Number of calls to write at once for performance
