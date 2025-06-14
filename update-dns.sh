#!/bin/bash

# Interface to monitor (change this to your actual interface if needed)
IFACE="wlp2s0"
HOSTNAME="pyplayer.local"
HOSTS_FILE="/etc/hosts"

# Get current IP address of the interface
IP=$(ip -4 addr show "$IFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

if [ -z "$IP" ]; then
  echo "❌ ERROR: Could not determine IP for interface $IFACE"
  exit 1
fi

# Backup current /etc/hosts
cp "$HOSTS_FILE" "$HOSTS_FILE.bak"

# Remove any existing pyplayer.local line
grep -v "$HOSTNAME" "$HOSTS_FILE.bak" >/tmp/hosts.tmp

# Add updated line
echo "$IP    $HOSTNAME" >>/tmp/hosts.tmp

# Replace /etc/hosts
sudo cp /tmp/hosts.tmp "$HOSTS_FILE"
rm /tmp/hosts.tmp

echo "✅ Updated $HOSTS_FILE: $HOSTNAME -> $IP"
