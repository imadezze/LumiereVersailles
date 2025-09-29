#!/usr/bin/env python3
"""
Monitor the research agent progress and show live results
"""

import os
import json
import time
from datetime import datetime

def monitor_research_progress():
    """Monitor research progress and show live updates"""
    
    print("🔍 MONITORING VERSAILLES RESEARCH AGENT")
    print("=" * 50)
    
    # Look for JSONL files
    project_dir = '/Users/abedattal/Documents/projects/LumiereVersailles'
    
    while True:
        try:
            # Find the most recent research file
            jsonl_files = [f for f in os.listdir(project_dir) if f.startswith('versailles_research_') and f.endswith('.jsonl')]
            
            if jsonl_files:
                latest_file = max(jsonl_files, key=lambda f: os.path.getctime(os.path.join(project_dir, f)))
                filepath = os.path.join(project_dir, latest_file)
                
                # Count lines in JSONL file
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                print(f"\r📊 Progress: {len(lines)} research items collected", end='', flush=True)
                
                # Show latest few items
                if len(lines) > 0:
                    print(f"\n📝 Latest research items:")
                    for line in lines[-3:]:  # Show last 3 items
                        try:
                            item = json.loads(line)
                            category = item.get('category', 'unknown').upper()
                            title = item.get('title', '')[:60] + '...'
                            print(f"   [{category}] {title}")
                        except:
                            pass
                    print("-" * 50)
            else:
                print(f"\r⏳ Waiting for research results...", end='', flush=True)
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_research_progress()
