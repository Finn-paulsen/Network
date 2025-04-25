document.addEventListener('DOMContentLoaded', function() {
    // Get URL parameters to pre-fill the form if coming from scanner
    const urlParams = new URLSearchParams(window.location.search);
    const sourceIp = urlParams.get('source_ip');
    
    if (sourceIp) {
        const sourceIpField = document.getElementById('source_ip');
        if (sourceIpField) {
            sourceIpField.value = sourceIp;
            
            // Focus the destination IP field
            const destinationIpField = document.getElementById('destination_ip');
            if (destinationIpField) {
                destinationIpField.focus();
            }
        }
    }
    
    // IP validation
    function validateIp(ip) {
        // Allow wildcard notation (e.g. 192.168.1.*)
        if (ip.endsWith('.*')) {
            const prefix = ip.slice(0, -2);
            const parts = prefix.split('.');
            
            if (parts.length !== 3) {
                return false;
            }
            
            for (const part of parts) {
                const num = parseInt(part);
                if (isNaN(num) || num < 0 || num > 255) {
                    return false;
                }
            }
            
            return true;
        }
        
        // Regular IP validation
        const parts = ip.split('.');
        if (parts.length !== 4) {
            return false;
        }
        
        for (const part of parts) {
            const num = parseInt(part);
            if (isNaN(num) || num < 0 || num > 255) {
                return false;
            }
        }
        
        return true;
    }
    
    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const sourceIpField = document.getElementById('source_ip');
            const destinationIpField = document.getElementById('destination_ip');
            
            let isValid = true;
            let errorMessage = '';
            
            if (sourceIpField && !validateIp(sourceIpField.value)) {
                isValid = false;
                errorMessage = 'Ungültige Quell-IP-Adresse. Verwenden Sie das Format xxx.xxx.xxx.xxx oder xxx.xxx.xxx.*';
                sourceIpField.classList.add('is-invalid');
            } else if (sourceIpField) {
                sourceIpField.classList.remove('is-invalid');
            }
            
            if (destinationIpField && !validateIp(destinationIpField.value)) {
                isValid = false;
                errorMessage = 'Ungültige Ziel-IP-Adresse. Verwenden Sie das Format xxx.xxx.xxx.xxx oder xxx.xxx.xxx.*';
                destinationIpField.classList.add('is-invalid');
            } else if (destinationIpField) {
                destinationIpField.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                alert(errorMessage);
            }
        });
    }
    
    // Rule highlighting
    const ruleRows = document.querySelectorAll('table tbody tr');
    ruleRows.forEach(row => {
        row.addEventListener('mouseover', function() {
            this.classList.add('bg-light');
        });
        
        row.addEventListener('mouseout', function() {
            this.classList.remove('bg-light');
        });
    });
    
    // Confirmation for rule deletion
    const deleteButtons = document.querySelectorAll('button[type="submit"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Sind Sie sicher, dass Sie diese Regel löschen möchten?')) {
                e.preventDefault();
            }
        });
    });
});
