/**
 * How to Play Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Staggered entry for sections
    const sections = document.querySelectorAll('.instruction-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = `all 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${0.2 + index * 0.15}s`;
        
        // Trigger reflow then set to final state
        requestAnimationFrame(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        });
    });

    // Hover effect for method cards
    const cards = document.querySelectorAll('.method-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const icon = card.querySelector('.method-icon');
            if (icon) {
                icon.style.transform = 'scale(1.2) rotate(5deg)';
                icon.style.transition = 'transform 0.3s ease';
            }
        });

        card.addEventListener('mouseleave', () => {
            const icon = card.querySelector('.method-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });
});
