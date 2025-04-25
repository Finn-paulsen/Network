import logging
import os
from datetime import datetime

# In-memory storage for firewall rules
firewall_rules = []
rule_id_counter = 1

def add_firewall_rule(source_ip, destination_ip, action):
    """
    Add a new firewall rule
    Returns True if successful, False otherwise
    """
    global rule_id_counter
    try:
        # Validate IPs (basic validation)
        if not is_valid_ip(source_ip) or not is_valid_ip(destination_ip):
            logging.error(f"Invalid IP address in firewall rule: {source_ip} -> {destination_ip}")
            return False
            
        # Validate action
        if action.lower() not in ['allow', 'deny']:
            logging.error(f"Invalid firewall action: {action}")
            return False
            
        # Create rule
        rule = {
            'id': rule_id_counter,
            'source_ip': source_ip,
            'destination_ip': destination_ip,
            'action': action.lower(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active'
        }
        
        firewall_rules.append(rule)
        rule_id_counter += 1
        
        # In a real application, this would interface with iptables or another firewall system
        logging.info(f"Added firewall rule: {source_ip} -> {destination_ip}, {action}")
        return True
    except Exception as e:
        logging.error(f"Error adding firewall rule: {str(e)}")
        return False

def delete_firewall_rule(rule_id):
    """
    Delete a firewall rule by ID
    Returns True if successful, False otherwise
    """
    global firewall_rules
    try:
        rule_id = int(rule_id)
        for i, rule in enumerate(firewall_rules):
            if rule['id'] == rule_id:
                del firewall_rules[i]
                logging.info(f"Deleted firewall rule ID {rule_id}")
                return True
        logging.warning(f"Firewall rule ID {rule_id} not found")
        return False
    except Exception as e:
        logging.error(f"Error deleting firewall rule: {str(e)}")
        return False

def get_firewall_rules():
    """
    Get list of all firewall rules
    """
    return firewall_rules

def is_valid_ip(ip):
    """
    Simple IP validation
    """
    parts = ip.split('.')
    
    # Check if wildcard is used (e.g. 192.168.1.*)
    if ip.endswith('.*'):
        parts = ip[:-2].split('.')
        if len(parts) != 3:
            return False
    # Normal IP validation    
    elif len(parts) != 4:
        return False
        
    for part in parts:
        if part == '*':
            continue
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    
    return True
