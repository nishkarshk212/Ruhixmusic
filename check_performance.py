#!/usr/bin/env python3
"""
Bot Performance Diagnostic Tool
Checks various aspects of your bot setup to identify potential slowdowns
"""

import os
import sys
import time
from pathlib import Path

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_check(name, status, message=""):
    icon = "✓" if status else "✗"
    color = Colors.OKGREEN if status else Colors.FAIL
    print(f"{color}{icon} {name}{Colors.ENDC}")
    if message:
        print(f"  {message}")

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Environment Configuration Check")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_check(".env file exists", False, "Create a .env file with your credentials")
        return False
    
    print_check(".env file exists", True)
    
    # Read required variables
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'MONGO_DB_URI', 'STRING_SESSION']
    optional_vars = ['GPT_API', 'DEEP_API', 'HEROKU_APP_NAME', 'HEROKU_API_KEY']
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    missing_required = []
    for var in required_vars:
        if var not in content:
            missing_required.append(var)
            print_check(f"{var} configured", False)
        else:
            print_check(f"{var} configured", True)
    
    if missing_required:
        print(f"\n{Colors.WARNING}⚠ Missing required variables: {', '.join(missing_required)}{Colors.ENDC}")
        return False
    
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("Dependencies Check")
    
    required_packages = [
        'pyrogram',
        'pytgcalls',
        'motor',
        'aiohttp',
        'asyncio'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print_check(f"{package} installed", True)
        except ImportError:
            print_check(f"{package} installed", False)
            missing.append(package)
    
    if missing:
        print(f"\n{Colors.WARNING}Install missing packages with: pip3 install -r requirements.txt{Colors.ENDC}")
        return False
    
    return True

def check_network_latency():
    """Test network connectivity to Telegram servers"""
    print_header("Network Latency Test")
    
    try:
        import socket
        
        # Test connection to Telegram API
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('api.telegram.org', 443))
        latency = (time.time() - start) * 1000
        sock.close()
        
        if result == 0:
            print_check("Telegram API reachable", True, f"Latency: {latency:.2f}ms")
            if latency < 200:
                print(f"{Colors.OKGREEN}Network connection is excellent{Colors.ENDC}")
            elif latency < 500:
                print(f"{Colors.OKGREEN}Network connection is good{Colors.ENDC}")
            elif latency < 1000:
                print(f"{Colors.WARNING}Network connection is acceptable{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Network connection is slow - may cause delays{Colors.ENDC}")
            return True
        else:
            print_check("Telegram API reachable", False, "Cannot connect to Telegram servers")
            return False
            
    except Exception as e:
        print_check("Network test", False, str(e))
        return False

def check_mongodb_connection():
    """Test MongoDB connection"""
    print_header("MongoDB Connection Test")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        mongo_uri = os.getenv('MONGO_DB_URI')
        if not mongo_uri:
            print_check("MongoDB URI configured", False, "MONGO_DB_URI not found in .env")
            return False
        
        print_check("MongoDB URI configured", True)
        
        # Try to connect
        from motor.motor_asyncio import AsyncIOMotorClient
        start = time.time()
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        latency = (time.time() - start) * 1000
        
        print_check("MongoDB connection", True, f"Latency: {latency:.2f}ms")
        
        if latency < 100:
            print(f"{Colors.OKGREEN}MongoDB connection is excellent{Colors.ENDC}")
        elif latency < 300:
            print(f"{Colors.OKGREEN}MongoDB connection is good{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}MongoDB connection may cause delays{Colors.ENDC}")
        
        client.close()
        return True
        
    except Exception as e:
        print_check("MongoDB connection", False, str(e))
        return False

def check_system_resources():
    """Check available system resources"""
    print_header("System Resources Check")
    
    try:
        import psutil
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print_check(f"CPU Usage: {cpu_percent}%", cpu_percent < 80)
        if cpu_percent > 80:
            print(f"{Colors.WARNING}⚠ High CPU usage detected{Colors.ENDC}")
        
        # Memory Usage
        memory = psutil.virtual_memory()
        mem_percent = memory.percent
        print_check(f"Memory Usage: {mem_percent}%", mem_percent < 90)
        if mem_percent > 90:
            print(f"{Colors.WARNING}⚠ Low memory available{Colors.ENDC}")
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        print_check(f"Disk Usage: {disk_percent}%", disk_percent < 90)
        if disk_percent > 90:
            print(f"{Colors.WARNING}⚠ Low disk space{Colors.ENDC}")
        
        return cpu_percent < 80 and mem_percent < 90 and disk_percent < 90
        
    except ImportError:
        print_check("psutil not installed", False, "Install with: pip3 install psutil")
        return False
    except Exception as e:
        print_check("System resources check", False, str(e))
        return False

def check_optimization_status():
    """Check if optimizations have been applied"""
    print_header("Optimization Status Check")
    
    optimizations = []
    
    # Check bot.py for workers parameter
    try:
        with open('ANNIEMUSIC/core/bot.py', 'r') as f:
            content = f.read()
            if 'workers=8' in content and 'in_memory=False' in content:
                print_check("Bot workers optimized", True)
                optimizations.append(True)
            else:
                print_check("Bot workers optimized", False, "Run optimization script first")
                optimizations.append(False)
    except FileNotFoundError:
        print_check("Bot configuration", False, "File not found")
        optimizations.append(False)
    
    # Check call.py for cache optimization
    try:
        with open('ANNIEMUSIC/core/call.py', 'r') as f:
            content = f.read()
            if 'cache_duration=300' in content:
                print_check("PyTgCalls cache optimized", True)
                optimizations.append(True)
            else:
                print_check("PyTgCalls cache optimized", False)
                optimizations.append(False)
    except FileNotFoundError:
        print_check("Call configuration", False, "File not found")
        optimizations.append(False)
    
    # Check mongo.py for connection pooling
    try:
        with open('ANNIEMUSIC/core/mongo.py', 'r') as f:
            content = f.read()
            if 'maxPoolSize' in content:
                print_check("MongoDB connection pooling", True)
                optimizations.append(True)
            else:
                print_check("MongoDB connection pooling", False)
                optimizations.append(False)
    except FileNotFoundError:
        print_check("Mongo configuration", False, "File not found")
        optimizations.append(False)
    
    return all(optimizations)

def main():
    print(f"\n{Colors.OKCYAN}")
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║       ANNIEMUSIC Bot Performance Diagnostic Tool      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}")
    
    results = []
    
    # Run all checks
    results.append(("Environment", check_env_file()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Network", check_network_latency()))
    results.append(("MongoDB", check_mongodb_connection()))
    results.append(("System Resources", check_system_resources()))
    results.append(("Optimizations", check_optimization_status()))
    
    # Summary
    print_header("Diagnostic Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if result else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}🎉 All checks passed! Your bot should perform well.{Colors.ENDC}")
    elif passed >= total - 1:
        print(f"\n{Colors.WARNING}⚠ Most checks passed. Minor issues detected.{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}❌ Several issues found. Please fix them for better performance.{Colors.ENDC}")
    
    print(f"\n{Colors.OKCYAN}For detailed optimization tips, see OPTIMIZATION_SUMMARY.md{Colors.ENDC}\n")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
