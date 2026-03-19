import csv
import os
from datetime import datetime

class AttackLogger:
    """
    Handles logging of attack events to CSV and system events to text files.
    """
    def __init__(self, attack_csv="attack_log.csv", system_txt="system_logs.txt"):
        self.attack_csv = attack_csv
        self.system_txt = system_txt
        self._initialize_files()

    def _initialize_files(self):
        """
        Creates the log files with headers if they don't exist.
        """
        if not os.path.exists(self.attack_csv):
            with open(self.attack_csv, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Attacker IP", "Attack Type", "Action Taken"])

        if not os.path.exists(self.system_txt):
            with open(self.system_txt, mode='w') as f:
                f.write(f"--- System Log Started at {datetime.now()} ---\n")

    def log_attack(self, ip, attack_type, action):
        """
        Logs a detected attack to the CSV file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.attack_csv, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, ip, attack_type, action])
            self.log_system_event(f"ATTACK DETECTED: {attack_type} from {ip}. Action: {action}")
        except Exception as e:
            self.log_system_event(f"ERROR: Failed to write to attack log: {str(e)}")

    def log_system_event(self, event):
        """
        Logs a general system event to the text file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.system_txt, mode='a') as f:
                f.write(f"[{timestamp}] {event}\n")
        except Exception:
            pass # Last resort: ignore if even system logging fails

if __name__ == "__main__":
    logger = AttackLogger()
    logger.log_attack("192.168.1.100", "DDoS", "IP Blocked")
    logger.log_system_event("NIDPS Module Started")
