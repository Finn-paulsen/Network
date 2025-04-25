document.addEventListener('DOMContentLoaded', function() {
    // Get the canvas element
    const canvas = document.getElementById('matrixCanvas');
    if (!canvas) return;
    
    // Set canvas size to match window
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Get the canvas context
    const ctx = canvas.getContext('2d');
    
    // Characters to use in the rain
    const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    // Font size and columns
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    
    // Array to store the y position of each drop
    const drops = [];
    for (let i = 0; i < columns; i++) {
        // Initially random position
        drops[i] = Math.floor(Math.random() * -canvas.height);
    }
    
    // Setting the color and font of text
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.font = fontSize + 'px monospace';
    
    // Counter for stopping the animation after a certain time
    let counter = 0;
    const maxIterations = 600; // Roughly 10 seconds at 60fps
    
    // Array to track when a column should stop
    const columnActive = Array(columns).fill(true);
    
    // Draw function
    function draw() {
        // Add semi-transparent black rectangle on top of previous frame
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Set text color
        ctx.fillStyle = '#0f0'; // Green text
        
        // Loop through each drop
        for (let i = 0; i < drops.length; i++) {
            // Skip if this column is no longer active
            if (!columnActive[i]) continue;
            
            // Choose a random character
            const text = chars[Math.floor(Math.random() * chars.length)];
            
            // Draw the character
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Lower opacity for characters closer to the end of the stream
            if (drops[i] > 5) {
                const opacity = Math.max(0, 1 - (drops[i] / 50));
                ctx.fillStyle = `rgba(0, 255, 0, ${opacity})`;
            } else {
                // Brighter color for the leading character
                ctx.fillStyle = 'rgba(0, 255, 0, 0.95)';
            }
            
            // Randomly reset some drops
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            // Move the drop down
            drops[i]++;
        }
        
        // Increment counter
        counter++;
        
        // Gradually fade out columns as we approach max iterations
        if (counter > maxIterations * 0.7) {
            const fadeRate = 0.02; // Speed of column deactivation
            for (let i = 0; i < columns; i++) {
                if (Math.random() < fadeRate && columnActive[i]) {
                    columnActive[i] = false;
                }
            }
        }
        
        // Continue animation until max iterations or all columns inactive
        if (counter < maxIterations && columnActive.some(Boolean)) {
            requestAnimationFrame(draw);
        } else {
            // Fade out the canvas when done
            fadeOutCanvas();
        }
    }
    
    // Function to fade out the canvas
    function fadeOutCanvas() {
        let opacity = 1.0;
        
        function fade() {
            opacity -= 0.05;
            
            if (opacity <= 0) {
                canvas.style.opacity = 0;
                setTimeout(() => {
                    // Hide canvas completely when done
                    canvas.style.display = 'none';
                    
                    // Fade in login form
                    const loginCard = document.querySelector('.login-card');
                    if (loginCard) {
                        loginCard.style.opacity = 0;
                        loginCard.style.display = 'block';
                        
                        let formOpacity = 0;
                        const formFade = setInterval(() => {
                            formOpacity += 0.1;
                            loginCard.style.opacity = formOpacity;
                            
                            if (formOpacity >= 1) {
                                clearInterval(formFade);
                            }
                        }, 50);
                    }
                }, 300);
                return;
            }
            
            canvas.style.opacity = opacity;
            requestAnimationFrame(fade);
        }
        
        fade();
    }
    
    // Start animation
    draw();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        // Resize canvas
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Recalculate columns
        const newColumns = Math.floor(canvas.width / fontSize);
        
        // Update drops array
        while (drops.length < newColumns) {
            drops.push(Math.floor(Math.random() * canvas.height));
            columnActive.push(true);
        }
        
        // Update font
        ctx.font = fontSize + 'px monospace';
    });
});