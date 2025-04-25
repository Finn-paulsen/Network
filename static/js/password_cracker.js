document.addEventListener('DOMContentLoaded', function() {
    // Elements for real-time analysis
    const targetTypeSelect = document.getElementById('target_type');
    const targetValueInput = document.getElementById('target_value');
    const charsetSelect = document.getElementById('character_set');
    const minLengthInput = document.getElementById('min_length');
    const maxLengthInput = document.getElementById('max_length');
    const startButton = document.getElementById('startButton');
    
    // Analysis result elements
    const charsetSizeElem = document.getElementById('charsetSize');
    const charsetSizeIndicator = document.getElementById('charsetSizeIndicator');
    const combinationsElem = document.getElementById('combinations');
    const combinationsIndicator = document.getElementById('combinationsIndicator');
    const crackTimeElem = document.getElementById('crackTime');
    const crackTimeIndicator = document.getElementById('crackTimeIndicator');
    const strengthIndicator = document.getElementById('strengthIndicator');
    const strengthText = document.getElementById('strengthText');
    
    // Simulation elements
    const simulationProgressBar = document.getElementById('simulationProgressBar');
    const progressLabel = document.getElementById('progressLabel');
    const passwordTriesElem = document.getElementById('passwordTries');
    const currentlyTestingElem = document.getElementById('currentlyTesting');
    const elapsedTimeElem = document.getElementById('elapsedTime');
    const simulationLog = document.getElementById('simulationLog');
    const liveResultsArea = document.getElementById('liveResultsArea');
    
    // Charset sizes by option
    const charsetSizes = {
        'numeric': 10,     // 0-9
        'alpha': 26,       // a-z
        'alphanumeric': 36, // a-z, 0-9
        'full': 94         // a-z, A-Z, 0-9, special chars
    };
    
    // Charset samples (for display only)
    const charsetSamples = {
        'numeric': '0123456789',
        'alpha': 'abcdefghijklmnopqrstuvwxyz',
        'alphanumeric': 'abcdefghijklmnopqrstuvwxyz0123456789',
        'full': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:\'",.<>/?`~'
    };
    
    // Add event listeners for real-time analysis
    [targetTypeSelect, targetValueInput, charsetSelect, minLengthInput, maxLengthInput].forEach(elem => {
        if (elem) elem.addEventListener('change', updateAnalysis);
    });
    
    if (targetValueInput) {
        targetValueInput.addEventListener('input', updateAnalysis);
    }
    
    // Initialize
    if (charsetSizeElem) updateAnalysis();
    
    // Show real-time password examples during simulation
    if (startButton) {
        startButton.addEventListener('click', function(e) {
            const form = document.getElementById('bruteForceForm');
            if (form && form.checkValidity()) {
                // If we're starting a simulation in the same page and not submitting the form
                if (liveResultsArea) {
                    e.preventDefault();
                    startSimulation();
                }
            }
        });
    }
    
    /**
     * Update the complexity analysis based on form inputs
     */
    function updateAnalysis() {
        if (!charsetSizeElem) return;
        
        // Get current values
        const charsetType = charsetSelect ? charsetSelect.value : 'alphanumeric';
        const charsetSize = charsetSizes[charsetType];
        const minLength = parseInt(minLengthInput ? minLengthInput.value : 1);
        const maxLength = parseInt(maxLengthInput ? maxLengthInput.value : 4);
        const targetValue = targetValueInput ? targetValueInput.value : '';
        
        // Update charset size display
        charsetSizeElem.textContent = charsetSize + ' Zeichen';
        charsetSizeIndicator.style.width = Math.min((charsetSize / 94) * 100, 100) + '%';
        
        // Calculate total combinations
        let totalCombinations = 0;
        for (let i = minLength; i <= maxLength; i++) {
            totalCombinations += Math.pow(charsetSize, i);
        }
        
        // Format combinations with thousands separators
        combinationsElem.textContent = totalCombinations.toLocaleString() + ' Kombinationen';
        
        // Calculate width for combinations indicator (log scale)
        const maxPossibleCombinations = Math.pow(94, 6); // Maximum value for full charset at length 6
        const logScale = (Math.log(totalCombinations) / Math.log(maxPossibleCombinations)) * 100;
        combinationsIndicator.style.width = Math.min(logScale, 100) + '%';
        
        // Estimate crack time (assuming 10,000 attempts per second for simulation)
        const attemptsPerSecond = 10000;
        const secondsToCrack = totalCombinations / attemptsPerSecond;
        
        // Format time in appropriate units
        let crackTimeText;
        if (secondsToCrack < 60) {
            crackTimeText = secondsToCrack.toFixed(2) + ' Sekunden';
        } else if (secondsToCrack < 3600) {
            crackTimeText = (secondsToCrack / 60).toFixed(2) + ' Minuten';
        } else if (secondsToCrack < 86400) {
            crackTimeText = (secondsToCrack / 3600).toFixed(2) + ' Stunden';
        } else if (secondsToCrack < 31536000) {
            crackTimeText = (secondsToCrack / 86400).toFixed(2) + ' Tage';
        } else {
            crackTimeText = (secondsToCrack / 31536000).toFixed(2) + ' Jahre';
        }
        
        crackTimeElem.textContent = crackTimeText;
        
        // Calculate width for crack time indicator (log scale)
        const maxSecondsToCrack = Math.pow(94, 6) / attemptsPerSecond; // Maximum crack time
        const logScaleTime = (Math.log(secondsToCrack) / Math.log(maxSecondsToCrack)) * 100;
        crackTimeIndicator.style.width = Math.min(logScaleTime, 100) + '%';
        
        // Update password strength if a target value is provided
        if (targetValue.length > 0) {
            // Simple strength calculation
            let strength = 0;
            
            // Length
            if (targetValue.length >= 8) strength += 1;
            if (targetValue.length >= 12) strength += 1;
            
            // Complexity
            if (/[a-z]/.test(targetValue) && /[A-Z]/.test(targetValue)) strength += 1;
            if (/\d/.test(targetValue)) strength += 1;
            if (/[^A-Za-z0-9]/.test(targetValue)) strength += 1;
            
            // Calculate percentage (out of 5)
            const strengthPercentage = (strength / 5) * 100;
            strengthIndicator.style.width = strengthPercentage + '%';
            
            // Set color based on strength
            let strengthColor, strengthDescription;
            if (strength < 2) {
                strengthColor = '#dc3545'; // Danger (red)
                strengthDescription = 'Sehr schwach';
            } else if (strength < 3) {
                strengthColor = '#ffc107'; // Warning (yellow)
                strengthDescription = 'Schwach';
            } else if (strength < 4) {
                strengthColor = '#0dcaf0'; // Info (blue)
                strengthDescription = 'Mittel';
            } else {
                strengthColor = '#198754'; // Success (green)
                strengthDescription = 'Stark';
            }
            
            strengthIndicator.style.backgroundColor = strengthColor;
            strengthText.textContent = strengthDescription;
            
            // Additional feedback
            const targetType = targetTypeSelect ? targetTypeSelect.value : 'password';
            if (targetType === 'password' && strength < 3) {
                strengthText.textContent += ' - Leicht zu knacken. Sollte verbessert werden.';
            } else if (targetType === 'password' && strength >= 4) {
                strengthText.textContent += ' - Gut! Diese Passwort ist sicher.';
            }
        } else {
            strengthIndicator.style.width = '0%';
            strengthText.textContent = 'Geben Sie einen Wert ein, um eine Analyse zu erhalten.';
        }
    }
    
    /**
     * Simulate a brute force attack in the browser
     */
    function startSimulation() {
        if (!liveResultsArea || !simulationProgressBar) return;
        
        liveResultsArea.style.display = 'block';
        document.getElementById('parameterCards').style.display = 'none';
        startButton.disabled = true;
        
        // Get simulation parameters
        const targetType = targetTypeSelect.value;
        const targetValue = targetValueInput.value;
        const charset = charsetSamples[charsetSelect.value]; 
        const minLength = parseInt(minLengthInput.value);
        const maxLength = parseInt(maxLengthInput.value);
        
        // Initialize simulation variables
        let found = false;
        let attempts = 0;
        let startTime = new Date().getTime();
        let estimatedAttempts = 0;
        let currentPassword = '';
        
        // Calculate total combinations
        let totalCombinations = 0;
        for (let i = minLength; i <= maxLength; i++) {
            totalCombinations += Math.pow(charset.length, i);
        }
        
        // Set up timer for real-time updates
        const updateInterval = setInterval(updateSimulationUI, 100);
        
        // Set up timer for generating random "attempts"
        const passwordGenInterval = setInterval(generateRandomPassword, 50);
        
        // Simulate finding the password after some time (between 3-8 seconds)
        const successTime = Math.floor(Math.random() * 5000) + 3000;
        setTimeout(() => {
            clearInterval(passwordGenInterval);
            found = true;
            // Generate a valid "cracked" password that looks like the target
            if (targetType === 'password') {
                currentPassword = targetValue;
            } else if (targetType === 'hash') {
                // For hashes, generate a random password that could have produced this hash
                currentPassword = generateRandomStringOfLength(charset, Math.min(8, maxLength));
            } else if (targetType === 'pin') {
                currentPassword = targetValue;
            }
            
            // Final update
            updateSimulationUI();
            
            // Add success animation
            const foundElement = document.getElementById('foundPassword');
            if (foundElement) {
                foundElement.textContent = currentPassword;
                foundElement.parentElement.classList.add('success-found');
            }
            
            // Generate final log entries
            const logElement = document.getElementById('simulationLog');
            if (logElement) {
                appendLogLine(logElement, `[Erfolg] Ziel geknackt nach ${attempts.toLocaleString()} Versuchen!`, 'success');
                appendLogLine(logElement, `[System] Gefundener Wert: ${currentPassword}`, 'muted');
                appendLogLine(logElement, `[System] Simulation abgeschlossen in ${((new Date().getTime() - startTime) / 1000).toFixed(2)} Sekunden.`, 'muted');
            }
            
            // Stop the simulation
            clearInterval(updateInterval);
            
            // Re-enable button
            startButton.disabled = false;
            startButton.textContent = 'Neue Simulation starten';
            
        }, successTime);
        
        /**
         * Generate a random password for display during simulation
         */
        function generateRandomPassword() {
            attempts += Math.floor(Math.random() * 500) + 100; // Random increment
            attempts = Math.min(attempts, totalCombinations);
            
            // Generate a random length between min and max
            const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
            currentPassword = generateRandomStringOfLength(charset, length);
        }
        
        /**
         * Update the UI elements during simulation
         */
        function updateSimulationUI() {
            // Update progress
            const progress = Math.min((attempts / totalCombinations) * 100, 100);
            simulationProgressBar.style.width = progress + '%';
            progressLabel.textContent = progress.toFixed(1) + '%';
            
            // Update current status
            passwordTriesElem.textContent = attempts.toLocaleString();
            currentlyTestingElem.textContent = currentPassword;
            
            // Update elapsed time
            const elapsedSeconds = (new Date().getTime() - startTime) / 1000;
            elapsedTimeElem.textContent = elapsedSeconds.toFixed(2) + ' s';
            
            // Add log entries periodically
            const logElement = document.getElementById('simulationLog');
            if (logElement && Math.random() < 0.1) { // 10% chance each update
                const progressPercent = Math.floor(progress);
                if (progressPercent % 5 === 0 && progressPercent > 0) {
                    appendLogLine(logElement, `[Fortschritt] ${progressPercent}% der möglichen Kombinationen überprüft...`, 'primary');
                }
                
                // Occasionally show the current password being tested
                if (Math.random() < 0.2) {
                    appendLogLine(logElement, `[Test] Versuche: ${currentPassword}`, 'warning');
                }
            }
        }
    }
    
    /**
     * Add a line to the simulation log with animation
     */
    function appendLogLine(logElement, text, styleClass) {
        const line = document.createElement('div');
        line.innerHTML = `<span class="text-${styleClass}">${text}</span>`;
        line.style.opacity = 0;
        line.classList.add('animate-in');
        logElement.appendChild(line);
        
        // Auto-scroll to bottom
        logElement.scrollTop = logElement.scrollHeight;
        
        // Make visible with animation
        setTimeout(() => {
            line.style.opacity = 1;
        }, 10);
    }
    
    /**
     * Generate a random string of a specified length using characters from charset
     */
    function generateRandomStringOfLength(charset, length) {
        let result = '';
        for (let i = 0; i < length; i++) {
            result += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        return result;
    }
});