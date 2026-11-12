/**
 * Factory Shop-Floor Execution System Main Script
 */

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // Confirmation on downtime resume
    const resumeForms = document.querySelectorAll("form.resume-form");
    resumeForms.forEach(form => {
        form.addEventListener("submit", (e) => {
            const confirmed = confirm("Are you sure you want to mark this machine as RESUMED? This will close the downtime log.");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
