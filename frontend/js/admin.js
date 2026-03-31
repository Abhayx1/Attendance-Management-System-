document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchAttendance();

    // Auto refresh every 30 seconds
    setInterval(() => {
        fetchStats();
        fetchAttendance();
    }, 30000);
});

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        if (data.success) {
            document.getElementById('statPresent').innerText = data.present_today;
            document.getElementById('statAbsent').innerText = data.absent_today;
            document.getElementById('statPercentage').innerText = data.attendance_percentage + '%';
            document.getElementById('statSpoof').innerText = data.spoof_attempts;
        }
    } catch (err) {
        console.error('Failed to fetch stats:', err);
    }
}

async function fetchAttendance() {
    try {
        const response = await fetch('/api/attendance');
        const data = await response.json();
        
        if (data.success) {
            const tbody = document.getElementById('attendanceTableBody');
            tbody.innerHTML = '';
            
            if (data.records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No records found.</td></tr>`;
                return;
            }

            data.records.forEach(r => {
                const tr = document.createElement('tr');
                const badgeClass = r.status.toLowerCase() === 'absent' ? 'badge-absent' : 'badge-present';
                tr.innerHTML = `
                    <td>${r.date}</td>
                    <td>${r.time}</td>
                    <td style="font-family: monospace;">${r.employee_id}</td>
                    <td><strong>${r.name}</strong></td>
                    <td><span class="badge ${badgeClass}">${r.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error('Failed to fetch attendance:', err);
    }
}
