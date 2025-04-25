document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const hostDetailsModal = new bootstrap.Modal(document.getElementById('hostDetailsModal'));
    const viewDetailsBtns = document.querySelectorAll('.view-details-btn');
    const hostRows = document.querySelectorAll('.host-row');
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
    const actionAddFirewall = document.querySelector('.action-add-firewall');

    // Current selected IP
    let currentIp = '';
    
    // Event delegation for view details buttons
    document.getElementById('scanResultsContainer').addEventListener('click', function(e) {
        const viewDetailsBtn = e.target.closest('.view-details-btn');
        if (viewDetailsBtn) {
            const ip = viewDetailsBtn.dataset.ip;
            showHostDetails(ip);
        }
    });
    
    // Double-click on host row
    hostRows.forEach(row => {
        row.addEventListener('dblclick', function() {
            const ip = this.dataset.ip;
            showHostDetails(ip);
        });
    });
    
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
        
        // Fetch host details
        fetch(`/api/host_details/${ip}`)
            .then(response => response.json())
            .then(data => {
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
                        `;
                        detailPorts.appendChild(row);
                    });
                } else {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td colspan="3" class="text-center">
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
                
                actionAddFirewall.onclick = () => {
                    hostDetailsModal.hide();
                    redirectToFirewall(currentIp);
                };
                
                // Hide loading, show content
                loadingSpinner.style.display = 'none';
                hostDetailsContent.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching host details:', error);
                loadingSpinner.style.display = 'none';
                hostDetailsContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Fehler beim Laden der Host-Details: ${error.message}
                    </div>
                `;
                hostDetailsContent.style.display = 'block';
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
});
