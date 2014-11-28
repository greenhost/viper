## Viper: keeps your online activity to yourself
https://www.greenhost.io/projects/viper

### What is Viper?
Viper is a client for a type of proxy that we like to call Encrypted Internet Proxy (EIP). An EIP is a set of technologies that work together to enable encrypted Internet access and enhanced anonymity.

As an EIP client Viper implements a set of policies that are aimed at keeping you anonymous online and encrypt all your interactions through the Internet.

Viper uses VPN technology, with a carefully crafted OpenVPN configuration, in combination with other techniques to achieve these goals.

### Anti-censorship
Viper uses OpenVPN, this provides first-hop encryption in all your connections to the Internet.

VPN traffic can still be identified and tracked by agents using deep packet inspection (DPI). To prevent this scenario Viper uses Tor's pluggable transports. These transports encode VPN traffic to make it look like something else that is less likely to be blocked in certain jurisdictions. In this way Viper leverages the phenomenal work that the people behind the Tor project have put at the service of anti-censorship.

By using VPN technology your geographical location when connecting to the internet can be hidden, so you can access websites that are blocked in your jurisdiction.

### What is it good for?

By proxying all your internet traffic through Viper the connections you make to sites on the internet will appear to come from another geographical location than your own. Making Viper a useful tool in circumventing location-based censorship.

Because the first hop in your communications with Viper is encrypted you can get some piece of mind by knowing that an attacker that is looking at your outgoing connection will be met with an encrypted stream of data.

### What Viper doesn't do yet.

This software doesn't yet support IPv6 for active connections, so to prevent attacks from the IPv6 network Viper blocks all IPv6 traffic using the Windows Firewall.

Full IPv6 support is planned in future releases.

### Disclaimer

Although Viper already is more carefully written than most 'security' software. We consider Viper to be in pre-release 'beta' status. As with all software, you should be circumspect about the security it provides.

