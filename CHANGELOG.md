# CHANGELOG

## 1.0b
* Major change in the architecture. Viper is now a Windows service that serves as a watchdog for your internet connection and a GUI reference client that can be used as a remote control for the service. The service is always active.

## b8 (mamba)
* Block all IPv6 upon start-up if Windows Firewall is aenabled
* Prevent the execution of multiple instances
* Acknowledge false OpenVPN starts due to bad configuration and report them
* Cleaned up the code quite substantially
* Tested the sleep restart
* Tested time-outs and multiple access with same certificate

## b7
* Check for TAP/TUN drivers on startup
* Report with a balloon tooltip when the status goes from CONNECTED to DISCONNECTED so users are aware that they are no longer under a secure connection.
* Installer now includes a third party TAP/TUN driver for windows
* Removed console window from systray client (was used for debugging only)
