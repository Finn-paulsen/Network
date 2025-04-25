import os
import time
import random
import string
import hashlib
import socket
import threading
import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app import app
from models import User
from forms import LoginForm, RegisterForm, NetworkScanForm, TerminalCommandForm, FirewallRuleForm, BruteForceForm, ExploitScannerForm, MalwareSimulatorForm
from network_utils import scan_network, get_host_details
from firewall_utils import add_firewall_rule, get_firewall_rules, delete_firewall_rule
import subprocess
import logging

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.get_by_username(form.username.data)
        if existing_user:
            flash('Username already exists', 'danger')
        else:
            user = User(username=form.username.data, password=form.password.data)
            user.save()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/scanner', methods=['GET', 'POST'])
@login_required
def scanner():
    form = NetworkScanForm()
    scan_results = []
    
    if form.validate_on_submit():
        target = form.target.data
        scan_results = scan_network(target)
    
    return render_template('scanner.html', form=form, scan_results=scan_results)

@app.route('/terminal', methods=['GET', 'POST'])
@login_required
def terminal():
    form = TerminalCommandForm()
    output = ""
    
    if form.validate_on_submit():
        command = form.command.data.strip()
        
        # Whitelist of allowed commands for safety
        allowed_commands = {
            # Network diagnostics
            'ping': ['ping'],
            'traceroute': ['traceroute'],
            'nslookup': ['nslookup'],
            'dig': ['dig'],
            'host': ['host'],
            'whois': ['whois'],
            'ifconfig': ['ifconfig'],
            'ipconfig': ['ipconfig'],
            'netstat': ['netstat'],
            
            # Extended network tools
            'arp': ['arp'],
            'route': ['route'],
            'nmap': ['echo', 'Simulated NMAP scan (education purpose only):\n\nStarting Nmap scan...\nScanning targets...\nPort scanning complete\n\nOpen ports found:'],
            'curl': ['curl', '-s', '-I'],
            'wget': ['echo', 'File download simulated successfully.'],
            
            # System info (simulated for safety)
            'ps': ['ps'],
            'top': ['echo', 'System monitoring simulated (education purpose only):\n\nCPU: 23% used\nMemory: 4.2GB/8GB\nProcesses: 124 running'],
            'uname': ['uname', '-a'],
            
            # File operations (simulated)
            'ls': ['ls', '-la', '/tmp'],
            'cat': ['echo', 'File contents displayed (simulated)'],
            'find': ['echo', 'File search simulated - found 5 matching files'],
            
            # Others
            'echo': ['echo'],
            'date': ['date'],
            'help': ['echo', 'Available commands: ping, traceroute, nslookup, dig, host, whois, ifconfig, ipconfig, netstat, arp, route, nmap, curl, wget, ps, top, uname, ls, cat, find, echo, date, help']
        }
        
        # Parse the command and check if it's allowed
        cmd_parts = command.split()
        if not cmd_parts:
            output = "Error: Empty command. Type 'help' to see available commands."
        elif cmd_parts[0] not in allowed_commands:
            output = f"[!] Command '{cmd_parts[0]}' not recognized. Type 'help' to see available commands."
        else:
            try:
                base_cmd = allowed_commands[cmd_parts[0]]
                
                # Special handling for certain commands
                if cmd_parts[0] == 'curl' and len(cmd_parts) > 1:
                    # For curl, we only allow fetching headers with -I flag for safety
                    exec_cmd = base_cmd + [cmd_parts[1]]
                elif cmd_parts[0] == 'echo' and len(cmd_parts) > 1:
                    # For echo, include all arguments
                    exec_cmd = [base_cmd[0]] + cmd_parts[1:]
                elif cmd_parts[0] in ['nmap', 'top', 'cat', 'find']:
                    # These commands are fully simulated
                    if cmd_parts[0] == 'nmap' and len(cmd_parts) > 1:
                        # Add target IP to output for more realism
                        exec_cmd = base_cmd + [f"\n\nPort 22 (SSH): open\nPort 80 (HTTP): open\nPort 443 (HTTPS): open\n\nHost {cmd_parts[1]} appears to be running a web server and SSH."]
                    else:
                        exec_cmd = base_cmd
                else:
                    # For other commands, use the first element of allowed_commands and append user arguments
                    if len(cmd_parts) > 1:
                        exec_cmd = [base_cmd[0]] + cmd_parts[1:]
                    else:
                        exec_cmd = base_cmd
                
                # Execute command with timeout for safety
                result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=10)
                output = result.stdout if result.stdout else result.stderr
                
                # If output is empty, provide a success message
                if not output.strip():
                    output = f"Command '{cmd_parts[0]}' executed successfully with no output."
                    
            except subprocess.TimeoutExpired:
                output = "[!] Error: Command execution timed out"
            except Exception as e:
                logging.error(f"Terminal error: {str(e)}")
                output = f"[!] Error executing command: {str(e)}"
    
    return render_template('terminal.html', form=form, output=output)

@app.route('/firewall', methods=['GET', 'POST'])
@login_required
def firewall():
    form = FirewallRuleForm()
    rules = get_firewall_rules()
    
    if form.validate_on_submit():
        source_ip = form.source_ip.data
        destination_ip = form.destination_ip.data
        action = form.action.data
        
        if action.lower() not in ['allow', 'deny']:
            flash('Invalid action. Use "allow" or "deny"', 'danger')
        else:
            success = add_firewall_rule(source_ip, destination_ip, action)
            if success:
                flash('Firewall rule added successfully', 'success')
                return redirect(url_for('firewall'))
            else:
                flash('Failed to add firewall rule', 'danger')
    
    return render_template('firewall.html', form=form, rules=rules)

@app.route('/api/host_details/<ip>', methods=['GET'])
@login_required
def host_details_api(ip):
    details = get_host_details(ip)
    return jsonify(details)

@app.route('/api/delete_firewall_rule/<int:rule_id>', methods=['POST'])
@login_required
def delete_rule(rule_id):
    success = delete_firewall_rule(rule_id)
    if success:
        flash('Rule deleted successfully', 'success')
    else:
        flash('Failed to delete rule', 'danger')
    return redirect(url_for('firewall'))

@app.route('/brute-force', methods=['GET', 'POST'])
@login_required
def brute_force():
    form = BruteForceForm()
    result = None
    found = False
    attempts = 0
    elapsed_time = 0
    password_found = None
    
    if form.validate_on_submit():
        start_time = time.time()
        target_type = form.target_type.data
        target_value = form.target_value.data
        character_set = form.character_set.data
        min_length = form.min_length.data
        max_length = form.max_length.data
        
        # Define character sets
        chars = {
            'numeric': string.digits,
            'alpha': string.ascii_lowercase,
            'alphanumeric': string.ascii_lowercase + string.digits,
            'full': string.ascii_letters + string.digits + string.punctuation
        }
        
        # For simulation purposes, we'll limit the possibilities
        # and control the runtime for educational purposes
        found, password_found, attempts = simulate_brute_force(
            target_type=target_type,
            target_value=target_value, 
            charset=chars[character_set],
            min_length=min_length,
            max_length=max_length
        )
        
        elapsed_time = time.time() - start_time
        
        result = {
            'target_type': target_type,
            'target_value': target_value,
            'character_set': character_set,
            'attempts': attempts,
            'elapsed_time': elapsed_time,
            'found': found,
            'password_found': password_found if found else None
        }
    
    return render_template('brute_force.html', form=form, result=result)

@app.route('/exploit-scanner', methods=['GET', 'POST'])
@login_required
def exploit_scanner():
    form = ExploitScannerForm()
    result = None
    
    if form.validate_on_submit():
        target_url = form.target_url.data
        scan_type = form.scan_type.data
        intensity = form.intensity.data
        
        # Simulate a vulnerability scan
        result = simulate_vulnerability_scan(target_url, scan_type, intensity)
    
    return render_template('exploit_scanner.html', form=form, result=result)

@app.route('/malware-simulator', methods=['GET', 'POST'])
@login_required
def malware_simulator():
    form = MalwareSimulatorForm()
    result = None
    
    if form.validate_on_submit():
        target_system = form.target_system.data
        malware_type = form.malware_type.data
        simulation_only = form.simulation_only.data
        propagation = form.propagation.data
        
        # This is just a simulation for educational purposes
        result = simulate_malware_behavior(
            target_system=target_system,
            malware_type=malware_type,
            simulation_only=simulation_only,
            propagation=propagation
        )
    
    return render_template('malware_simulator.html', form=form, result=result)

# Simulation functions for educational purposes only

def simulate_brute_force(target_type, target_value, charset, min_length, max_length):
    """
    Simulates a brute force attack for educational purposes only.
    Returns: (found, password_found, attempts)
    """
    # For safety and educational purposes, we'll simulate the process
    # and always return after a reasonable number of attempts
    max_attempts = 1000
    attempts = 0
    
    # For simulation, if target is a PIN, we'll "find" it as long as it's numeric
    # Otherwise, we'll randomly decide if we find it or not
    if target_type == 'pin' and target_value.isdigit() and len(target_value) <= 6:
        # Simulate a successful PIN cracking
        time.sleep(random.uniform(0.5, 2.0))  # Simulate processing time
        return (True, target_value, random.randint(50, max_attempts))
    
    # For passwords, simulate success if length is reasonable
    elif target_type == 'password' and len(target_value) <= max_length:
        success_chance = 0.7 if len(target_value) <= 3 else 0.3
        found = random.random() < success_chance
        
        # Make the simulation time proportional to the complexity
        simulation_time = 0.5 * (2 ** (min(len(target_value), 5) - 1))
        time.sleep(simulation_time)
        
        if found:
            return (True, target_value, random.randint(100, max_attempts))
    
    # For hash cracking, simulate by checking if it looks like a hash
    elif target_type == 'hash' and len(target_value) >= 32:
        # For education: simulate a harder time cracking hashes
        time.sleep(random.uniform(1.5, 3.0))
        
        # Simulate a low success chance for hashes
        found = random.random() < 0.2
        if found:
            # Generate a plausible password that could've created the hash
            fake_password = ''.join(random.choices(charset, k=random.randint(4, 6)))
            return (True, fake_password, random.randint(500, max_attempts))
    
    # Default: unsuccessful brute force
    return (False, None, random.randint(max_attempts // 2, max_attempts))

def simulate_vulnerability_scan(target_url, scan_type, intensity):
    """
    Simulates a vulnerability scan for educational purposes.
    No actual scanning is performed.
    """
    # Validate IP or URL format
    if not (target_url.startswith('http') or is_valid_ip_format(target_url)):
        return {
            'status': 'error',
            'message': 'Invalid target URL or IP format'
        }
    
    # Simulate scanning time based on intensity
    if intensity == 'low':
        time.sleep(random.uniform(1.0, 2.0))
    elif intensity == 'medium':
        time.sleep(random.uniform(2.0, 3.0))
    else:  # high
        time.sleep(random.uniform(3.0, 4.0))
    
    # Generate educational scan results
    vulnerabilities = []
    
    # Common vulnerabilities for educational demonstrations
    vuln_database = {
        'basic': [
            {'name': 'Obsolete HTTP Headers', 'severity': 'low', 'cve': 'N/A'},
            {'name': 'Missing Security Headers', 'severity': 'medium', 'cve': 'N/A'},
            {'name': 'Information Disclosure', 'severity': 'low', 'cve': 'CVE-2021-XXXX'}
        ],
        'advanced': [
            {'name': 'Potential XSS Vulnerability', 'severity': 'high', 'cve': 'CVE-2020-XXXX'},
            {'name': 'Session Management Issue', 'severity': 'medium', 'cve': 'CVE-2019-XXXX'},
            {'name': 'Weak Password Policy', 'severity': 'medium', 'cve': 'N/A'},
            {'name': 'Insecure Cookie Flags', 'severity': 'low', 'cve': 'N/A'}
        ],
        'dos': [
            {'name': 'Potential DoS Vulnerability', 'severity': 'critical', 'cve': 'CVE-2022-XXXX'},
            {'name': 'Resource Exhaustion Risk', 'severity': 'high', 'cve': 'N/A'}
        ],
        'sqli': [
            {'name': 'Potential SQL Injection', 'severity': 'critical', 'cve': 'CVE-2021-XXXX'},
            {'name': 'Database Error Disclosure', 'severity': 'medium', 'cve': 'N/A'}
        ],
        'xss': [
            {'name': 'Reflected XSS Vulnerability', 'severity': 'high', 'cve': 'CVE-2020-XXXX'},
            {'name': 'Stored XSS Vulnerability', 'severity': 'critical', 'cve': 'CVE-2019-XXXX'},
            {'name': 'DOM-based XSS Risk', 'severity': 'medium', 'cve': 'N/A'}
        ]
    }
    
    # Add some specific vulnerabilities based on scan type
    if scan_type in vuln_database:
        for vuln in vuln_database[scan_type]:
            # Randomize finding vulnerabilities
            if random.random() < 0.7:  # 70% chance to "find" each vulnerability
                vulnerabilities.append(vuln)
    
    # Add some random general vulnerabilities
    general_vulns = [
        {'name': 'Outdated Software Version', 'severity': 'medium', 'cve': 'N/A'},
        {'name': 'Insecure Transport Layer', 'severity': 'medium', 'cve': 'N/A'},
        {'name': 'Default Credentials Risk', 'severity': 'high', 'cve': 'N/A'}
    ]
    
    for vuln in general_vulns:
        if random.random() < 0.3:  # 30% chance to add each general vulnerability
            vulnerabilities.append(vuln)
    
    # Count vulnerabilities by severity
    severity_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for vuln in vulnerabilities:
        if vuln['severity'] in severity_counts:
            severity_counts[vuln['severity']] += 1
    
    return {
        'status': 'completed',
        'target': target_url,
        'scan_type': scan_type,
        'intensity': intensity,
        'vulnerabilities': vulnerabilities,
        'severity_counts': severity_counts,
        'total_vulnerabilities': len(vulnerabilities),
        'scan_time': random.uniform(1.5, 5.0),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def simulate_malware_behavior(target_system, malware_type, simulation_only, propagation):
    """
    Simulates malware behavior for educational purposes.
    No actual malicious activity is performed.
    """
    # This is purely educational - no real malware functionality
    simulation_time = random.uniform(1.5, 3.0)
    time.sleep(simulation_time)
    
    # Sample behaviors for different malware types
    behaviors = {
        'ransomware': [
            'Scanning for document files',
            'File encryption simulation',
            'Ransom note creation (simulated)',
            'Encryption key generation'
        ],
        'trojan': [
            'Backdoor connection simulation',
            'Simulated data exfiltration',
            'Command & control communication',
            'User activity monitoring'
        ],
        'virus': [
            'Self-replication mechanism',
            'File infection simulation',
            'Boot sector analysis',
            'System modification attempt'
        ],
        'worm': [
            'Network scanning simulation',
            'Remote exploit simulation',
            'Propagation via network shares',
            'Self-replication routine'
        ],
        'rootkit': [
            'System hooking simulation',
            'Process hiding techniques',
            'Privilege escalation attempt',
            'System file modification (simulated)'
        ]
    }
    
    # Propagation methods
    propagation_methods = {
        'email': [
            'Crafting malicious email templates',
            'Attachment preparation',
            'Social engineering content creation',
            'Email header spoofing'
        ],
        'network': [
            'Network vulnerability scanning',
            'SMB exploitation simulation',
            'Lateral movement techniques',
            'Network share targeting'
        ],
        'usb': [
            'Autorun mechanism simulation',
            'USB device detection',
            'File dropper routine',
            'Shortcut file creation'
        ],
        'download': [
            'Fake update notification',
            'Drive-by download simulation',
            'Traffic redirection technique',
            'Malicious payload disguise'
        ]
    }
    
    # Generate the simulation stages
    stages = []
    
    # Initial infection
    stages.append({
        'name': 'Initial Infection',
        'actions': random.sample(propagation_methods.get(propagation, ['Generic infection method']), 
                               k=min(2, len(propagation_methods.get(propagation, ['']))))
    })
    
    # Core malware behavior
    stages.append({
        'name': 'Malware Execution',
        'actions': random.sample(behaviors.get(malware_type, ['Generic malware behavior']), 
                               k=min(3, len(behaviors.get(malware_type, ['']))))
    })
    
    # Defense evasion
    evasion_techniques = [
        'Process injection simulation',
        'Anti-VM detection techniques',
        'Timestamp modification',
        'Sleep timer to evade sandboxes',
        'Code obfuscation simulation'
    ]
    
    stages.append({
        'name': 'Defense Evasion',
        'actions': random.sample(evasion_techniques, k=random.randint(1, 3))
    })
    
    # Target-specific actions
    target_actions = [
        f'Targeting {target_system} specific vulnerabilities',
        f'Checking for {target_system} security features',
        f'Adapting to {target_system} environment'
    ]
    
    stages.append({
        'name': 'Target Analysis',
        'actions': target_actions
    })
    
    return {
        'status': 'completed',
        'target_system': target_system,
        'malware_type': malware_type,
        'simulation_only': simulation_only,
        'propagation': propagation,
        'stages': stages,
        'simulation_time': simulation_time,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'educational_note': 'This is purely a simulation for educational purposes.'
    }

def is_valid_ip_format(ip):
    """Check if string looks like a valid IP address"""
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False
