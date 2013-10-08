/*
 * Copyright (c) 2013 Greenhost VOF and contributors
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met: 
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer. 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution. 
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * The views and conclusions contained in the software and documentation are those
 * of the authors and should not be interpreted as representing official policies, 
 * either expressed or implied, of the FreeBSD Project.
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

        static string GLOBAL_UNICAST_ADDRESS = "2033::/3";  // IPv6 Global Unicast
        static string VIPER_RULE_NAME = "Viper - Block IPv6";

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

        public bool AddRule()
        {
            // try to find the rule first, if found return successfully
            INetFwRule2 rule = FindRule(VIPER_RULE_NAME);
            if(null != rule) {
                return true;
            }

            // if it's not found, add it
            try
            {
                INetFwRule2 firewallRule = (INetFwRule2)Activator.CreateInstance(Type.GetTypeFromProgID("HNetCfg.FWRule"));

                firewallRule.Name = VIPER_RULE_NAME;
                firewallRule.Description = "Block unwated IPv6 traffic while Viper OpenVPN client is running";
                firewallRule.Action = NET_FW_ACTION_.NET_FW_ACTION_BLOCK;
                firewallRule.Direction = NET_FW_RULE_DIRECTION_.NET_FW_RULE_DIR_OUT;
                firewallRule.Enabled = true;
                firewallRule.Protocol = (int)NET_FW_IP_PROTOCOL_.NET_FW_IP_PROTOCOL_ANY; // 6
                firewallRule.RemoteAddresses = GLOBAL_UNICAST_ADDRESS;
                firewallRule.LocalAddresses = GLOBAL_UNICAST_ADDRESS;

                fwpolicy.Rules.Add(firewallRule);

                Console.WriteLine("Adding firewall rule...");
            } catch (Exception e) {
                return false;
            }
            return true;
        }

        public bool RemoveRule()
        {
            try
            {
                Console.WriteLine("Removing firewall rule...");
                fwpolicy.Rules.Remove(VIPER_RULE_NAME);
            } catch (Exception e) {
                return false;
            }
            return true;
        }

        public bool EnableRule()
        {
            bool retval = true;

            INetFwRule2 rule = FindRule(VIPER_RULE_NAME);
            if (null != rule)
            {
                Console.WriteLine("Enabling firewall rule...");
                rule.Enabled = true;
                Marshal.ReleaseComObject(rule);
            }
            else
            {
                Console.WriteLine("Couldn't enable firewall rule " + VIPER_RULE_NAME + " because I coudn't find it.");
                retval = false;
            }

            return retval;
        }

        public void Usage() {
            Console.WriteLine("Viper command line interface to the Windows Firewall");
            Console.WriteLine("(c) 2013 Greenhost VOF\n");
            Console.WriteLine(@"fwipv6 manages the Windows Firewall to block all IPv6 traffic. For it to work it must be executed with elevated privileges.\n

Usage:
    fwipv6 add       -   adds rule
    fwipv6 remove    -   removes rule
    fwipv6 enable    -   enables the rule (rule must exist in current profile)
    fwipv6 disable   -   disables the rule (rule must exist in current profile)
    fwipv6 usage     -   prints this text
");
        }

        public bool DisableRule()
        {
            bool retval = true;

            INetFwRule2 rule = FindRule(VIPER_RULE_NAME);
            if (null != rule)
            {
                Console.WriteLine("Disabling firewall rule...");
                rule.Enabled = false;
                Marshal.ReleaseComObject(rule);
            }
            else
            {
                Console.WriteLine("Couldn't disable firewall rule " + VIPER_RULE_NAME + " because I coudn't find it.");
                retval = false;
            }

            return retval;
        }

    } // class

    class Program
    {
        static void Main(string[] args)
        {
            Firewall fw = new Firewall();
            bool retval = true;

            if (!fw.FirewallEnabled) System.Environment.Exit(2);

            if (args.Length > 0)
            {
                switch (args[0].ToLower())
                {
                    case "add":
                        retval = fw.AddRule();
                        break;
                    case "remove":
                        retval = fw.RemoveRule();
                        break;
                    case "enable":
                        retval = fw.EnableRule();
                        break;
                    case "disable":
                        retval = fw.DisableRule();
                        break;
                    case "usage":
                        fw.Usage();
                        retval = true;
                        break;
                }
            }
            else
            {
                fw.Usage();
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
        } // Main

    } // class

} // ns
