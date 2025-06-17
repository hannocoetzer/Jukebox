#!/bin/bash

echo "🔍 DEBUGGING PYPLAYER.LOCAL RESOLUTION"
echo "======================================"

# Get basic info
HOSTNAME=$(hostname)
CURRENT_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || hostname -I | awk '{print $1}')
echo "📍 Current hostname: $HOSTNAME"
echo "📍 Current IP: $CURRENT_IP"
echo "📍 Date: $(date)"
echo ""

# Check network interface
echo "🌐 NETWORK INTERFACE:"
echo "Primary interface: $(ip route | grep default | awk '{print $5}' | head -n1)"
ip addr show $(ip route | grep default | awk '{print $5}' | head -n1) 2>/dev/null | grep "inet " || echo "❌ Could not get interface info"
echo ""

# Check if services are running
echo "🔧 SERVICE STATUS:"
echo "Avahi daemon:"
systemctl is-active avahi-daemon 2>/dev/null || echo "❌ Not running"
echo "Dnsmasq:"
systemctl is-active dnsmasq 2>/dev/null || echo "❌ Not running"
echo "Systemd-resolved:"
systemctl is-active systemd-resolved 2>/dev/null || echo "❌ Not running"
echo ""

# Check ports
echo "🔌 PORT USAGE:"
echo "Port 53 (DNS):"
sudo netstat -tulnp | grep :53 || echo "No processes on port 53"
echo ""

# Check DNS resolution locally
echo "🧪 LOCAL DNS TESTS:"
echo "Testing nslookup pyplayer.local:"
nslookup pyplayer.local 2>/dev/null || echo "❌ Failed"
echo ""
echo "Testing nslookup pyplayer.local 127.0.0.1:"
nslookup pyplayer.local 127.0.0.1 2>/dev/null || echo "❌ Failed"
echo ""

# Check mDNS
echo "📡 mDNS TESTS:"
echo "Avahi resolve pyplayer.local:"
avahi-resolve -n pyplayer.local 2>/dev/null || echo "❌ Failed"
echo ""
echo "Avahi browse:"
timeout 3 avahi-browse -rt _http._tcp 2>/dev/null || echo "❌ No mDNS services found"
echo ""

# Check configuration files
echo "📁 CONFIGURATION FILES:"
echo ""
echo "/etc/resolv.conf:"
cat /etc/resolv.conf 2>/dev/null || echo "❌ File missing"
echo ""
echo "/etc/hosts:"
grep -E "(pyplayer|127)" /etc/hosts 2>/dev/null || echo "❌ No pyplayer entries"
echo ""
echo "/etc/hosts.dnsmasq:"
cat /etc/hosts.dnsmasq 2>/dev/null || echo "❌ File missing"
echo ""
echo "/etc/dnsmasq.conf (relevant lines):"
grep -E "(listen-address|address=)" /etc/dnsmasq.conf 2>/dev/null || echo "❌ No relevant config found"
echo ""

# Check if files are immutable
echo "🔒 FILE PERMISSIONS:"
lsattr /etc/resolv.conf 2>/dev/null | grep -q "i" && echo "✅ /etc/resolv.conf is immutable" || echo "⚠️ /etc/resolv.conf is not immutable"
echo ""

# Test web services
echo "🌐 WEB SERVICE TESTS:"
echo "Testing local web server:"
curl -s -I http://localhost:8080/play.html 2>/dev/null | head -1 || echo "❌ Web server not responding on :8080"
curl -s -I http://$CURRENT_IP:8080/play.html 2>/dev/null | head -1 || echo "❌ Web server not responding on IP:8080"
echo ""
echo "Testing Icecast:"
curl -s -I http://localhost:8000/stream.mp3 2>/dev/null | head -1 || echo "❌ Icecast not responding on :8000"
curl -s -I http://$CURRENT_IP:8000/stream.mp3 2>/dev/null | head -1 || echo "❌ Icecast not responding on IP:8000"
echo ""

# Check firewall
echo "🛡️ FIREWALL STATUS:"
sudo ufw status 2>/dev/null || echo "UFW not available"
echo ""

# Check logs for errors
echo "📋 RECENT ERROR LOGS:"
echo "Dnsmasq errors (last 5):"
sudo journalctl -u dnsmasq --no-pager -n 5 -p err 2>/dev/null || echo "No dnsmasq logs"
echo ""
echo "Avahi errors (last 5):"
sudo journalctl -u avahi-daemon --no-pager -n 5 -p err 2>/dev/null || echo "No avahi logs"
echo ""

# Test from current device
echo "🔄 RESOLUTION TESTS FROM THIS DEVICE:"
echo "ping pyplayer.local (1 packet):"
ping -c 1 pyplayer.local 2>/dev/null && echo "✅ Ping successful" || echo "❌ Ping failed"
echo ""
echo "wget test:"
timeout 5 wget -q --spider http://pyplayer.local:8080/play.html 2>/dev/null && echo "✅ HTTP accessible via pyplayer.local" || echo "❌ HTTP not accessible via pyplayer.local"
echo ""

echo "======================================"
echo "🎯 QUICK DIAGNOSIS:"
echo ""

# Quick diagnosis
if ! systemctl is-active dnsmasq >/dev/null 2>&1; then
  echo "❌ CRITICAL: dnsmasq is not running"
fi

if ! systemctl is-active avahi-daemon >/dev/null 2>&1; then
  echo "❌ CRITICAL: avahi-daemon is not running"
fi

if ! grep -q "127.0.0.1" /etc/resolv.conf 2>/dev/null; then
  echo "❌ CRITICAL: /etc/resolv.conf doesn't point to local DNS"
fi

if ! [ -f /etc/hosts.dnsmasq ]; then
  echo "❌ CRITICAL: /etc/hosts.dnsmasq missing"
fi

if ! nslookup pyplayer.local 127.0.0.1 >/dev/null 2>&1; then
  echo "❌ CRITICAL: Local DNS resolution not working"
fi

echo ""
echo "🔧 NEXT STEPS:"
echo "1. Run this script and share the output"
echo "2. Try the simplified setup script below"
echo "3. Test step by step"
