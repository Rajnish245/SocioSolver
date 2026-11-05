// SocioSolve Client-side Interactions

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. AJAX Upvoting on Solution Proposals
    document.querySelectorAll('.btn-upvote').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const proposalId = this.dataset.proposalId;
            const voteUrl = this.dataset.voteUrl;
            const countSpan = this.querySelector('.vote-count');
            const icon = this.querySelector('i');

            if (!voteUrl) return;

            fetch(voteUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return null;
                }
                return res.json();
            })
            .then(data => {
                if (data) {
                    if (countSpan) countSpan.textContent = data.upvotes_count;
                    if (data.voted) {
                        this.classList.add('active', 'btn-primary');
                        this.classList.remove('btn-outline-primary');
                    } else {
                        this.classList.remove('active', 'btn-primary');
                        this.classList.add('btn-outline-primary');
                    }
                }
            })
            .catch(err => console.error('Vote error:', err));
        });
    });

    // 3. Demo Account Quick-Fill on Login Page
    document.querySelectorAll('.demo-login-fill').forEach(btn => {
        btn.addEventListener('click', function () {
            const user = this.dataset.user;
            const pass = this.dataset.pass || 'SocioSolve2026!';
            const userInput = document.querySelector('input[name="username"]');
            const passInput = document.querySelector('input[name="password"]');
            if (userInput && passInput) {
                userInput.value = user;
                passInput.value = pass;
            }
        });
    });
});
