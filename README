Viper: Internet-over-OpenVPN software for Windows

https://www.greenhost.io/projects/viper


## What is Viper?
Viper is an OpenVPN client for Windows, designed for directing all traffic over a VPN connection. Viper has a strong emphasis on ease-of-use and accuracy in reporting the state of the VPN.

Although it's already more carefully written than most 'security' software, we consider Viper to be in pre-release 'beta' status. As with all software, you should be circumspect about the security it provides.


## Why another VPN client?
We wanted to build software designed specifically for directing all Internet traffic over the VPN. This is an important application of VPN technology, for people who are using Internet connections with filtering and surveillance risks. Common open-source OpenVPN Windows clients are not designed for this purpose.


## How does it work?
Viper wraps the open-source OpenVPN command line tool, providing a simple GUI in the Windows system tray that allows for control and monitoring of the connection status.

Viper reports the connection as secure only when the VPN gateway is designated as the route to the Internet. To accomplish this, Viper continuously checks the kernel's IP routing table against OpenVPN's internal status. Viper's lock icon is shown only when it really mean to say that the connection is secured.


## What is missing?
Viper does not include an OpenVPN client configuration -- you must create you own. The configuration directive "redirect-gateway def1 bypass-dhcp" must be used to establish the routes which will cause Internet traffic to be directed over the VPN. The directive "management localhost 7505" must be used to allow Viper to monitor the VPN.

Viper does not (yet) block communications with the local network segment where the client computer is connected. An OpenVPN client configuration directive such as "dhcp-option DNS n.n.n.n" (where n.n.n.n is a trusted DNS resolver) should be used to ensure that a DNS resolver on the local network segment is not used. A more complete mitigation of this issue in in the works.

Viper does not (yet) support IPv6. Since version R7, Viper configures the Windows Firewall to block all IPv6 traffic while the VPN is connected. If the Windows Firewall is not available, Viper will refuse to connect and present an explanatory dialog. Support for IPv6-over-IPv4 tunnelling is in the works.


## How can I contribute to Viper?
Viper is a new development, and like all pre-release software it is likely to have bugs. I would very much appreciate bug reports from your tests. If you wish to join the development of Viper, please continue reading for help on how to set up a development environments.


## Notes for developers
Viper is written in Python with some bits and pieces in C#. To build Viper you must have Microsoft's .NET SDK 3.5, used for external utilities such as the firewall CLI and Active State's Python 2.7.5.

There's no need for a Microsoft IDE. I have successfully compiled the C# utilities using the open-source SharpDevelop IDE.

Due to compatibility issues between Python virtual environments and the Python Windows APIs, it is recommended that you do not create a Python virtualenv for Viper (as you might normally do for any new development in Python).

Have a look at the build script 'build.bat' to see how the different elements of a release are built together.

All build products are output to the 'dist' directory where the installer script expects them.

You can install the Python dependencies using the requirements file provided:
:\> pip install -r third-party\requirements.txt

NSIS is used to generate the Windows installer, so make sure you have it in your system and makensis.exe is in your path. You can get NSIS here: http://nsis.sourceforge.net

This distribution of Viper contains binary files in the 'third-party' directory from the OpenVPN project. You may replace them with (or compare tham against) official files from the OpenVPN project. See: http://openvpn.net/index.php/download/community-downloads.html

