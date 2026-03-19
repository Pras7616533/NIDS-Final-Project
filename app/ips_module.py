from firewall_controller import FirewallController
from attack_logger import AttackLogger

class IPSModule:
    """
    Orchestrates the intrusion prevention logic.
    """
    def __init__(self):
        self.firewall = FirewallController()
        self.logger = AttackLogger()
        self.whitelist = {"127.0.0.1", "localhost", "192.168.1.1"} # Default whitelist
        
        # Examples for demonstration purposes
        example_ips = [
            "192.168.1.105", "10.0.0.45", "172.16.254.1", 
            "192.168.1.200", "192.168.1.222", "10.0.0.101",
            "45.33.22.11", "185.10.10.10", "203.0.113.5",
            "198.51.100.12", "192.0.2.1"
        ]
        for ip in example_ips:
            self.firewall.blocked_ips.add(ip)

    def handle_detection(self, ip, attack_type):
        """
        Decides and executes the prevention action for a detected attack.
        """
        if ip in self.whitelist:
            self.logger.log_system_event(f"WHITEDLISTED: Attack {attack_type} detected from {ip}. No action taken.")
            return "Whitelisted"

        # Check if already blocked (this logic is also in FirewallController but we can double check here)
        success, message = self.firewall.block_ip(ip)
        
        if success:
            action = "IP Blocked"
            self.logger.log_attack(ip, attack_type, action)
        else:
            action = "Block Failed"
            self.logger.log_system_event(f"PREVENTION FAILED: {message}")

        return action

    def unblock_attacker(self, ip):
        """
        Removes a block on an IP.
        """
        success, message = self.firewall.unblock_ip(ip)
        if success:
            self.logger.log_system_event(f"MANUAL UNBLOCK: IP {ip} has been unblocked.")
        return success, message

    def add_to_whitelist(self, ip):
        self.whitelist.add(ip)
        self.logger.log_system_event(f"WHITELIST UPDATE: IP {ip} added to whitelist.")

    def remove_from_whitelist(self, ip):
        if ip in self.whitelist:
            self.whitelist.remove(ip)
            self.logger.log_system_event(f"WHITELIST UPDATE: IP {ip} removed from whitelist.")

    def get_status(self):
        return {
            "blocked_ips": self.firewall.get_blocked_ips(),
            "whitelist": list(self.whitelist)
        }

if __name__ == "__main__":
    # Mock some activity
    ips = IPSModule()
    print("IPS Status:", ips.get_status())
    ips.handle_detection("10.0.0.5", "SQL Injection")
    print("Post-detection status:", ips.get_status())
