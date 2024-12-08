// static/js/index.js
document.addEventListener('DOMContentLoaded', () => {
    const dniForm = document.getElementById('dni-form');
    const studentInfo = document.getElementById('student-info');
    const startExamButton = document.getElementById('start-exam');

    dniForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const dniInput = document.getElementById('dni');
        
        // Reset previous state
        studentInfo.style.display = 'none';
        startExamButton.style.display = 'none';
        dniInput.classList.remove('is-invalid');

        const dni = dniInput.value.trim();

        // Validate DNI client-side
        const dniRegex = /^\d{7,8}$/;
        if (!dniRegex.test(dni)) {
            dniInput.classList.add('is-invalid');
            document.getElementById('dni-error').textContent = 
                'DNI inválido. Debe contener 7 u 8 dígitos sin puntos.';
            return;
        }

        try {
            const response = await fetch('/validate_dni', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dni: dni })
            });

            const data = await response.json();

            if (response.ok) {
                // Populate student info
                document.getElementById('info-dni').textContent = data.student_info.dni;
                document.getElementById('info-nombre').textContent = data.student_info.nombre;
                document.getElementById('info-email').textContent = data.student_info.email;
                document.getElementById('info-tecnicatura').textContent = data.student_info.tecnicatura;

                // Show student info and exam button
                studentInfo.style.display = 'block';
                startExamButton.style.display = 'block';
                
                // Store exam info in local storage
                localStorage.setItem('examInfo', JSON.stringify(data.student_info));
            } else {
                // Show error message
                alert(data.message || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Hubo un problema al validar el DNI');
        }
    });

    // Start Exam Button
    startExamButton.addEventListener('click', () => {
        window.location.href = '/exam';
    });
})