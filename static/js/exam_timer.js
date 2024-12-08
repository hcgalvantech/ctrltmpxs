// static/js/exam_timer.js
class ExamTimer {
    constructor(totalMinutes) {
        this.totalSeconds = totalMinutes * 60;
        this.remainingSeconds = this.totalSeconds;
        this.timerInterval = null;
        this.onTimerEnd = null;
    }

    start(displayElement, onTimerEnd) {
        this.onTimerEnd = onTimerEnd;
        this.timerInterval = setInterval(() => {
            this.remainingSeconds--;
            this.updateDisplay(displayElement);

            if (this.remainingSeconds <= 0) {
                this.stop();
                if (this.onTimerEnd) this.onTimerEnd();
            }
        }, 1000);
    }

    stop() {
        clearInterval(this.timerInterval);
    }

    updateDisplay(displayElement) {
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        displayElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Ejemplo de uso en el examen
document.addEventListener('DOMContentLoaded', () => {
    const timerDisplay = document.getElementById('timer');
    const projectLinkInput = document.getElementById('project-link');
    const submitButton = document.getElementById('submit-exam');

    const timer = new ExamTimer(120); // 2 horas
    timer.start(timerDisplay, () => {
        projectLinkInput.disabled = true;
        submitButton.disabled = true;
        alert('Tiempo de examen terminado');
    });
});