document.addEventListener('DOMContentLoaded', function() {
    const userElement = document.querySelector('.user_role');
    if (userElement) { 
        const userRole = userElement.getAttribute('data-role').trim();
        const roleStyles = {
            admin: 'color: #f39c12;',
            user: 'color: #3498db;'
        };
        if (roleStyles[userRole]) {
            userElement.style = roleStyles[userRole];
        }
    }
});