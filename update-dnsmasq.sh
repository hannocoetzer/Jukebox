#!/bin/bash

# Change this to your active network interface name
IFACE="wlp2s0"

# The hostname you want to map
HOSTNAME="pyplayer.local"

# Path to dnsmasq config
DNSMASQ_CONF="/etc/dnsmasq.conf"

# Get the IPv4 address of the interface
IP=$(ip -4 addr show "$IFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

if [[ -z "$IP" ]]; then
  echo "ERROR: Could not find IPv4 address for interface $IFACE"
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  echo "Please run this script with sudo or as root"
  exit 1
fi

echo "Detected IP for $IFACE: $IP"

# Backup the config before modifying
cp "$DNSMASQ_CONF" "$DNSMASQ_CONF.bak.$(date +%F_%T)"

# Append listen-address if not present
if ! grep -q "^listen-address=" "$DNSMASQ_CONF"; then
  echo "listen-address=127.0.0.1,$IP" >>"$DNSMASQ_CONF"
  echo "Added listen-address line"
else
  echo "listen-address line already exists, skipping append"
fi

# Append hostname mapping if not present
if ! grep -q "address=/$HOSTNAME/" "$DNSMASQ_CONF"; then
  echo "address=/$HOSTNAME/$IP" >>"$DNSMASQ_CONF"
  echo "Added hostname mapping"
else
  echo "Hostname mapping already exists, skipping append"
fi

# Restart dnsmasq to apply changes
systemctl restart dnsmasq

echo "dnsmasq restarted. Changes applied."
