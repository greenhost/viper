# Viper helps with best practices for VPN access

> WARNING: At the time of this writing this software is still in a BETA 
> development state. It is very well possible that bugs might still lurk
> in unknown places. If your personal integrity depends on a secured
> internet connection, we remind you that it is not wise to trust your life 
> to any piece of software so use with utmost care.

## Installation
The provided installer will carry out the installation of all the necessary components used by Viper.

#### Pre-requisites
Install TAP Windows from the client distribution by double-clicking on the installer.

To let the monitor know where the OpenVPN client is, you must have a system-wide environment variable called *OPENVPN_HOME* that points to the folder where your OpenVPN installation is. Make sure this variable is available to all users, not only to your current user.

## Running Viper

Once you start this application it will sit rather quietly in your system tray until you establish the connection. You do not have to install this one, it is a self-standing executable. You may place it in your *Start Up* items if you wish to have it available upon startup.

## Configuring Viper

Choose **Configure...** to set the configuration file provided by your VPN administrator. This configuration file will be used in every subsequent connection.

> The GUI client provides a way to validate the VPN connection against a preconfigured server 
> inside of the VPN. This is useful as a double check, but please be mindful that this is not 
> foolproof and if your network has been compromised it would be easy to fool the browser with a 
> fake page. So trust only what the system tray icon says.

When you click on *Go online...* the client will take a few seconds to initialize the connection. Please wait untill your connection is secured.

![illustration4](res/connecting.png "Opening the connection to the VPN takes a few seconds")

You are now connected to the VPN. Plase validate the IP address of the gateway and the address of your interface, to make absolutely sure that your connection is secured.

![illustration5](res/connected.png "You are now connected to the VPN")

## Troubleshooting

## Help out
You can help the developers of Viper by testing the software and sending reports of any bugs you might find. If you wish to hack at the code and perhaps even join the development please refer to the development section at the README.

## Future
We would like to make Viper a good VPN client for people that work in environments were best practices in security are a must. We would very much appreciate to hear your use cases if they are not contemplated by Viper, to gain more experience from the field.

In future releases we would like to focus on responsiveness, auto-configuration and self-updating.
