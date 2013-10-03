# Viper beta 8 (mamba)
Viper is Windows OpenVPN client software designed for Internet access over an VPN connection.

> WARNING: At the time of this writing this software is still in a BETA 
> development state. It is very well possible that bugs might still lurk
> in unknown places. 

## New in this release
- Block all IPv6 upon start-up if Windows Firewall is enabled
- Prevent the execution of multiple instances
- Acknowledge false OpenVPN starts due to bad configuration and report them
- More robust error checking
- Tested the sleep restart
- Tested time-outs and multiple access with same certificate

## Installation
The installer will carry out the installation of all the necessary components used by Viper. This includes the TAP/TUN networking driver for Windows, an OpenVPN binary, a service that runs with elevated privileges to start and stop the VPN a small binary utility named `fwipv6` that helps Viper manage the *Windows Firewall* and a GUI client that the user interacts with through the systray.

## Configuring Viper
Viper needs a configuration file containing the VPN connection details and all the pertinent certificates. You can request this configuration file from your administrator or fetch it from the Uman VPN web interface.

![illustration4](res/configure.png "Tell Viper where to find the configuration VPN file.")

To configure Viper you first have to run the application and right click on the `Configure...`. A file selection dialog will apear, select the configuration file. Tis file will now be placed in your user directory so that it becomes the default configuration in subsequent runs of Viper.

At the moment Viper supports one connection profile only, so only one configuration file. Support for multiple connection profiles is planned for future releases.

### Recommendations
If Viper finds the *Windows Firewall* active it will automatically configure it to block all IPv6 traffic. The current release of Uman/Viper doesn't support IPv6, so if the network your computer is connected to supports IPv6 it is a good practice to block that traffic during your connection to the VPN.

If you run Viper with your *Windows Firewall* disabled it will warn you about it, so that you can manually enable it before you continue.

Full support for IPv6 is planned for future releases of the server side software.

>If your personal integrity depends on a secured
> internet connection, we remind you that it is not wise to trust your life 
> to any piece of software, so use Viper with utmost care.

## Using the client
It is important to understand the way Viper reports the connection status. When you click on `Go online...` Viper will initiate the OpenVPN connection process, it takes a few seconds. When the handshake was successful and the new IP and routing tables are updated Viper will report this by showing a grey icon. Your connection is not yet secure.

![illustration5](res/connecting.png "Opening the connection to the VPN takes a few seconds")

If the connection process was successful a lock icon will appear. Mousing over the icon will show you your new IP and the IP of the gateway that you are connected to. Make sure that those IPs are familiar to you.

![illustration6](res/connected.png "Only when the icon turns into a lock is the connection secured")

If you do not see the lock appear, your connection is not secure.

From Windows 7 onwards, systray icons are sometimes pushed out of view automatically by Windows. There's nothing Viper can do to always stay in sight, but you can change this yourself by clicking on `Customize...` on the system tray and selecting the drop down that says `Show icon and notifications` for Viper. That way the icon will always be present.

### What happens if the connection is lost?
Sometimes it can happen that connection to the VPN gateway is momentarily lost. Viper will notify you of this change in situation with a ballon, without interrupting your normal activity.

It is up to you to take measures when the connection to the VPN is lost. But if your computer disconnects from the VPN and you continue using software that has access to the internet your system will default to your standard non-secure connection. So please take approppriate action when Viper notifies you of a dropped connection.

## Troubleshooting
The Viper beta releases produce two log files that are located in the root directory of your Windows drive. They are named `ovpnmon.log` which is produced by the Windows service that Viper interacts with for actions that require elevated privileges. The other log file is named `openvpn-log.txt` and contains the raw log of OpenVPN, here you can find information about connection bootstrapping and possible error messages in the communication with the server.

When reporting bugs it is generally a good idea to include these two log files.

## Help out
You can help the developers of Viper by testing the software and sending reports of any bugs you might find. If you wish to hack at the code and perhaps even join the development, please refer to the development section at the `README`.

## Future
We would like to make Viper a good VPN client for people that work in environments were best practices in security are routine. We would very much appreciate to hear your use cases if they are not contemplated by Viper, to gain more experience from the field.

In future releases we would like to focus on responsiveness, auto-configuration and self-updating.
