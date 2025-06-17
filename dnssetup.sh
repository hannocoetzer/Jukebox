#!/bin/bash

# Complete solution for pyplayer.local resolution across all devices
# This script sets up both mDNS (Avahi) and local DNS (dnsmasq) properly

set -e

HOSTNAME="pyplayer"
DOMAIN="local"
FULL_HOSTNAME="${HOSTNAME}.${DOMAIN}"

echo "🔧 Setting up universal hostname resolution for ${FULL_HOSTNAME}"

# Get current IP address
get_local_ip() {
  # Get the primary network interface IP (not loopback)
  ip route get 1.1.1.1 | grep -oP 'src \K\S+' 2>/dev/null ||
    hostname -I | awk '{print $1}' | head -n1
}

CURRENT_IP=$(get_local_ip)
echo "📍 Current IP: $CURRENT_IP"

# 1. Set system hostname
echo "🏷️  Setting system hostname..."
sudo hostnamectl set-hostname "$HOSTNAME"
echo "127.0.1.1 $HOSTNAME" | sudo tee -a /etc/hosts >/dev/null

# 2. Configure Avahi properly
echo "📡 Configuring Avahi (mDNS)..."
sudo apt-get update
sudo apt-get install -y avahi-daemon avahi-utils

# Create proper Avahi configuration
sudo tee /etc/avahi/avahi-daemon.conf >/dev/null <<EOF
[server]
host-name=$HOSTNAME
domain-name=$DOMAIN
browse-domains=$DOMAIN
use-ipv4=yes
use-ipv6=no
allow-interfaces=
deny-interfaces=
check-response-ttl=no
use-iff-running=no
enable-dbus=yes
disallow-other-stacks=no
allow-point-to-point=no
cache-entries-max=4096
clients-max=4096
objects-per-client-max=1024
entries-per-entry-group-max=32
ratelimit-interval-usec=1000000
ratelimit-burst=1000

[wide-area]
enable-wide-area=yes

[publish]
disable-publishing=no
disable-user-service-publishing=no
add-service-cookie=no
publish-addresses=yes
publish-hinfo=yes
publish-workstation=yes
publish-domain=yes
publish-dns-servers=
publish-resolv-conf-dns-servers=yes
publish-aaaa-on-ipv4=yes
publish-a-on-ipv6=no

[reflector]
enable-reflector=no
reflect-ipv=no

[rlimits]
rlimit-as=
rlimit-core=0
rlimit-data=8388608
rlimit-fsize=0
rlimit-nofile=768
rlimit-stack=8388608
rlimit-nproc=3
EOF

# 3. Install and configure dnsmasq as local DNS server
echo "🌐 Setting up dnsmasq for broader device compatibility..."
sudo apt-get install -y dnsmasq

# Backup original dnsmasq config
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true

# Create new dnsmasq configuration
sudo tee /etc/dnsmasq.conf >/dev/null <<EOF
# Listen on localhost and local IP
listen-address=127.0.0.1,$CURRENT_IP

# Don't read /etc/hosts for DNS (we'll use our own entries)
no-hosts

# Use /etc/hosts.dnsmasq for local entries
addn-hosts=/etc/hosts.dnsmasq

# Set local domain
local=/$DOMAIN/
domain=$DOMAIN

# Expand simple names
expand-hosts

# Don't forward short names
domain-needed

# Don't forward addresses in the non-routed address spaces
bogus-priv

# Cache size
cache-size=1000

# Log queries for debugging (remove in production)
log-queries

# Interface to listen on (auto-detect primary interface)
interface=$(ip route | grep default | awk '{print $5}' | head -n1)

# DHCP range (optional - only if you want DHCP)
# dhcp-range=192.168.1.100,192.168.1.200,12h
EOF

# 4. Create hosts file for dnsmasq
echo "📝 Creating DNS entries..."
sudo tee /etc/hosts.dnsmasq >/dev/null <<EOF
# Local hostname entries for dnsmasq
$CURRENT_IP $FULL_HOSTNAME $HOSTNAME
EOF

# 5. Configure systemd-resolved to work with dnsmasq
echo "⚙️  Configuring systemd-resolved..."
sudo mkdir -p /etc/systemd/resolved.conf.d
sudo tee /etc/systemd/resolved.conf.d/dnsmasq.conf >/dev/null <<EOF
[Resolve]
DNS=127.0.0.1
Domains=~$DOMAIN
DNSStubListener=no
EOF

# 6. Update /etc/resolv.conf to use our local DNS
echo "🔄 Updating DNS resolution..."
sudo rm -f /etc/resolv.conf
sudo tee /etc/resolv.conf >/dev/null <<EOF
nameserver 127.0.0.1
nameserver 8.8.8.8
nameserver 8.8.4.4
search $DOMAIN
EOF

# Make resolv.conf immutable to prevent overwriting
sudo chattr +i /etc/resolv.conf 2>/dev/null || true

# 7. Start and enable services
echo "🚀 Starting services..."
sudo systemctl enable avahi-daemon
sudo systemctl restart avahi-daemon
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq
sudo systemctl restart systemd-resolved

# 8. Create update script for IP changes
echo "📜 Creating IP update script..."
sudo tee /usr/local/bin/update-hostname-ip.sh >/dev/null <<'EOF'
#!/bin/bash

HOSTNAME="pyplayer"
DOMAIN="local"
FULL_HOSTNAME="${HOSTNAME}.${DOMAIN}"

get_local_ip() {
    ip route get 1.1.1.1 | grep -oP 'src \K\S+' 2>/dev/null || \
    hostname -I | awk '{print $1}' | head -n1
}

NEW_IP=$(get_local_ip)
CURRENT_IP=$(grep "$FULL_HOSTNAME" /etc/hosts.dnsmasq | awk '{print $1}' | head -n1)

if [ "$NEW_IP" != "$CURRENT_IP" ]; then
    echo "IP changed from $CURRENT_IP to $NEW_IP"
    
    # Update dnsmasq hosts file
    sudo sed -i "s/$CURRENT_IP $FULL_HOSTNAME/$NEW_IP $FULL_HOSTNAME/" /etc/hosts.dnsmasq
    
    # Update dnsmasq config
    sudo sed -i "s/listen-address=127.0.0.1,$CURRENT_IP/listen-address=127.0.0.1,$NEW_IP/" /etc/dnsmasq.conf
    
    # Restart services
    sudo systemctl restart dnsmasq
    sudo systemctl restart avahi-daemon
    
    echo "Updated $FULL_HOSTNAME to $NEW_IP"
else
    echo "IP unchanged: $CURRENT_IP"
fi
EOF

sudo chmod +x /usr/local/bin/update-hostname-ip.sh

# 9. Create systemd timer for automatic IP updates
echo "⏰ Setting up automatic IP monitoring..."
sudo tee /etc/systemd/system/update-hostname-ip.service >/dev/null <<EOF
[Unit]
Description=Update hostname IP mapping
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/update-hostname-ip.sh
EOF

sudo tee /etc/systemd/system/update-hostname-ip.timer >/dev/null <<EOF
[Unit]
Description=Update hostname IP mapping every 5 minutes
Requires=update-hostname-ip.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

sudo systemctl enable update-hostname-ip.timer
sudo systemctl start update-hostname-ip.timer

# 10. Configure router DNS (instructions)
echo ""
echo "🏠 IMPORTANT: Configure your router's DNS settings"
echo "   To make this work on ALL devices, configure your router to use"
echo "   $CURRENT_IP as a DNS server alongside your ISP's DNS."
echo ""
echo "   Router settings typically found at:"
echo "   - Primary DNS: $CURRENT_IP"
echo "   - Secondary DNS: 8.8.8.8 (or your ISP's DNS)"
echo ""

# 11. Test the setup
echo "🧪 Testing configuration..."
sleep 3

# Test local resolution
if nslookup "$FULL_HOSTNAME" 127.0.0.1 >/dev/null 2>&1; then
  echo "✅ Local DNS resolution working"
else
  echo "❌ Local DNS resolution failed"
fi

# Test Avahi
if avahi-resolve -n "$FULL_HOSTNAME" >/dev/null 2>&1; then
  echo "✅ Avahi mDNS working"
else
  echo "❌ Avahi mDNS failed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Summary:"
echo "   • Hostname: $FULL_HOSTNAME"
echo "   • IP Address: $CURRENT_IP"
echo "   • Local DNS Server: $CURRENT_IP:53"
echo "   • mDNS (Avahi): Enabled"
echo "   • Auto IP Updates: Every 5 minutes"
echo ""
echo "🔗 Test URLs:"
echo "   • Web Interface: http://$FULL_HOSTNAME:8080/play.html"
echo "   • Icecast Stream: http://$FULL_HOSTNAME:8000/stream.mp3"
echo ""
echo "📱 For devices that still can't resolve $FULL_HOSTNAME:"
echo "   1. Configure router DNS to include $CURRENT_IP"
echo "   2. Or manually set device DNS to $CURRENT_IP"
echo "   3. Android: WiFi Settings → Advanced → DNS → Custom"
echo "   4. Windows: Network Settings → Change Adapter Options → Properties → IPv4"
echo ""
echo "🔧 Manual IP update: sudo /usr/local/bin/update-hostname-ip.sh"
echo "📊 Check status: systemctl status update-hostname-ip.timer"
