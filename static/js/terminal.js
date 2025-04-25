document.addEventListener('DOMContentLoaded', function() {
    // Focus the terminal input when the page loads
    const terminalInput = document.querySelector('.terminal-input');
    if (terminalInput) {
        terminalInput.focus();
    }
    
    // Command history functionality
    const commandHistory = [];
    let historyIndex = -1;
    
    // Store current input before navigating history
    let currentInput = '';
    
    if (terminalInput) {
        // Handle up/down arrows for command history
        terminalInput.addEventListener('keydown', function(e) {
            // Up arrow
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                
                // Save current input when starting to navigate history
                if (historyIndex === -1) {
                    currentInput = terminalInput.value;
                }
                
                if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    terminalInput.value = commandHistory[historyIndex];
                }
            } 
            // Down arrow
            else if (e.key === 'ArrowDown') {
                e.preventDefault();
                
                if (historyIndex > 0) {
                    historyIndex--;
                    terminalInput.value = commandHistory[historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    terminalInput.value = currentInput;
                }
            }
            // Tab completion (basic version)
            else if (e.key === 'Tab') {
                e.preventDefault();
                
                const commands = ['ping', 'traceroute', 'nslookup', 'dig', 'host', 'whois', 'ifconfig', 'ipconfig', 'netstat'];
                const currentCommand = terminalInput.value.trim();
                
                // Only auto-complete if we're at the beginning of a command
                if (!currentCommand.includes(' ')) {
                    const matchingCommands = commands.filter(cmd => cmd.startsWith(currentCommand));
                    
                    if (matchingCommands.length === 1) {
                        // If only one match, complete it
                        terminalInput.value = matchingCommands[0] + ' ';
                    } else if (matchingCommands.length > 1) {
                        // Show available options in terminal output
                        const output = document.getElementById('terminalOutput');
                        if (output) {
                            const suggestions = document.createElement('pre');
                            suggestions.classList.add('terminal-text');
                            suggestions.textContent = matchingCommands.join('  ');
                            output.appendChild(suggestions);
                            
                            // Scroll to bottom
                            output.scrollTop = output.scrollHeight;
                        }
                    }
                }
            }
        });
        
        // Handle form submission to update history
        const terminalForm = document.getElementById('terminalForm');
        if (terminalForm) {
            terminalForm.addEventListener('submit', function() {
                const command = terminalInput.value.trim();
                if (command) {
                    // Add to beginning of history array
                    commandHistory.unshift(command);
                    
                    // Limit history size
                    if (commandHistory.length > 20) {
                        commandHistory.pop();
                    }
                    
                    // Reset index
                    historyIndex = -1;
                }
            });
        }
    }
    
    // Syntax highlighting in terminal output (basic)
    const terminalOutput = document.getElementById('terminalOutput');
    if (terminalOutput) {
        // Make sure pre elements have proper styling
        const preElements = terminalOutput.querySelectorAll('pre');
        preElements.forEach(pre => {
            // Add highlighting for IP addresses
            pre.innerHTML = pre.innerHTML.replace(
                /\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/g, 
                '<span class="text-info">$&</span>'
            );
            
            // Add highlighting for success messages
            pre.innerHTML = pre.innerHTML.replace(
                /\b(?:success|successful|ok|up|online)\b/gi, 
                '<span class="text-success">$&</span>'
            );
            
            // Add highlighting for error messages
            pre.innerHTML = pre.innerHTML.replace(
                /\b(?:error|failed|timeout|unreachable|offline|down)\b/gi, 
                '<span class="text-danger">$&</span>'
            );
        });
        
        // Scroll to bottom
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
});
