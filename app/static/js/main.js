console.log("CONST loaded ✅");

// ── Password strength indicator ──────────────────────────────────────────
const passwordInput = document.getElementById('password');
const strengthFill  = document.getElementById('strength-fill');
const strengthLabel = document.getElementById('strength-label');

if (passwordInput) {
    passwordInput.addEventListener('input', () => {
        const val = passwordInput.value;
        let score = 0;

        if (val.length >= 8)                        score++;
        if (/[A-Z]/.test(val))                      score++;
        if (/\d/.test(val))                         score++;
        if (/[!@#$%^&*(),.?\":{}|<>]/.test(val))   score++;

        const levels = [
            { label: '',          color: 'transparent', width: '0%'   },
            { label: 'Weak',      color: '#ff4d4d',     width: '25%'  },
            { label: 'Fair',      color: '#ffaa00',     width: '50%'  },
            { label: 'Good',      color: '#88cc00',     width: '75%'  },
            { label: 'Strong ✓',  color: '#e8ff47',     width: '100%' },
        ];

        const level = levels[score];
        if (strengthFill)  { strengthFill.style.width = level.width; strengthFill.style.background = level.color; }
        if (strengthLabel) { strengthLabel.textContent = level.label; strengthLabel.style.color = level.color; }
    });
}

// ── Auto-dismiss flash messages ──────────────────────────────────────────
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.transition = 'opacity 0.5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 3000);
