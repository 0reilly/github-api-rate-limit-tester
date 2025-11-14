#!/usr/bin/env python3
"""
GitHub API Rate Limit Tester

This script tests GitHub API rate limits and response patterns by making requests
to the GitHub API with different patterns (burst, sustained, delayed).

Usage:
  export GITHUB_TOKEN=your_token_here
  python3 github_api_tester_clean.py

Features:
- Tests different request patterns
- Analyzes response times, status codes, and rate limit headers
- Creates visualizations of request patterns and response times
- Generates a summary report with findings
"""

import requests
import time
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from typing import List, Dict, Any, Optional
import os


class GitHubAPITester:
    def __init__(self, token: str = None, base_url: str = "https://api.github.com"):
        """
        Initialize the GitHub API tester.
        
        Args:
            token: GitHub personal access token (optional, will use GITHUB_TOKEN env var if not provided)
            base_url: GitHub API base URL
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Either pass it as an argument or set GITHUB_TOKEN environment variable.")
            
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-API-Tester/1.0"
        })
        self.results = []
        
    def make_request(self, endpoint: str = "/users/octocat") -> Dict[str, Any]:
        """
        Make a single request to the GitHub API and collect metrics.
        
        Args:
            endpoint: API endpoint to test
            
        Returns:
            Dictionary containing request metrics
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.get(url)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Extract rate limit information
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
            rate_limit_limit = response.headers.get('X-RateLimit-Limit', 'N/A')
            rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'N/A')
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'rate_limit_remaining': rate_limit_remaining,
                'rate_limit_limit': rate_limit_limit,
                'rate_limit_reset': rate_limit_reset,
                'success': response.status_code == 200,
                'error': None
            }
            
            if response.status_code != 200:
                result['error'] = response.text[:200]  # Truncate error message
                
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            result = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'status_code': 0,
                'response_time_ms': response_time,
                'rate_limit_remaining': 'N/A',
                'rate_limit_limit': 'N/A',
                'rate_limit_reset': 'N/A',
                'success': False,
                'error': str(e)
            }
            
        self.results.append(result)
        return result
    
    def test_burst_pattern(self, num_requests: int = 10, endpoint: str = "/users/octocat") -> List[Dict[str, Any]]:
        """
        Test burst pattern - make multiple requests in quick succession.
        
        Args:
            num_requests: Number of requests to make
            endpoint: API endpoint to test
            
        Returns:
            List of request results
        """
        print(f"Testing burst pattern with {num_requests} requests...")
        results = []
        
        for i in range(num_requests):
            print(f"  Request {i+1}/{num_requests}")
            result = self.make_request(endpoint)
            results.append(result)
            
        return results
    
    def test_sustained_pattern(self, num_requests: int = 20, interval: float = 0.5, 
                              endpoint: str = "/users/octocat") -> List[Dict[str, Any]]:
        """
        Test sustained pattern - make requests at regular intervals.
        
        Args:
            num_requests: Number of requests to make
            interval: Time between requests in seconds
            endpoint: API endpoint to test
            
        Returns:
            List of request results
        """
        print(f"Testing sustained pattern with {num_requests} requests at {interval}s intervals...")
        results = []
        
        for i in range(num_requests):
            print(f"  Request {i+1}/{num_requests}")
            result = self.make_request(endpoint)
            results.append(result)
            
            if i < num_requests - 1:  # Don't sleep after the last request
                time.sleep(interval)
                
        return results
    
    def test_delayed_pattern(self, num_requests: int = 15, initial_delay: float = 1.0,
                           delay_increment: float = 0.5, endpoint: str = "/users/octocat") -> List[Dict[str, Any]]:
        """
        Test delayed pattern - increasing delays between requests.
        
        Args:
            num_requests: Number of requests to make
            initial_delay: Initial delay in seconds
            delay_increment: How much to increase delay each time
            endpoint: API endpoint to test
            
        Returns:
            List of request results
        """
        print(f"Testing delayed pattern with {num_requests} requests and increasing delays...")
        results = []
        current_delay = initial_delay
        
        for i in range(num_requests):
            print(f"  Request {i+1}/{num_requests} (delay: {current_delay:.1f}s)")
            result = self.make_request(endpoint)
            results.append(result)
            
            if i < num_requests - 1:  # Don't sleep after the last request
                time.sleep(current_delay)
                current_delay += delay_increment
                
        return results
    
    def save_results(self, filename: str = "api_test_results.csv"):
        """
        Save test results to CSV file.
        
        Args:
            filename: Output CSV filename
        """
        if not self.results:
            print("No results to save.")
            return
            
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = self.results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
            
        print(f"Results saved to {filename}")
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the collected test results.
        
        Returns:
            Dictionary with analysis metrics
        """
        if not self.results:
            return {}
            
        df = pd.DataFrame(self.results)
        
        # Basic statistics
        successful_requests = df[df['success'] == True]
        failed_requests = df[df['success'] == False]
        
        analysis = {
            'total_requests': len(df),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(df) * 100,
            'avg_response_time_ms': df['response_time_ms'].mean(),
            'min_response_time_ms': df['response_time_ms'].min(),
            'max_response_time_ms': df['response_time_ms'].max(),
            'std_response_time_ms': df['response_time_ms'].std(),
            'status_code_counts': df['status_code'].value_counts().to_dict()
        }
        
        # Rate limit analysis (only for successful requests with rate limit data)
        rate_limit_data = df[df['rate_limit_remaining'] != 'N/A']
        if not rate_limit_data.empty:
            rate_limit_data['rate_limit_remaining'] = pd.to_numeric(rate_limit_data['rate_limit_remaining'], errors='coerce')
            analysis['final_rate_limit_remaining'] = rate_limit_data['rate_limit_remaining'].iloc[-1]
            analysis['rate_limit_usage'] = 100 - (analysis['final_rate_limit_remaining'] / int(rate_limit_data['rate_limit_limit'].iloc[0]) * 100)
        
        return analysis
    
    def create_visualizations(self):
        """Create visualizations of the test results."""
        if not self.results:
            print("No results to visualize.")
            return
            
        df = pd.DataFrame(self.results)
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        df['request_number'] = range(1, len(df) + 1)
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Response times over time
        axes[0, 0].plot(df['request_number'], df['response_time_ms'], marker='o', linewidth=2, markersize=4)
        axes[0, 0].set_title('Response Times Over Request Sequence', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Request Number')
        axes[0, 0].set_ylabel('Response Time (ms)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Status code distribution
        status_counts = df['status_code'].value_counts()
        axes[0, 1].bar(status_counts.index.astype(str), status_counts.values, color=['green' if x == 200 else 'red' for x in status_counts.index])
        axes[0, 1].set_title('Status Code Distribution', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Status Code')
        axes[0, 1].set_ylabel('Count')
        
        # Plot 3: Success rate over time (rolling window)
        df['success_cumulative'] = df['success'].cumsum() / (df.index + 1) * 100
        axes[1, 0].plot(df['request_number'], df['success_cumulative'], linewidth=2, color='blue')
        axes[1, 0].set_title('Cumulative Success Rate', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Request Number')
        axes[1, 0].set_ylabel('Success Rate (%)')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim(0, 100)
        
        # Plot 4: Response time distribution
        axes[1, 1].hist(df['response_time_ms'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[1, 1].set_title('Response Time Distribution', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Response Time (ms)')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('api_test_visualization.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Visualizations saved to 'api_test_visualization.png'")
    
    def generate_report(self, analysis: Dict[str, Any]):
        """Generate a summary report of the test findings."""
        report = f"""
GitHub API Rate Limit Test Report
================================

Test Summary
------------
Total Requests: {analysis.get('total_requests', 0)}
Successful Requests: {analysis.get('successful_requests', 0)}
Failed Requests: {analysis.get('failed_requests', 0)}
Success Rate: {analysis.get('success_rate', 0):.2f}%

Performance Metrics
-------------------
Average Response Time: {analysis.get('avg_response_time_ms', 0):.2f} ms
Minimum Response Time: {analysis.get('min_response_time_ms', 0):.2f} ms
Maximum Response Time: {analysis.get('max_response_time_ms', 0):.2f} ms
Response Time Std Dev: {analysis.get('std_response_time_ms', 0):.2f} ms

Status Code Distribution
------------------------
"""
        
        for status_code, count in analysis.get('status_code_counts', {}).items():
            report += f"Status {status_code}: {count} requests\n"
            
        if 'final_rate_limit_remaining' in analysis:
            report += f"\nRate Limit Analysis\n-------------------\n"
            report += f"Final Rate Limit Remaining: {analysis['final_rate_limit_remaining']}\n"
            report += f"Rate Limit Usage: {analysis['rate_limit_usage']:.2f}%\n"
        
        report += f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        with open('api_test_report.txt', 'w') as f:
            f.write(report)
            
        print("Report saved to 'api_test_report.txt'")
        print(report)


def main():
    """Main function to run the API tests."""
    # Get token from environment variable
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
        return
    
    # Initialize the tester
    tester = GitHubAPITester(token)
    
    print("Starting GitHub API Rate Limit Tests...")
    print("=" * 50)
    
    # Test different patterns
    print("\n1. Testing Burst Pattern (10 rapid requests)")
    print("-" * 40)
    tester.test_burst_pattern(num_requests=10)
    
    print("\n2. Testing Sustained Pattern (20 requests at 0.5s intervals)")
    print("-" * 40)
    tester.test_sustained_pattern(num_requests=20, interval=0.5)
    
    print("\n3. Testing Delayed Pattern (15 requests with increasing delays)")
    print("-" * 40)
    tester.test_delayed_pattern(num_requests=15, initial_delay=1.0, delay_increment=0.5)
    
    # Save and analyze results
    print("\n" + "=" * 50)
    print("Analyzing Results...")
    
    tester.save_results("github_api_test_results.csv")
    analysis = tester.analyze_results()
    tester.create_visualizations()
    tester.generate_report(analysis)
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
    print("Check the following files:")
    print("- github_api_test_results.csv (raw data)")
    print("- api_test_visualization.png (charts)")
    print("- api_test_report.txt (summary)")


if __name__ == "__main__":
    main()