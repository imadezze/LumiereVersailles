#!/usr/bin/env python3
"""
Startup script for the Versailles Chatbot frontend
"""
import os
import sys
import subprocess
from pathlib import Path

def check_node():
    """Check if Node.js and npm are installed"""
    try:
        # Check Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
        else:
            print("❌ Node.js is not installed")
            return False

        # Check npm
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm version: {result.stdout.strip()}")
        else:
            print("❌ npm is not installed")
            return False

        return True

    except FileNotFoundError:
        print("❌ Node.js or npm is not installed")
        print("Please install Node.js from https://nodejs.org/")
        return False

def install_dependencies():
    """Install npm dependencies"""
    frontend_dir = Path(__file__).parent / "frontend"

    if not (frontend_dir / "package.json").exists():
        print("❌ package.json not found in frontend directory")
        return False

    print("📦 Installing frontend dependencies...")
    try:
        os.chdir(frontend_dir)
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_frontend():
    """Start the React frontend"""
    if not check_node():
        return False

    frontend_dir = Path(__file__).parent / "frontend"

    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        if not install_dependencies():
            return False

    print("🚀 Starting Versailles Chatbot Frontend...")
    print("🌐 Frontend will be available at: http://localhost:3000")
    print("🔗 Make sure the backend is running at: http://localhost:8000")
    print()

    try:
        os.chdir(frontend_dir)
        subprocess.run(['npm', 'start'], check=True)

    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True

if __name__ == "__main__":
    start_frontend()