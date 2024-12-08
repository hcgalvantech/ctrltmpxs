from flask import Flask, render_template, request, jsonify
from src.exam_manager import ExamManager
from src.logging_config import setup_logging
from src.config import Config
import re
import logging

# Setup logging
logger = setup_logging()

app = Flask(__name__, template_folder='template')

# Add error handling with logging
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
    return render_template('error.html', 
                           error_title='Error Interno del Servidor', 
                           error_message='Ocurrió un error inesperado'), 500

exam_manager = ExamManager()

# Existing routes with added logging
@app.route('/')
def index():
    logger.info("Accessing index page")
    return render_template('index.html')

@app.route('/validate_dni', methods=['POST'])
def validate_dni():
    dni = request.json.get('dni')
    
    logger.info(f"Validating DNI: {dni}")
    
    # Validate DNI input
    if not re.match(r'^\d+$', str(dni)):
        logger.warning(f"Invalid DNI format: {dni}")
        return jsonify({
            'error': 'DNI inválido. Solo se permiten números.'
        }), 400

    result = exam_manager.check_exam_eligibility(int(dni))
    
    if result['eligible']:
        logger.info(f"DNI {dni} is eligible for exam")
        return jsonify({
            'status': 'success',
            'student_info': {
                'dni': result['student_data']['alumno'].dni,
                'nombre': result['student_data']['alumno'].apenom,
                'email': result['student_data']['inscriptos'].email,
                'tecnicatura': result['student_data']['tecnicatura'].tectun,
                'exam_time_limit': result['exam_time_limit']
            }
        })
    else:
        logger.warning(f"DNI {dni} not eligible: {result['message']}")
        return jsonify({
            'status': 'error',
            'message': result['message']
        }), 400

@app.route('/exam')
def exam():
    logger.info("Accessing exam page")
    # Fetch exam instructions
    exam_instructions = exam_manager.get_exam_instructions(1)  # Assuming exam_id is 1
    return render_template('exam.html', exam_instructions=exam_instructions)

@app.route('/start_exam', methods=['POST'])
def start_exam():
    logger.info("Starting exam")
    # Implement exam start logic
    student_data = request.json.get('student_data')
    try:
        access_record = exam_manager.start_exam(student_data)
        return jsonify({'status': 'success', 'access_id': access_record.id})
    except Exception as e:
        logger.error(f"Error starting exam: {str(e)}")
        return jsonify({'status': 'error', 'message': 'No se pudo iniciar el examen'}), 500

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    logger.info("Submitting exam")
    data = request.json
    github_link = data.get('github_link')
    access_id = data.get('access_id')  # You'll need to pass this from frontend

    try:
        result = exam_manager.submit_exam(access_id, github_link)
        if result:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo enviar el examen'}), 400
    except Exception as e:
        logger.error(f"Error submitting exam: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error al enviar el examen'}), 500

if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY  # Add a secret key for flash messages
    app.run(debug=True)