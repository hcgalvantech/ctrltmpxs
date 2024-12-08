// static/js/exam.js
document.addEventListener('DOMContentLoaded', () => {
    const examSubmissionForm = document.getElementById('exam-submission-form');
    const timerDisplay = document.getElementById('timer');
    const githubLinkInput = document.getElementById('github-link');
    const submitExamButton = document.getElementById('submit-exam');

    // Validate GitHub link
    function validateGithubLink(link) {
        const githubRegex = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w-]+\/?$/;
        return githubRegex.test(link);
    }

    // Create exam timer
    const examInfo = JSON.parse(localStorage.getItem('examInfo'));
    const examTimeLimit = examInfo ? examInfo.exam_time_limit : 120; // Default 2 hours

    class ExamTimer {
        constructor(totalMinutes) {
            this.totalSeconds = totalMinutes * 60;
            this.remainingSeconds = this.totalSeconds;
            this.timerInterval = null;
        }

        start() {
            this.timerInterval = setInterval(() => {
                this.remainingSeconds--;
                this.updateDisplay();

                if (this.remainingSeconds <= 0) {
                    this.stop();
                    this.onTimerEnd();
                }
            }, 1000);
        }

        stop() {
            clearInterval(this.timerInterval);
        }

        updateDisplay() {
            const minutes = Math.floor(this.remainingSeconds / 60);
            const seconds = this.remainingSeconds % 60;
            timerDisplay.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        onTimerEnd() {
            githubLinkInput.disabled = true;
            submitExamButton.disabled = true;
            alert('Tiempo de examen terminado');
        }
    }

    const timer = new ExamTimer(examTimeLimit);
    timer.start();

    examSubmissionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const githubLink = githubLinkInput.value.trim();

        if (!validateGithubLink(githubLink)) {
            alert('Por favor, ingrese un enlace válido de GitHub');
            return;
        }

        try {
            const response = await fetch('/submit_exam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    github_link: githubLink,
                    access_id: examInfo.access_id  // Add this line 
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert('Examen enviado exitosamente');
                window.location.href = '/';  // Redirigir al inicio
            } else {
                alert(data.message || 'Error al enviar el examen');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Hubo un problema al enviar el examen');
        }
    });
});