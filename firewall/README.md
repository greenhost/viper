## Interaction with the platform's firewall
Viper can interact with your platform's firewall to enhance your security while you are connected to the Encrypted Internet Proxy.

### On Windows
To benefit from the extra security provided by this feature we strongly recommend the use of Windows Firewall. Please make sure you have it activated before you run Viper. No other firewalls have been tested at the time of release.

When Viper opens a connection with your OpenVPN server it blocks all traffic using the following policies:
 
 * **Deny all IPv6 traffic, incoming and outgoing**. This prevents commonly known IPv6 attacks.

##### To do
[ ] Deny all traffic outside the VPN

### OSX
Not supported in this release.

### Linux
Not supported in this release.
