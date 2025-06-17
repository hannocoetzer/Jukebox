#!/bin/bash

echo "🤬 WTF DEBUG - Let's see what's actually broken"
echo "=============================================="

echo "📍 Current status:"
ip addr show | grep "inet " | grep -v "127.0.0.1"
echo ""

echo "🔍 What's listening on port 53:"
sudo ss -tulnp | grep ":53 " || echo "Nothing on port 53"
echo ""

echo "🔍 What's listening on port 5353:"
sudo ss -tulnp | grep ":5353 " || echo "Nothing on port 5353"
echo ""

echo "🔧 Service status:"
echo "systemd-resolved: $(systemctl is-active systemd-resolved 2>/dev/null || echo 'inactive')"
echo "dnsmasq: $(systemctl is-active dnsmasq 2>/dev/null || echo 'inactive')"
echo "avahi: $(systemctl is-active avahi-daemon 2>/dev/null || echo 'inactive')"
echo ""

echo "📄 dnsmasq config:"
echo "Last 10 lines of /etc/dnsmasq.conf:"
tail -10 /etc/dnsmasq.conf 2>/dev/null || echo "Can't read dnsmasq.conf"
echo ""

echo "📄 hosts.dnsmasq:"
cat /etc/hosts.dnsmasq 2>/dev/null || echo "hosts.dnsmasq missing"
echo ""

echo "🚨 dnsmasq logs (last 10 lines):"
sudo journalctl -u dnsmasq --no-pager -n 10 || echo "No dnsmasq logs"
echo ""

echo "🧪 BRUTAL TESTS:"
echo ""

echo "Test 1: Direct dnsmasq test"
echo "nslookup pyplayer.local 127.0.0.1:"
nslookup pyplayer.local 127.0.0.1 2>&1 || echo "FAILED"
echo ""

echo "Test 2: Dig test"
echo "dig @127.0.0.1 pyplayer.local:"
dig @127.0.0.1 pyplayer.local +short 2>&1 || echo "FAILED"
echo ""

echo "Test 3: What does /etc/resolv.conf say:"
cat /etc/resolv.conf
echo ""

echo "Test 4: Can we resolve anything via 127.0.0.1:"
echo "nslookup google.com 127.0.0.1:"
nslookup google.com 127.0.0.1 2>&1 | head -5 || echo "FAILED"
echo ""

echo "🔥 NUCLEAR OPTION - Let's restart everything and see what happens:"
echo ""

echo "Stopping all DNS services..."
sudo systemctl stop systemd-resolved dnsmasq avahi-daemon 2>/dev/null

echo "Waiting 3 seconds..."
sleep 3

echo "Starting dnsmasq only..."
sudo systemctl start dnsmasq

echo "Checking if dnsmasq actually started:"
sleep 2
systemctl is-active dnsmasq && echo "✅ dnsmasq is active" || echo "❌ dnsmasq failed to start"

echo ""
echo "What's on port 53 now:"
sudo ss -tulnp | grep ":53 " || echo "Still nothing on port 53"

echo ""
echo "dnsmasq process check:"
ps aux | grep dnsmasq | grep -v grep || echo "No dnsmasq process found"

echo ""
echo "🔧 MANUAL DNSMASQ TEST:"
echo "Let's try starting dnsmasq manually to see errors..."
echo ""

sudo dnsmasq --test --conf-file=/etc/dnsmasq.conf 2>&1 || echo "Config test failed"

echo ""
echo "🎯 SIMPLE WORKING SOLUTION:"
echo "Forget all this DNS server bullshit. Your ping already works!"
echo ""
echo "Just do this on each device:"
echo ""
echo "=== WINDOWS ==="
echo "1. Open Command Prompt as Administrator"
echo "2. Run: echo 192.168.0.105 pyplayer.local >> C:\\Windows\\System32\\drivers\\etc\\hosts"
echo ""
echo "=== MAC/LINUX ==="
echo "1. Run: echo '192.168.0.105 pyplayer.local' | sudo tee -a /etc/hosts"
echo ""
echo "=== ANDROID ==="
echo "1. Use 'Hosts Editor' app (needs root)"
echo "2. Add: 192.168.0.105 pyplayer.local"
echo ""
echo "THIS WILL WORK 100% and takes 30 seconds per device"
echo ""
echo "Or just use the IP address: http://192.168.0.105:8080/play.html"
