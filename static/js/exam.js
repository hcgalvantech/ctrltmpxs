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

    // Obtener información del examen
    const examInfo = JSON.parse(localStorage.getItem('examInfo') || '{}');
    const examTimeLimit = examInfo.exam_time_limit || 120; // Default 2 hours

    class ExamTimer {
        constructor(totalMinutes) {
            this.totalMinutes = totalMinutes;
            this.timerInterval = null;
            this.startTime = null;
            this.endTime = null;
        }

        async initialize() {
            // Verificar estado del examen con el servidor
            try {
                const response = await fetch('/check_exam_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        access_id: examInfo.access_id 
                    })
                });

                const statusData = await response.json();

                if (!statusData.can_continue) {
                    this.onTimerEnd();
                    return false;
                }

                // Establecer tiempos basados en respuesta del servidor o localStorage
                const storedStartTime = localStorage.getItem('examStartTime');
                const storedEndTime = localStorage.getItem('examEndTime');

                if (storedStartTime && storedEndTime) {
                    this.startTime = parseInt(storedStartTime);
                    this.endTime = parseInt(storedEndTime);
                } else {
                    // Primera vez iniciando el examen
                    this.startTime = Date.now();
                    this.endTime = this.startTime + (this.totalMinutes * 60 * 1000);
                    
                    localStorage.setItem('examStartTime', this.startTime);
                    localStorage.setItem('examEndTime', this.endTime);
                }

                return true;
            } catch (error) {
                console.error('Error verificando estado del examen:', error);
                this.onTimerEnd();
                return false;
            }
        }

        start() {
            this.timerInterval = setInterval(() => {
                const currentTime = Date.now();
                const remainingTime = this.endTime - currentTime;

                if (remainingTime <= 0) {
                    this.stop();
                    this.onTimerEnd();
                    return;
                }

                this.updateDisplay(remainingTime);
            }, 1000);
        }

        stop() {
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }
        }

        updateDisplay(remainingTime) {
            const minutes = Math.floor(remainingTime / 60000);
            const seconds = Math.floor((remainingTime % 60000) / 1000);
            timerDisplay.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        onTimerEnd() {
            this.stop();
            githubLinkInput.disabled = true;
            submitExamButton.disabled = true;
            alert('Tiempo de examen terminado');
            localStorage.removeItem('examStartTime');
            localStorage.removeItem('examEndTime');
        }
    }

    // Inicializar y comenzar el temporizador
    async function initializeExam() {
        const timer = new ExamTimer(examTimeLimit);
        const canContinue = await timer.initialize();
        
        if (canContinue) {
            timer.start();

            // Prevenir salida o recarga
            window.addEventListener('beforeunload', (e) => {
                e.preventDefault();
                e.returnValue = ''; // Mostrar advertencia del navegador
            });
        }
    }

    // Llamar a la inicialización
    initializeExam();

    examSubmissionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const githubLink = githubLinkInput.value.trim();
        
        // Validaciones previas...
        if (!validateGithubLink(githubLink)) {
            alert('Por favor, ingrese un enlace válido de GitHub');
            return;
        }
    
        if (!examInfo.access_id) {
            alert('Información de acceso no disponible. Por favor, inicie sesión de nuevo.');
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
                    access_id: examInfo.access_id
                })
            });
    
            const responseData = await response.json();
    
            if (response.ok) {
                alert('Examen enviado exitosamente');
                window.location.href = '/';
            } else {
                alert(responseData.message || 'Error al enviar el examen');
            }
        } catch (error) {
            console.error('Error en el envío del examen:', error);
            alert('Hubo un problema al enviar el examen');
        }
    });
});