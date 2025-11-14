#!/usr/bin/env python3
"""
Enhanced Visualizations for GitHub API Rate Limit Tester
Creates multiple engaging visualizations for the README.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

# Set up professional styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_sample_visualizations():
    """Create sample visualizations for demonstration purposes."""
    
    # Create realistic sample data
    np.random.seed(42)
    
    # Sample data structure
    n_requests = 50
    patterns = ['Burst'] * 15 + ['Sustained'] * 20 + ['Delayed'] * 15
    
    # Generate realistic response times
    response_times = []
    for i, pattern in enumerate(patterns):
        if pattern == 'Burst':
            base_time = 100 + np.random.normal(0, 20)
            if i < 5:
                response_times.append(max(50, base_time))
            else:
                response_times.append(max(150, base_time + np.random.normal(50, 30)))
        elif pattern == 'Sustained':
            response_times.append(120 + np.random.normal(0, 25) + (i-15)*0.5)
        else:
            response_times.append(180 + np.random.normal(0, 15))
    
    # Generate success/failure data
    success = [True] * 45 + [False] * 5
    np.random.shuffle(success)
    
    # Rate limit data
    rate_limit_total = 5000
    rate_limit_remaining = [rate_limit_total - i*100 for i in range(n_requests)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'request_number': range(1, n_requests + 1),
        'pattern': patterns,
        'response_time_ms': response_times,
        'success': success,
        'rate_limit_remaining': rate_limit_remaining,
        'rate_limit_limit': [rate_limit_total] * n_requests
    })
    
    # Create visualizations directory
    os.makedirs('visualizations', exist_ok=True)
    
    print("Creating enhanced visualizations...")
    
    # 1. Performance Dashboard
    create_performance_dashboard(df)
    
    # 2. Pattern Comparison
    create_pattern_comparison(df)
    
    # 3. Rate Limit Analysis
    create_rate_limit_analysis(df)
    
    # 4. Success Metrics
    create_success_metrics(df)
    
    print("✅ All visualizations created in 'visualizations/' directory")


def create_performance_dashboard(df):
    """Create a comprehensive performance dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('GitHub API Performance Dashboard', fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Response Time Trend
    axes[0, 0].plot(df['request_number'], df['response_time_ms'], 
                   linewidth=2, marker='o', markersize=3, alpha=0.8)
    axes[0, 0].set_title('Response Time Trend', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Request Sequence')
    axes[0, 0].set_ylabel('Response Time (ms)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Rate Limit Usage
    rate_limit_used = df['rate_limit_limit'].iloc[0] - df['rate_limit_remaining']
    rate_limit_pct = (rate_limit_used / df['rate_limit_limit'].iloc[0]) * 100
    
    axes[0, 1].plot(df['request_number'], rate_limit_pct, 
                   linewidth=2, marker='s', markersize=3)
    axes[0, 1].set_title('Rate Limit Usage Over Time', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Request Sequence')
    axes[0, 1].set_ylabel('Rate Limit Used (%)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_ylim(0, 100)
    
    # Plot 3: Success Rate Over Time
    df['success_cumulative'] = df['success'].cumsum() / (df.index + 1) * 100
    axes[1, 0].plot(df['request_number'], df['success_cumulative'], 
                   linewidth=2)
    axes[1, 0].set_title('Cumulative Success Rate', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Request Sequence')
    axes[1, 0].set_ylabel('Success Rate (%)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_ylim(0, 100)
    
    # Plot 4: Response Time Distribution
    axes[1, 1].hist(df['response_time_ms'], bins=12, alpha=0.7)
    axes[1, 1].set_title('Response Time Distribution', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Response Time (ms)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/performance_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_pattern_comparison(df):
    """Create visualizations comparing different request patterns."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Request Pattern Performance Comparison', fontsize=18, fontweight='bold')
    
    # Plot 1: Response Times by Pattern
    pattern_data = [df[df['pattern'] == p]['response_time_ms'] for p in df['pattern'].unique()]
    
    box_plot = axes[0, 0].boxplot(pattern_data, labels=df['pattern'].unique(), patch_artist=True)
    axes[0, 0].set_title('Response Time Distribution by Pattern', fontsize=14, fontweight='bold')
    axes[0, 0].set_ylabel('Response Time (ms)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Success Rate by Pattern
    success_rates = []
    for pattern in df['pattern'].unique():
        pattern_df = df[df['pattern'] == pattern]
        success_rate = pattern_df['success'].mean() * 100
        success_rates.append(success_rate)
    
    bars = axes[0, 1].bar(df['pattern'].unique(), success_rates, alpha=0.8)
    axes[0, 1].set_title('Success Rate by Pattern', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].set_ylim(0, 100)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Pattern Timeline
    for pattern in df['pattern'].unique():
        pattern_data = df[df['pattern'] == pattern]
        axes[1, 0].scatter(pattern_data['request_number'], 
                          pattern_data['response_time_ms'], 
                          label=pattern, alpha=0.7)
    
    axes[1, 0].set_title('Response Times by Pattern Over Time', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Request Sequence')
    axes[1, 0].set_ylabel('Response Time (ms)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Pattern Performance Summary
    metrics = ['Avg Response Time', 'Success Rate', 'Requests']
    pattern_metrics = {}
    
    for pattern in df['pattern'].unique():
        pattern_df = df[df['pattern'] == pattern]
        pattern_metrics[pattern] = [
            pattern_df['response_time_ms'].mean(),
            pattern_df['success'].mean() * 100,
            len(pattern_df)
        ]
    
    x = np.arange(len(metrics))
    width = 0.25
    multiplier = 0
    
    for pattern, metrics_data in pattern_metrics.items():
        offset = width * multiplier
        axes[1, 1].bar(x + offset, metrics_data, width, label=pattern, alpha=0.8)
        multiplier += 1
    
    axes[1, 1].set_title('Pattern Performance Summary', fontsize=14, fontweight='bold')
    axes[1, 1].set_xticks(x + width)
    axes[1, 1].set_xticklabels(metrics)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/pattern_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_rate_limit_analysis(df):
    """Create visualizations focused on rate limiting."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Rate Limit Analysis', fontsize=18, fontweight='bold')
    
    # Calculate rate limit usage
    total_limit = df['rate_limit_limit'].iloc[0]
    df['rate_limit_used'] = total_limit - df['rate_limit_remaining']
    df['rate_limit_pct'] = (df['rate_limit_used'] / total_limit) * 100
    
    # Plot 1: Rate Limit Usage Over Time
    axes[0, 0].plot(df['request_number'], df['rate_limit_pct'], 
                   linewidth=2, marker='o', markersize=3)
    axes[0, 0].set_title('Rate Limit Usage Over Time', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Request Sequence')
    axes[0, 0].set_ylabel('Rate Limit Used (%)')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_ylim(0, 100)
    
    # Plot 2: Rate Limit Allocation
    requests_per_limit = len(df) / total_limit * 100
    limit_data = [requests_per_limit, 100 - requests_per_limit]
    labels = ['Used by Test', 'Remaining']
    
    axes[0, 1].pie(limit_data, labels=labels, autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Rate Limit Allocation', fontsize=14, fontweight='bold')
    
    # Plot 3: Rate Limit vs Response Time
    scatter = axes[1, 0].scatter(df['rate_limit_pct'], df['response_time_ms'], 
                               c=df['request_number'], alpha=0.7)
    axes[1, 0].set_title('Rate Limit Usage vs Response Time', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Rate Limit Used (%)')
    axes[1, 0].set_ylabel('Response Time (ms)')
    axes[1, 0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes[1, 0], label='Request Sequence')
    
    # Plot 4: Consumption Rate
    df['consumption_rate'] = df['rate_limit_pct'] / df['request_number']
    
    axes[1, 1].plot(df['request_number'], df['consumption_rate'], 
                   linewidth=2, marker='s', markersize=3)
    axes[1, 1].set_title('Rate Limit Consumption Rate', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Request Sequence')
    axes[1, 1].set_ylabel('Consumption Rate (%/request)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/rate_limit_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_success_metrics(df):
    """Create visualizations focused on success metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Success Metrics Analysis', fontsize=18, fontweight='bold')
    
    # Plot 1: Success/Failure Distribution
    success_count = df['success'].sum()
    failure_count = len(df) - success_count
    
    axes[0, 0].bar(['Success', 'Failure'], [success_count, failure_count], 
                  color=['green', 'red'], alpha=0.7)
    axes[0, 0].set_title('Request Success/Failure Distribution', fontsize=14, fontweight='bold')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Response Time by Success
    success_times = df[df['success']]['response_time_ms']
    failure_times = df[~df['success']]['response_time_ms']
    
    axes[0, 1].boxplot([success_times, failure_times], 
                      labels=['Success', 'Failure'], patch_artist=True)
    axes[0, 1].set_title('Response Time by Outcome', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('Response Time (ms)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Success Rate Over Time
    df['success_rolling'] = df['success'].rolling(window=5).mean() * 100
    axes[1, 0].plot(df['request_number'], df['success_rolling'], linewidth=2)
    axes[1, 0].set_title('Rolling Success Rate (Window=5)', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Request Sequence')
    axes[1, 0].set_ylabel('Success Rate (%)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Performance Summary
    metrics = ['Total Requests', 'Success Rate', 'Avg Response Time', 'Rate Limit Used']
    values = [
        len(df),
        df['success'].mean() * 100,
        df['response_time_ms'].mean(),
        df['rate_limit_pct'].iloc[-1]
    ]
    
    bars = axes[1, 1].bar(metrics, values, alpha=0.7)
    axes[1, 1].set_title('Performance Summary', fontsize=14, fontweight='bold')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations/success_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    create_sample_visualizations()