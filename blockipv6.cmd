netsh advfirewall firewall add rule name="IPv6" protocol=icmpv6 dir=out action=block
netsh advfirewall firewall add rule name="IPv6" protocol=icmpv6 dir=in action=block
netsh advfirewall firewall add rule name="IPv6" action=block protocol=41 dir=out
netsh advfirewall firewall add rule name="IPv6 protocol 43" protocol=43 action=block dir=out
netsh advfirewall firewall add rule name="IPv6 protocol 44" protocol=44 action=block dir=out
netsh advfirewall firewall add rule name="IPv6 protocol 58" protocol=58 action=block dir=out
netsh advfirewall firewall add rule name="IPv6 protocol 59" protocol=59 action=block dir=out
netsh advfirewall firewall add rule name="IPv6 protocol 60" protocol=60 action=block dir=out