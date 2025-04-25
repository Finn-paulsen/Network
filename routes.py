import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app import app
from models import User
from forms import LoginForm, RegisterForm, NetworkScanForm, TerminalCommandForm, FirewallRuleForm
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
        allowed_commands = ['ping', 'traceroute', 'nslookup', 'dig', 'host', 'whois', 'ifconfig', 'ipconfig', 'netstat']
        
        # Parse the command to check if it's allowed
        cmd_parts = command.split()
        if not cmd_parts:
            output = "Error: Empty command"
        elif cmd_parts[0] not in allowed_commands:
            output = f"Error: Command '{cmd_parts[0]}' is not allowed. Allowed commands: {', '.join(allowed_commands)}"
        else:
            try:
                # Execute command with timeout for safety
                result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=10)
                output = result.stdout if result.stdout else result.stderr
            except subprocess.TimeoutExpired:
                output = "Error: Command execution timed out"
            except Exception as e:
                output = f"Error executing command: {str(e)}"
    
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
