const form = document.getElementById('password-form');
const aiChat = document.getElementById('ai-chat');
const aiAnimation = document.getElementById('ai-animation');

function showAIAnimation(show) {
    if (aiAnimation) aiAnimation.style.display = show ? 'inline-block' : 'none';
}

function addAIMessage(text, isAI = true) {
    const msg = document.createElement('div');
    msg.className = 'ai-message ' + (isAI ? 'ai-message-ai' : 'ai-message-user');
    msg.innerText = text;
    aiChat.appendChild(msg);
    aiChat.scrollTop = aiChat.scrollHeight;
}

function analyzeStrength(password) {
    if (!password) return '';
    let score = 0;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    if (score >= 5) return '🟢 Very Strong';
    if (score >= 4) return '🟡 Strong';
    if (score >= 3) return '🟠 Medium';
    return '🔴 Weak';
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    aiChat.innerHTML = '';
    addAIMessage('Generating your human-friendly password... Please wait!', false);
    showAIAnimation(true);
    const length = +form.length.value;
    const uppercase = form.uppercase.checked;
    const lowercase = form.lowercase.checked;
    const numbers = form.numbers.checked;
    const symbols = form.symbols.checked;
    try {
        const response = await fetch('/api/ai-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length, uppercase, lowercase, numbers, symbols })
        });
        const data = await response.json();
        let password = data.password;
        if (!password && data.raw_output) {
            const choices = data.raw_output.choices;
            if (choices && choices.length > 0) {
                password = choices[0].message.content.trim();
            }
        }
        showAIAnimation(false);
        addAIMessage('Here is your AI-generated password:', true);
        addAIMessage(password || 'AI did not return a password.', false);
        addAIMessage('Strength: ' + analyzeStrength(password), true);
        addAIMessage('Tip: Use a password manager to keep your passwords safe!', true);
    } catch (err) {
        showAIAnimation(false);
        addAIMessage('Error generating password. Please try again later.', true);
    }
});
