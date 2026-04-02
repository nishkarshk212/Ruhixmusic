#!/usr/bin/env python3
"""
Voice Chat Connection Monitor for ANNIEMUSIC Bot
Tracks success rates and connection times for voice chat detection
"""

import asyncio
from datetime import datetime
from collections import defaultdict
import statistics

class VoiceChatMonitor:
    def __init__(self):
        self.stats = defaultdict(list)
        self.total_attempts = 0
        self.successful_connections = 0
        self.first_try_successes = 0
        self.second_try_successes = 0
        self.failures = 0
        
    async def track_connection_attempt(self, chat_id: int, attempt_number: int, success: bool, time_taken: float):
        """Track a single connection attempt"""
        self.total_attempts += 1
        self.stats[chat_id].append({
            'timestamp': datetime.now(),
            'attempt': attempt_number,
            'success': success,
            'time_taken': time_taken
        })
        
        if success:
            self.successful_connections += 1
            if attempt_number == 1:
                self.first_try_successes += 1
            else:
                self.second_try_successes += 1
        else:
            self.failures += 1
    
    def get_statistics(self):
        """Get current statistics"""
        if self.total_attempts == 0:
            return "No data yet"
        
        first_try_rate = (self.first_try_successes / self.total_attempts * 100) if self.total_attempts > 0 else 0
        second_try_rate = (self.second_try_successes / self.total_attempts * 100) if self.total_attempts > 0 else 0
        success_rate = (self.successful_connections / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        all_times = [entry['time_taken'] for attempts in self.stats.values() for entry in attempts]
        avg_time = statistics.mean(all_times) if all_times else 0
        
        report = f"""
╔═══════════════════════════════════════════════════════╗
║     VOICE CHAT CONNECTION STATISTICS                  ║
╠═══════════════════════════════════════════════════════╣

📊 Overall Performance:
   • Total Attempts: {self.total_attempts}
   • Successful Connections: {self.successful_connections}
   • Failed Connections: {self.failures}
   • Success Rate: {success_rate:.1f}%

🎯 Detection Method Performance:
   • First Try Success: {self.first_try_successes} ({first_try_rate:.1f}%)
   • Second Try Success: {self.second_try_successes} ({second_try_rate:.1f}%)
   
⏱️ Response Times:
   • Average Connection Time: {avg_time:.2f}s
   • Target: < 2.0s
   • Status: {'✅ Optimal' if avg_time < 2.0 else '⚠️ Needs attention'}

📈 Recent Activity (Last 10 connections):
"""
        # Show last 10 connections
        recent = []
        for chat_id, attempts in list(self.stats.items())[-10:]:
            for attempt in attempts[-1:]:
                status = '✅' if attempt['success'] else '❌'
                recent.append(f"   {status} Chat {chat_id}: Attempt #{attempt['attempt']}, {attempt['time_taken']:.2f}s")
        
        report += '\n'.join(recent) if recent else "   No recent activity"
        report += "\n\n╚═══════════════════════════════════════════════════════╝"
        
        return report

# Global monitor instance
monitor = VoiceChatMonitor()

async def main():
    """Run monitoring display"""
    print("Starting Voice Chat Connection Monitor...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            print(monitor.get_statistics())
            await asyncio.sleep(10)  # Update every 10 seconds
        except KeyboardInterrupt:
            print("\n\nFinal Statistics:")
            print(monitor.get_statistics())
            break

if __name__ == "__main__":
    asyncio.run(main())
