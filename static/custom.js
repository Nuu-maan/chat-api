window.onload = function() {
    // Add custom initialization code here
    const ui = document.getElementsByClassName('swagger-ui')[0];
    if (ui) {
        // Add dark mode class
        ui.classList.add('dark-mode');
        
        // Add custom event listeners
        ui.addEventListener('click', function(e) {
            // Handle expand/collapse all
            if (e.target.classList.contains('expand-operation')) {
                const operations = document.querySelectorAll('.opblock');
                operations.forEach(op => op.classList.add('is-open'));
            }
            if (e.target.classList.contains('collapse-operation')) {
                const operations = document.querySelectorAll('.opblock');
                operations.forEach(op => op.classList.remove('is-open'));
            }
        });

        // Add expand/collapse buttons
        const info = document.querySelector('.info');
        if (info) {
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'expand-collapse-container';
            buttonContainer.style.marginBottom = '1rem';

            const expandButton = document.createElement('button');
            expandButton.className = 'expand-operation';
            expandButton.innerText = 'Expand All';
            expandButton.style.marginRight = '1rem';

            const collapseButton = document.createElement('button');
            collapseButton.className = 'collapse-operation';
            collapseButton.innerText = 'Collapse All';

            buttonContainer.appendChild(expandButton);
            buttonContainer.appendChild(collapseButton);
            info.appendChild(buttonContainer);
        }
    }

    // Add custom keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + E to expand all
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            const operations = document.querySelectorAll('.opblock');
            operations.forEach(op => op.classList.add('is-open'));
        }
        // Ctrl/Cmd + C to collapse all
        if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
            e.preventDefault();
            const operations = document.querySelectorAll('.opblock');
            operations.forEach(op => op.classList.remove('is-open'));
        }
    });
}; 