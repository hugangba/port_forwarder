# port_forwarder

IPv6 to IPv4 Port Forwarder
Overview
This is an asynchronous Python script (proxy.py) that forwards network traffic from IPv6 addresses to corresponding public IPv4 addresses. It maps the last four segments of an IPv6 address to an IPv4 address by interpreting each segment as a decimal value after removing leading zeros. The script only forwards traffic for IPv6 addresses that generate valid public IPv4 addresses, optimizing resource usage by skipping invalid or private IPv4 mappings.
Features

Listens on specified ports (80, 443, 8080, 8443) for IPv6 connections.
Maps the last four segments of an IPv6 address (e.g., 0047:0100:0065:0065) to an IPv4 address (e.g., 47.100.65.65).
Ensures the generated IPv4 address is a public address (not private, reserved, multicast, or loopback).
Skips IPv6 addresses with segments that exceed the valid IPv4 range (0-255) to save resources.
Uses asyncio for efficient handling of multiple concurrent connections.
Provides minimal logging for successful forwards and errors, reducing resource consumption.

Prerequisites

Operating System: Linux (due to IPv6 check via /proc/sys/net/ipv6/conf/all/disable_ipv6).
Python: Version 3.7 or higher.
Privileges: Root privileges (sudo) are required to listen on privileged ports (e.g., 80, 443).
IPv6 Support: The system must have IPv6 enabled.

Installation

Clone or Download:Download the proxy.py script to your local machine or clone the repository:
git clone <repository-url>
cd <repository-directory>


Ensure IPv6 is Enabled:Verify that IPv6 is enabled on your system:
cat /proc/sys/net/ipv6/conf/all/disable_ipv6

The output should be 0. If it’s 1, enable IPv6:
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0


Install Python:Ensure Python 3.7+ is installed:
python3 --version

If not installed, install it (e.g., on Ubuntu):
sudo apt update
sudo apt install python3



Usage

Run the Script:Execute the script with root privileges to listen on privileged ports:
sudo python3 proxy.py

The script will start listening on ports 80, 443, 8080, and 8443 for IPv6 connections.

Expected Output:Upon starting, the script will display:
监听 [::]:80
监听 [::]:443
监听 [::]:8080
监听 [::]:8443

For successful forwards, it logs messages like:
从客户端 [2001:470:f2f4:1:0:67:145c:3acf]:80 (服务器 [2001:470:19:53f:47:100:65:65]:80) 转发到 47.100.65.65:80


Mapping Logic:

The last four segments of an IPv6 address are used to generate an IPv4 address.
Each segment has leading zeros removed and is parsed as a decimal value (base 10).
Example: [2001:470:19:53f:47:100:65:65]:80 → 47.100.65.65:80
Segments: 0047:0100:0065:0065
After removing leading zeros: 47:100:65:65
Parsed as decimal: 47, 100, 65, 52
Resulting IPv4: 47.100.65.65


If any segment exceeds 255 (e.g., 0352 → 352) or the generated IPv4 is not public, the connection is silently closed without logging.


Stopping the Script:Press Ctrl+C to stop the script gracefully:
正在关闭...



Notes

Resource Optimization: The script skips IPv6 addresses that do not map to valid public IPv4 addresses (e.g., segments > 255 or private IPv4 addresses) without logging, reducing resource usage.
Privileged Ports: Running on ports like 80 and 443 requires sudo. For non-privileged ports (e.g., 8080, 8443), sudo may not be needed.
Linux Dependency: The script checks /proc/sys/net/ipv6/conf/all/disable_ipv6, making it Linux-specific. For other operating systems, this check needs modification.
Error Handling: The script logs errors only for connection or forwarding issues, not for invalid IPv6 mappings, to minimize output.

Troubleshooting

IPv6 Disabled Error:
错误: 系统已禁用 IPv6，请启用 IPv6。

Enable IPv6 as described in the Installation section.

Port Already in Use:
启动服务器失败，地址 [::]:80: [Errno 98] Address already in use

Ensure no other process is using the specified ports:
sudo netstat -tuln | grep :80

Stop conflicting processes or change the ports in the script.

No Forwarding Occurs:

Verify the IPv6 address’s last four segments generate a valid public IPv4 address.
Check if the target IPv4 address is reachable:ping 47.100.65.65





Limitations

Segment Range: IPv6 segments that parse to values > 255 (e.g., 0352 → 352) are skipped. To handle such cases (e.g., using modulo 256), modify the mapping logic.
Platform: Currently Linux-only due to the IPv6 check. For cross-platform support, remove or adapt the /proc check.
Logging: Minimal logging is implemented for resource efficiency. For debugging, you can add more detailed logs in the handle_client function.

Contributing
Contributions are welcome! Please submit a pull request or open an issue to suggest improvements, such as:

Cross-platform IPv6 checks.
Configurable ports via command-line arguments.
Enhanced logging with timestamps or connection IDs.
Support for modulo 256 handling of segments > 255.

License
This project is licensed under the MIT License.
