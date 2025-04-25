document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const hostDetailsModal = new bootstrap.Modal(document.getElementById('hostDetailsModal'));
    const actionMenuModal = new bootstrap.Modal(document.getElementById('actionMenuModal'));
    const viewDetailsBtns = document.querySelectorAll('.view-details-btn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const hostDetailsContent = document.getElementById('hostDetailsContent');
    
    // Host details elements
    const detailIp = document.getElementById('detailIp');
    const detailHostname = document.getElementById('detailHostname');
    const detailOs = document.getElementById('detailOs');
    const detailPorts = document.getElementById('detailPorts');
    
    // Action buttons
    const actionPing = document.querySelector('.action-ping');
    const actionTraceroute = document.querySelector('.action-traceroute');
    const actionNmap = document.querySelector('.action-nmap');
    const actionAddFirewall = document.querySelector('.action-add-firewall');
    const actionBruteForce = document.querySelector('.action-brute-force');
    const actionExploitScan = document.querySelector('.action-exploit-scan');

    // Current selected IP
    let currentIp = '';
    let scanProgress = 0;
    let scanTimer = null;
    
    // Event delegation for view details buttons
    document.getElementById('scanResultsContainer').addEventListener('click', function(e) {
        const viewDetailsBtn = e.target.closest('.view-details-btn');
        if (viewDetailsBtn) {
            const ip = viewDetailsBtn.dataset.ip;
            showHostDetails(ip);
        }

        // Quick-action button
        const quickActionBtn = e.target.closest('.quick-action-btn');
        if (quickActionBtn) {
            const ip = quickActionBtn.dataset.ip;
            showQuickActionMenu(ip, quickActionBtn);
        }
    });
    
    // Double-click on host row
    document.getElementById('scanResultsContainer').addEventListener('dblclick', function(e) {
        const hostRow = e.target.closest('.host-row');
        if (hostRow) {
            const ip = hostRow.dataset.ip;
            showHostDetails(ip);
        }
    });
    
    // Progress bar animation for scan
    function updateProgressBar() {
        const progressBar = document.getElementById('scanProgressBar');
        const progressContainer = document.getElementById('scanProgressContainer');
        
        if (progressBar && progressContainer) {
            scanProgress += Math.random() * 15;
            if (scanProgress >= 100) {
                scanProgress = 100;
                clearInterval(scanTimer);
                
                // Small delay before hiding progress
                setTimeout(() => {
                    progressContainer.classList.add('d-none');
                    document.getElementById('scanResultsSection').classList.remove('d-none');
                }, 500);
            }
            
            progressBar.style.width = scanProgress + '%';
            progressBar.setAttribute('aria-valuenow', scanProgress);
            
            // Update scan status message
            const scanStatusMsg = document.getElementById('scanStatusMessage');
            if (scanStatusMsg) {
                if (scanProgress < 25) {
                    scanStatusMsg.textContent = 'Initialisiere Scan...';
                } else if (scanProgress < 50) {
                    scanStatusMsg.textContent = 'Sende Scan-Pakete...';
                } else if (scanProgress < 75) {
                    scanStatusMsg.textContent = 'Analysiere Antworten...';
                } else {
                    scanStatusMsg.textContent = 'Scan wird abgeschlossen...';
                }
            }
        }
    }
    
    // Initialize scan process if there's a form submission
    const scanForm = document.getElementById('scanForm');
    if (scanForm) {
        scanForm.addEventListener('submit', function(e) {
            // Don't actually prevent the default - we want the form to submit
            // but we'll show a progress animation while it's processing
            
            const scanProgressContainer = document.getElementById('scanProgressContainer');
            const scanResultsSection = document.getElementById('scanResultsSection');
            
            if (scanProgressContainer && scanResultsSection) {
                scanProgressContainer.classList.remove('d-none');
                scanResultsSection.classList.add('d-none');
                
                // Reset progress
                scanProgress = 0;
                document.getElementById('scanProgressBar').style.width = '0%';
                document.getElementById('scanProgressBar').setAttribute('aria-valuenow', 0);
                
                // Start progress animation
                scanTimer = setInterval(updateProgressBar, 200);
            }
        });
    }
    
    // Function to show quick action menu
    function showQuickActionMenu(ip, buttonElement) {
        currentIp = ip;
        
        // Update modal content
        document.getElementById('actionMenuIp').textContent = ip;
        
        // Position the modal near the button if possible
        const rect = buttonElement.getBoundingClientRect();
        const modal = document.getElementById('actionMenuModal');
        
        // Show the modal
        actionMenuModal.show();
    }
    
    // Function to show host details
    function showHostDetails(ip) {
        currentIp = ip;
        
        // Reset and show loading state
        hostDetailsContent.style.display = 'none';
        loadingSpinner.style.display = 'block';
        
        // Show the modal
        hostDetailsModal.show();
        
        // Update modal title
        document.getElementById('hostDetailsModalLabel').textContent = `Host Details: ${ip}`;
        
        // Simulate scan progress for more realistic feel
        let detailProgress = 0;
        const detailProgressBar = document.getElementById('detailProgressBar');
        const detailProgressInterval = setInterval(() => {
            detailProgress += 5;
            if (detailProgressBar) {
                detailProgressBar.style.width = `${detailProgress}%`;
            }
            if (detailProgress >= 100) {
                clearInterval(detailProgressInterval);
            }
        }, 50);
        
        // Fetch host details
        fetch(`/api/host_details/${ip}`)
            .then(response => response.json())
            .then(data => {
                // Simulate a short delay for the loading effect
                setTimeout(() => {
                    // Update details
                    detailIp.textContent = data.ip;
                    detailHostname.textContent = data.hostname;
                    detailOs.textContent = data.os_guess;
                    
                    // Update ports table
                    detailPorts.innerHTML = '';
                    if (data.ports && data.ports.length > 0) {
                        data.ports.forEach(port => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${port.port}</td>
                                <td>${port.service}</td>
                                <td>
                                    <span class="badge bg-${port.status === 'open' ? 'success' : 'danger'}">
                                        ${port.status}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary port-action-btn" 
                                            data-port="${port.port}" data-service="${port.service}">
                                        <i class="fas fa-ellipsis-h"></i>
                                    </button>
                                </td>
                            `;
                            detailPorts.appendChild(row);
                        });
                        
                        // Add event listeners to port action buttons
                        document.querySelectorAll('.port-action-btn').forEach(btn => {
                            btn.addEventListener('click', function() {
                                const port = this.dataset.port;
                                const service = this.dataset.service;
                                showPortActionMenu(currentIp, port, service, this);
                            });
                        });
                    } else {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td colspan="4" class="text-center">
                                Keine offenen Ports gefunden
                            </td>
                        `;
                        detailPorts.appendChild(row);
                    }
                    
                    // Set action button event handlers
                    actionPing.onclick = () => {
                        hostDetailsModal.hide();
                        redirectToTerminal(`ping -c 4 ${currentIp}`);
                    };
                    
                    actionTraceroute.onclick = () => {
                        hostDetailsModal.hide();
                        redirectToTerminal(`traceroute ${currentIp}`);
                    };
                    
                    actionNmap.onclick = () => {
                        hostDetailsModal.hide();
                        redirectToTerminal(`nmap ${currentIp}`);
                    };
                    
                    actionAddFirewall.onclick = () => {
                        hostDetailsModal.hide();
                        redirectToFirewall(currentIp);
                    };

                    if (actionBruteForce) {
                        actionBruteForce.onclick = () => {
                            hostDetailsModal.hide();
                            redirectToBruteForce(currentIp);
                        };
                    }

                    if (actionExploitScan) {
                        actionExploitScan.onclick = () => {
                            hostDetailsModal.hide();
                            redirectToExploitScanner(currentIp);
                        };
                    }
                    
                    // Hide loading, show content
                    loadingSpinner.style.display = 'none';
                    hostDetailsContent.style.display = 'block';
                }, 800); // Artificial delay for better UX
            })
            .catch(error => {
                console.error('Error fetching host details:', error);
                setTimeout(() => {
                    loadingSpinner.style.display = 'none';
                    hostDetailsContent.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            Fehler beim Laden der Host-Details: ${error.message}
                        </div>
                    `;
                    hostDetailsContent.style.display = 'block';
                }, 500);
            });
    }
    
    // Function to show port action menu
    function showPortActionMenu(ip, port, service, buttonElement) {
        // Create and show a popover or custom dropdown menu
        const popover = bootstrap.Popover.getInstance(buttonElement);
        
        if (popover) {
            popover.dispose();
        }
        
        const actions = [];
        
        // Add different actions based on service
        if (service === 'HTTP' || service === 'HTTPS') {
            actions.push({
                icon: 'fas fa-globe',
                text: 'Web-Seite öffnen',
                action: () => {
                    const protocol = service === 'HTTPS' ? 'https' : 'http';
                    window.open(`${protocol}://${ip}:${port}`, '_blank');
                }
            });
        }
        
        if (service === 'SSH') {
            actions.push({
                icon: 'fas fa-terminal',
                text: 'SSH-Befehl',
                action: () => {
                    redirectToTerminal(`echo "ssh user@${ip} -p ${port}" && echo "Simulated SSH connection (education only)"`);
                }
            });
        }
        
        if (service === 'FTP') {
            actions.push({
                icon: 'fas fa-exchange-alt',
                text: 'FTP-Befehl',
                action: () => {
                    redirectToTerminal(`echo "ftp ${ip} ${port}" && echo "Simulated FTP connection (education only)"`);
                }
            });
        }
        
        // Add generic actions for any port
        actions.push({
            icon: 'fas fa-search',
            text: 'Port scannen',
            action: () => {
                redirectToTerminal(`nmap -p ${port} ${ip}`);
            }
        });
        
        actions.push({
            icon: 'fas fa-fire',
            text: 'Firewall-Regel',
            action: () => {
                redirectToFirewall(ip);
            }
        });
        
        // Create the popover content
        let content = '<div class="port-actions-menu">';
        actions.forEach(action => {
            content += `<div class="port-action-item" data-action="${action.text.replaceAll(' ', '-')}">
                <i class="${action.icon} me-2"></i> ${action.text}
            </div>`;
        });
        content += '</div>';
        
        // Initialize a new popover
        new bootstrap.Popover(buttonElement, {
            html: true,
            content: content,
            trigger: 'focus',
            placement: 'left'
        });
        
        // Show the popover
        buttonElement.focus();
        
        // Add event listeners to the popover items once it's shown
        buttonElement.addEventListener('inserted.bs.popover', function () {
            document.querySelectorAll('.port-action-item').forEach((item, index) => {
                item.addEventListener('click', function() {
                    // Close the popover
                    bootstrap.Popover.getInstance(buttonElement).hide();
                    // Execute the action
                    actions[index].action();
                });
            });
        });
    }
    
    // Function to redirect to terminal with command
    function redirectToTerminal(command) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/terminal';
        
        // Add CSRF token (this would need to be retrieved from the page)
        const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfTokenMeta) {
            const csrfToken = document.createElement('input');
            csrfToken.type = 'hidden';
            csrfToken.name = 'csrf_token';
            csrfToken.value = csrfTokenMeta.content;
            form.appendChild(csrfToken);
        }
        
        // Add command input
        const commandInput = document.createElement('input');
        commandInput.type = 'hidden';
        commandInput.name = 'command';
        commandInput.value = command;
        form.appendChild(commandInput);
        
        // Submit form
        document.body.appendChild(form);
        form.submit();
    }
    
    // Function to redirect to firewall with IP pre-filled
    function redirectToFirewall(ip) {
        window.location.href = `/firewall?source_ip=${ip}`;
    }

    // Function to redirect to brute force with IP pre-filled
    function redirectToBruteForce(ip) {
        window.location.href = `/brute-force?target=${ip}`;
    }

    // Function to redirect to exploit scanner with URL pre-filled
    function redirectToExploitScanner(ip) {
        window.location.href = `/exploit-scanner?target=${ip}`;
    }
    
    // Initialize all action buttons in the quick action menu modal
    document.querySelectorAll('.modal-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            
            switch(action) {
                case 'ping':
                    actionMenuModal.hide();
                    redirectToTerminal(`ping -c 4 ${currentIp}`);
                    break;
                case 'traceroute':
                    actionMenuModal.hide();
                    redirectToTerminal(`traceroute ${currentIp}`);
                    break;
                case 'nmap':
                    actionMenuModal.hide();
                    redirectToTerminal(`nmap ${currentIp}`);
                    break;
                case 'whois':
                    actionMenuModal.hide();
                    redirectToTerminal(`whois ${currentIp}`);
                    break;
                case 'firewall':
                    actionMenuModal.hide();
                    redirectToFirewall(currentIp);
                    break;
                case 'brute-force':
                    actionMenuModal.hide();
                    redirectToBruteForce(currentIp);
                    break;
                case 'exploit-scan':
                    actionMenuModal.hide();
                    redirectToExploitScanner(currentIp);
                    break;
                case 'details':
                    actionMenuModal.hide();
                    showHostDetails(currentIp);
                    break;
            }
        });
    });
});
