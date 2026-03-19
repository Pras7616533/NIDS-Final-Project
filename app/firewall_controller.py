import os
import platform
import subprocess

class FirewallController:
    """
    Handles OS-specific firewall commands for blocking and unblocking IP addresses.
    """
    def __init__(self):
        self.os_type = platform.system()
        self.blocked_ips = set()

    def block_ip(self, ip):
        """
        Blocks an IP address using system firewall rules.
        """
        if ip in self.blocked_ips:
            return True, f"IP {ip} is already blocked."

        try:
            if self.os_type == "Windows":
                # Windows: netsh advfirewall
                command = f'netsh advfirewall firewall add rule name="BlockedIP_{ip}" dir=in action=block remoteip={ip}'
                subprocess.run(command, shell=True, check=True, capture_output=True)
            elif self.os_type == "Linux":
                # Linux: iptables
                command = f"sudo iptables -A INPUT -s {ip} -j DROP"
                subprocess.run(command, shell=True, check=True, capture_output=True)
            else:
                return False, f"Unsupported OS: {self.os_type}"

            self.blocked_ips.add(ip)
            return True, f"Successfully blocked IP: {ip}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to block IP {ip}: {e.stderr.decode().strip()}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def unblock_ip(self, ip):
        """
        Removes the firewall rule for a specific IP address.
        """
        try:
            if self.os_type == "Windows":
                command = f'netsh advfirewall firewall delete rule name="BlockedIP_{ip}"'
                subprocess.run(command, shell=True, check=True, capture_output=True)
            elif self.os_type == "Linux":
                command = f"sudo iptables -D INPUT -s {ip} -j DROP"
                subprocess.run(command, shell=True, check=True, capture_output=True)
            else:
                return False, f"Unsupported OS: {self.os_type}"

            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
            return True, f"Successfully unblocked IP: {ip}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to unblock IP {ip}: {e.stderr.decode().strip()}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def get_blocked_ips(self):
        """
        Returns a list of currently blocked IP addresses.
        """
        return list(self.blocked_ips)

if __name__ == "__main__":
    # Basic self-test
    controller = FirewallController()
    print(f"Detected OS: {controller.os_type}")
    # Note: Actually running block/unblock might fail without admin privileges
    # This is handled gracefully by catching CalledProcessError
