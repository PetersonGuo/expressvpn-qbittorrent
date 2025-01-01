#!/usr/bin/expect -f
set timeout -1
spawn expressvpn activate
expect "Enter activation code:"
send "$env(EXPRESSVPN_ACTIVATION_CODE)\r"
expect "Help improve ExpressVPN: Share crash reports, speed tests, usability diagnostics, and whether VPN connection attempts succeed. These reports never contain personally identifiable information. (Y/n)"
send "n"
