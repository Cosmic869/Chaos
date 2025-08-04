#!/usr/bin/env python3
"""
Discord Bot Runner with Auto-Restart and 24/7 Operation
This script ensures the bot stays running continuously with automatic restarts.
"""

import subprocess
import sys
import time
import logging
import os
from datetime import datetime

# Set up logging for the runner
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [RUNNER] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self):
        self.restart_count = 0
        self.max_restarts_per_hour = 10
        self.restart_times = []
        
    def clean_old_restart_times(self):
        """Remove restart times older than 1 hour"""
        current_time = time.time()
        self.restart_times = [t for t in self.restart_times if current_time - t < 3600]
    
    def can_restart(self):
        """Check if we can restart (not too many restarts in the last hour)"""
        self.clean_old_restart_times()
        return len(self.restart_times) < self.max_restarts_per_hour
    
    def run_bot(self):
        """Run the bot with automatic restart capability"""
        logger.info("🚀 Starting Discord Bot Runner for 24/7 operation")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        while True:
            try:
                if not self.can_restart():
                    logger.error(f"❌ Too many restarts ({len(self.restart_times)}) in the last hour. Waiting 10 minutes...")
                    time.sleep(600)  # Wait 10 minutes
                    continue
                
                self.restart_count += 1
                self.restart_times.append(time.time())
                
                logger.info(f"🔄 Starting bot (Attempt #{self.restart_count})")
                logger.info(f"📊 Restarts in last hour: {len(self.restart_times)}")
                
                # Start the bot process
                process = subprocess.Popen(
                    [sys.executable, 'main.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                logger.info(f"✅ Bot process started with PID: {process.pid}")
                
                # Monitor the process and log output
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Log bot output with timestamp
                        print(f"[BOT] {output.strip()}")
                
                # Process has ended
                return_code = process.poll()
                logger.warning(f"⚠️ Bot process ended with return code: {return_code}")
                
                if return_code == 0:
                    logger.info("✅ Bot shut down gracefully")
                    break
                else:
                    logger.error(f"❌ Bot crashed with code {return_code}")
                
                # Wait before restarting
                wait_time = min(30 * len(self.restart_times), 300)  # Max 5 minutes
                logger.info(f"⏰ Waiting {wait_time} seconds before restart...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received shutdown signal")
                if 'process' in locals():
                    logger.info("🔄 Terminating bot process...")
                    process.terminate()
                    process.wait()
                break
            except Exception as e:
                logger.error(f"💥 Runner error: {e}")
                time.sleep(60)  # Wait 1 minute on runner errors

if __name__ == "__main__":
    runner = BotRunner()
    runner.run_bot()
