document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const startCamBtn = document.getElementById('startCamBtn');
    const checkInBtn = document.getElementById('checkInBtn');
    const registerBtn = document.getElementById('registerBtn');
    const statusMsg = document.getElementById('statusMsg');
    
    let stream = null;

    // Helper functions for UI
    function showMessage(msg, type='success') {
        statusMsg.textContent = msg;
        statusMsg.className = `status-msg show status-${type}`;
        setTimeout(() => {
            statusMsg.classList.remove('show');
        }, 5000);
    }

    function captureImage() {
        if (!stream) return null;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.8);
    }

    // Camera Init
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480, facingMode: "user" } 
            });
            video.srcObject = stream;
            startCamBtn.textContent = 'Camera Active';
            startCamBtn.disabled = true;
            checkInBtn.disabled = false;
            registerBtn.disabled = false;
            showMessage('Camera started successfully', 'success');
        } catch (err) {
            console.error("Error accessing camera:", err);
            showMessage('Failed to access camera. Please allow permissions.', 'error');
        }
    }

    startCamBtn.addEventListener('click', startCamera);

    // Register Handler
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const empId = document.getElementById('regEmpId').value;
        const name = document.getElementById('regName').value;
        const imageBase64 = captureImage();

        if (!imageBase64) {
            showMessage('Camera not active', 'error');
            return;
        }

        registerBtn.disabled = true;
        registerBtn.textContent = 'Processing...';

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ employee_id: empId, name: name, image: imageBase64 })
            });
            const data = await response.json();
            
            if (response.ok) {
                showMessage(`Success: ${data.message}`, 'success');
                document.getElementById('registerForm').reset();
            } else {
                showMessage(`Error: ${data.message}`, 'error');
            }
        } catch (err) {
            showMessage(`Network error: ${err.message}`, 'error');
        } finally {
            registerBtn.disabled = false;
            registerBtn.textContent = 'Capture Face & Register';
        }
    });

    // Check In Handler
    checkInBtn.addEventListener('click', async () => {
        const imageBase64 = captureImage();

        if (!imageBase64) {
            showMessage('Camera not active', 'error');
            return;
        }

        checkInBtn.disabled = true;
        checkInBtn.innerHTML = 'Analyzing Face...';

        try {
            const response = await fetch('/api/recognize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageBase64 })
            });
            const data = await response.json();
            
            if (response.ok || data.success) {
                showMessage(`Welcome ${data.name}! ${data.message}`, 'success');
            } else {
                showMessage(`Error: ${data.message}`, 'error');
            }
        } catch (err) {
            showMessage(`Network error: ${err.message}`, 'error');
        } finally {
            checkInBtn.disabled = false;
            checkInBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> Verify & Check In`;
        }
    });
});
