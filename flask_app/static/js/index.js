document.addEventListener('DOMContentLoaded', function() {
    const leaderboardModal = document.getElementById('leaderboard');
    const instructionsModal = document.getElementById('instructions');
    
    const leaderboardBtn = document.getElementById('leaderboardBtn');
    const instructionsBtn = document.getElementById('instructionsBtn');
    
    const closeButtons = document.querySelectorAll('.close');
    
    leaderboardBtn.addEventListener('click', function() {
        loadLeaderboard();
        leaderboardModal.style.display = 'block';
    });
    
    instructionsBtn.addEventListener('click', function() {
        instructionsModal.style.display = 'block';
    });
    
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            leaderboardModal.style.display = 'none';
            instructionsModal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === leaderboardModal) {
            leaderboardModal.style.display = 'none';
        }
        if (event.target === instructionsModal) {
            instructionsModal.style.display = 'none';
        }
    });
    
    function loadLeaderboard() {
        fetch('/api/leaderboard')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector('#leaderboardTable tbody');
                tableBody.innerHTML = '';
                
                if (data.length === 0) {
                    const row = document.createElement('tr');
                    row.innerHTML = '<td colspan="4">No scores yet. Be the first!</td>';
                    tableBody.appendChild(row);
                } else {
                    data.forEach((entry, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${index + 1}</td>
                            <td>${entry.name}</td>
                            <td>${entry.score}</td>
                            <td>${entry.date}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading leaderboard:', error);
                const tableBody = document.querySelector('#leaderboardTable tbody');
                tableBody.innerHTML = '<tr><td colspan="4">Error loading leaderboard</td></tr>';
            });
    }
});
