// static/js/exam_timer.js
class ExamTimer {
    constructor(examTimeLimit) {
        // Use the passed exam time limit directly
        this.totalMinutes = examTimeLimit;
        this.timerInterval = null;
        this.onTimerEnd = null;
    }

    start(displayElement, onTimerEnd) {
        // Check if exam has already started
        const examStartTime = localStorage.getItem('examStartTime');
        const examEndTime = localStorage.getItem('examEndTime');
        const examTimeLimit = localStorage.getItem('examTimeLimit');

        // Ensure we have a valid time limit
        if (!this.totalMinutes) {
            console.error('No exam time limit specified');
            onTimerEnd();
            return;
        }

        if (examStartTime && examEndTime && examTimeLimit) {
            const currentTime = Date.now();
            const remainingTime = parseInt(examEndTime) - currentTime;
            const originalTimeLimit = parseInt(examTimeLimit);

            if (remainingTime > 0 && originalTimeLimit === this.totalMinutes) {
                // Resume existing timer
                this.remainingSeconds = Math.floor(remainingTime / 1000);
            } else {
                // Exam time has expired or time limit changed
                this.remainingSeconds = 0;
                onTimerEnd();
                return;
            }
        } else {
            // First time starting the exam
            this.remainingSeconds = this.totalMinutes * 60;
            localStorage.setItem('examStartTime', Date.now());
            localStorage.setItem('examEndTime', Date.now() + (this.totalMinutes * 60 * 1000));
            localStorage.setItem('examTimeLimit', this.totalMinutes);
        }

        this.onTimerEnd = onTimerEnd;
        this.timerInterval = setInterval(() => {
            this.remainingSeconds--;
            this.updateDisplay(displayElement);

            if (this.remainingSeconds <= 0) {
                this.stop();
                this.clearTimerStorage();
                if (this.onTimerEnd) this.onTimerEnd();
            }
        }, 1000);
    }

    stop() {
        clearInterval(this.timerInterval);
    }

    clearTimerStorage() {
        localStorage.removeItem('examStartTime');
        localStorage.removeItem('examEndTime');
        localStorage.removeItem('examTimeLimit');
    }

    updateDisplay(displayElement) {
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        displayElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Exam page initialization
document.addEventListener('DOMContentLoaded', () => {
    const timerDisplay = document.getElementById('timer');
    const projectLinkInput = document.getElementById('project-link');
    const submitButton = document.getElementById('submit-exam');

    // Retrieve exam info from localStorage
    const examInfo = JSON.parse(localStorage.getItem('examInfo') || '{}');
    const examTimeLimit = examInfo.exam_time_limit || 120; // Default to 2 hours if not specified

    const timer = new ExamTimer(examTimeLimit);
    timer.start(timerDisplay, () => {
        projectLinkInput.disabled = true;
        submitButton.disabled = true;
        alert('Tiempo de examen terminado');
    });

    // Prevent accidental page reload
    window.addEventListener('beforeunload', (e) => {
        // Only show warning if exam is in progress
        if (localStorage.getItem('examStartTime')) {
            e.preventDefault(); // Show browser's default warning
            e.returnValue = ''; // Required for some browsers
        }
    });
});