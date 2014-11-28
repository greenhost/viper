/*
 * Copyright (c) 2013 Greenhost VOF
 * https://greenhost.nl -\- https://greenhost.io
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
using System;
using System.Collections.Generic;
using System.Text;
using NATUPNPLib;
using NETCONLib;
using NetFwTypeLib;
using System.Collections;
using System.Runtime.InteropServices;

namespace fwipv6
{
    /**
     * Very simple command line tool to add/remove and activate/deactivate a Windows Firewall rule
     * that blocks IPv6.
     *  
     * The following tool produces an exit code, here are the values and their respective meaning:
     * 
     * 0 = operation was successful
     * 1 = operation failed
     * 2 = firewall is not enabled
     */
    class Firewall
    {
        INetFwMgr fwmngr = Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FwMgr")) as INetFwMgr;
        INetFwPolicy2 fwpolicy = Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FwPolicy2")) as INetFwPolicy2;

        public bool FirewallEnabled
        {
            get { return fwmngr.LocalPolicy.CurrentProfile.FirewallEnabled; }
        }

        public const string VIPER_RULE_IPv6 = "Viper - Block IPv6";
		public const string VIPER_RULE_DEFGATEWAY = "Viper - Block default gateway subnet";
		public const string VIPER_RULE_ALLPORTS = "Viper - Block all ports but VPN";

		/// <summary>
		/// Known IP addresses, ranges and ip wildcards used in the firewall rules.
		/// </summary>
		const  string GLOBAL_UNICAST_ADDRESS = "2033::/3";  // IPv6 Global Unicast
		const  string ANY_IP_ADDRESS = "*";
		const  string LOCAL_SUBNET = "LocalSubnet";

		/*
        static Firewall()
        {
            INetFwMgr fwmngr = Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FwMgr")) as INetFwMgr;
            INetFwPolicy2 fwpolicy = Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FwPolicy2")) as INetFwPolicy2;
        }
        */

        /**
         * Find a rule in the firewall profile.
         */
        private INetFwRule2 FindRule(string rulename)
        {
            IEnumerator enumerator = this.fwpolicy.Rules.GetEnumerator();
            try
            {
                while(enumerator.MoveNext()) {
                    INetFwRule2 rule = enumerator.Current as INetFwRule2;
                    if (string.Equals(rule.Name, rulename, StringComparison.OrdinalIgnoreCase)) {
                        return rule;
                    }
                }
            } finally {
                if (enumerator is IDisposable)
                {
                    (enumerator as IDisposable).Dispose();
                }
            }

            return null;
        }

		public bool AddRule_DefGateway(string gatewayIp)
		{
			// try to find the rule first, if found return successfully
			INetFwRule2 rule = FindRule(VIPER_RULE_DEFGATEWAY);
			if(null != rule) {
				Console.WriteLine("Not adding rule because iit already exists...");
				return true;
			}

			// if it's not found, add it
			try
			{
				INetFwRule2 firewallRule = (INetFwRule2)Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FWRule"));

				firewallRule.Name = VIPER_RULE_DEFGATEWAY;
				firewallRule.Description = "Block all traffic through the default gateway";
				firewallRule.Action = NET_FW_ACTION_.NET_FW_ACTION_BLOCK;
				firewallRule.Direction = NET_FW_RULE_DIRECTION_.NET_FW_RULE_DIR_OUT;
				firewallRule.Enabled = true;
				firewallRule.Protocol = (int)NET_FW_IP_PROTOCOL_.NET_FW_IP_PROTOCOL_ANY;
				firewallRule.RemoteAddresses = Firewall.LOCAL_SUBNET;
				firewallRule.LocalAddresses = Firewall.ANY_IP_ADDRESS;

				this.fwpolicy.Rules.Add(firewallRule);

				Console.WriteLine("Adding firewall rule '{0}'...", VIPER_RULE_DEFGATEWAY);
			} catch (UnauthorizedAccessException uae) {
				Console.WriteLine("I'm sorry Dave, I'm afraid I can't do that. You do not have sufficient privileges. Run again as admin.");
			} catch (Exception e) {
				return false;
			}
			return true;
		}

		public bool AddRule_ipv6()
        {
            // try to find the rule first, if found return successfully
			INetFwRule2 rule = FindRule(VIPER_RULE_IPv6);
            if(null != rule) {
                return true;
            }

            // if it's not found, add it
            try
            {
                INetFwRule2 firewallRule = (INetFwRule2)Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FWRule"));

				firewallRule.Name = VIPER_RULE_IPv6;
                firewallRule.Description = "Block unwated IPv6 traffic while Viper OpenVPN client is running";
                firewallRule.Action = NET_FW_ACTION_.NET_FW_ACTION_BLOCK;
                firewallRule.Direction = NET_FW_RULE_DIRECTION_.NET_FW_RULE_DIR_OUT;
                firewallRule.Enabled = true;
                firewallRule.Protocol = (int)NET_FW_IP_PROTOCOL_.NET_FW_IP_PROTOCOL_ANY; // 6
                firewallRule.RemoteAddresses = GLOBAL_UNICAST_ADDRESS;
                firewallRule.LocalAddresses = GLOBAL_UNICAST_ADDRESS;

                this.fwpolicy.Rules.Add(firewallRule);

				Console.WriteLine("Adding firewall rule '{0}'...", VIPER_RULE_IPv6);
			} catch (UnauthorizedAccessException uae) {
				Console.WriteLine("I'm sorry Dave, I'm afraid I can't do that. You do not have sufficient privileges. Run again as admin.");
            } catch (Exception e) {
                return false;
            }
            return true;
        }

		public bool AddRule(string name, string[] parameters) 
		{
			bool retval = false;

			switch(name) {
				case Firewall.VIPER_RULE_ALLPORTS:
					break;
			case Firewall.VIPER_RULE_DEFGATEWAY:
					retval = this.AddRule_DefGateway(null);
					break;
			case Firewall.VIPER_RULE_IPv6:
				retval = this.AddRule_ipv6 ();
					break;
			}
			return retval;
		}

        public bool RemoveRule(string name)
        {
            try
            {
				Console.WriteLine("Removing firewall rule '{0}'", name);
				this.fwpolicy.Rules.Remove(name);
            } catch (Exception e) {
                return false;
            }
            return true;
        }

        public bool EnableRule(string name)
        {
            bool retval = true;

            INetFwRule2 rule = FindRule(name);
            if (null != rule)
            {
				Console.WriteLine("Enabling firewall rule '{0}'", name);
                rule.Enabled = true;
                Marshal.ReleaseComObject(rule);
            }
            else
            {
                Console.WriteLine("Couldn't enable firewall rule '{0}' because I coudn't find it.", name);
                retval = false;
            }

            return retval;
        }

        public void Usage() {
            Console.WriteLine("Viper command line interface to the Windows Firewall");
            Console.WriteLine("(c) 2013 Greenhost VOF\n");
            Console.WriteLine(@"fwipv6 manages the Windows Firewall to block all IPv6 traffic. For it to work it must be executed with elevated privileges.\n

Usage:
    fwi add <rule>       -   adds rule
    fwi remove <rule>    -   removes rule
    fwi enable <rule>    -   enables the rule (rule must exist in current profile)
    fwi disable <rule>   -   disables the rule (rule must exist in current profile)
    fwi usage <rule>     -   prints this text

Available rules:
	ipv6				 - rule that denies/allows IPv6 traffic
	defgateway			 - rule that blocks/unblocks all traffic on the default gateway (blocks local subnet)
	allports			 - rule that blocks/unblocks all ports except those used by the VPN
");
        }

        public bool DisableRule(string name)
        {
            bool retval = true;

            INetFwRule2 rule = FindRule(name);
            if (null != rule)
            {
                Console.WriteLine("Disabling firewall rule...");
                rule.Enabled = false;
                Marshal.ReleaseComObject(rule);
            }
            else
            {
                Console.WriteLine("Couldn't disable firewall rule '{0}' because I coudn't find it.", name);
                retval = false;
            }

            return retval;
        }

    } // class

    class Program
    {
		Firewall fwall;

		private string ParseRuleFromCli(string []args)
		{
			string retval = null;

			if(args.Length >= 2) {
				switch (args[1].ToLower())
				{
					case "ipv6":
					retval = Firewall.VIPER_RULE_IPv6;
					break;
					case "defgateway":
					retval = Firewall.VIPER_RULE_DEFGATEWAY;
					break;
					case "allports":
					retval = Firewall.VIPER_RULE_ALLPORTS;
					break;
				}
			}

			return retval;
		}

//		private string[] ParseRuleParameters(string[] args) 
//		{
//		}

		public void go(string []args) {
			this.fwall = new Firewall();
			bool retval = true;

			if (!this.fwall.FirewallEnabled) System.Environment.Exit(2);

			string rule = ParseRuleFromCli(args);
			//string[] parameters = ParseRuleParameters(rule, args);

			if (args.Length > 0)
			{
				switch (args[0].ToLower())
				{
					case "add":
						retval = this.fwall.AddRule(rule, null);
						break;
					case "remove":
						retval = this.fwall.RemoveRule(rule);
						break;
					case "enable":
						retval = this.fwall.EnableRule(rule);
						break;
					case "disable":
						retval = this.fwall.DisableRule(rule);
						break;
					case "usage":
						this.fwall.Usage();
						retval = true;
					break;
				}
			}
			else
			{
				this.fwall.Usage();
			}

			// set system return code to be read from calling script
			if (false == retval)
			{
				System.Environment.Exit(1);
			}
			else
			{
				System.Environment.Exit(0);
			}
		} // go(string [])

        static void Main(string[] args)
        {
        	new Program().go(args);
        } // Main

    } // class

} // ns
