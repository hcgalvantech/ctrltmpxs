import os
import sys
from flask import Flask, render_template, request, jsonify
from src.exam_manager import ExamManager
from src.logging_config import setup_logging
from src.config import Config
from src.models import Alumno, Inscriptos, Tecnicatura, Turnos, Examen, Acceso
import re
import logging
from datetime import datetime
from dotenv import load_dotenv

# Get the absolute path of the project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

# Validate configuration
Config.validate()

# Setup logging
logger = setup_logging()

# Configure Flask app with dynamic template and static paths
app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'template'),  
            static_folder=os.path.join(PROJECT_ROOT, 'static'))

# Configure Flask with settings from Config
app.config.from_object(Config)


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

    exam_manager = ExamManager()
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
                'exam_time_limit': result['exam_time_limit'],
                'inscriptos': {
                    'id': result['student_data']['inscriptos'].id  # Añadir ID de inscripción
                }
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
    exam_manager = ExamManager()
    # Asume que el ID de examen es 1, ajusta según tu configuración
    exam_instructions = exam_manager.get_exam_instructions(1)  
    return render_template('exam.html', exam_instructions=exam_instructions or '')

# Ruta para iniciar examen
@app.route('/start_exam', methods=['POST'])
def start_exam():
    logger.info("Starting exam")
    exam_manager = ExamManager()
    
    try:
        # Obtener datos del estudiante del JSON
        student_data = request.json.get('student_data')
        
        if not student_data:
            logger.error("No student data provided")
            return jsonify({
                'status': 'error', 
                'message': 'Datos del estudiante no proporcionados'
            }), 400
        
        # Extraer el ID de inscripción
        inscriptos_id = student_data.get('inscriptos', {}).get('id')
        
        if not inscriptos_id:
            logger.error("No inscriptos ID found")
            return jsonify({
                'status': 'error', 
                'message': 'ID de inscripción no encontrado'
            }), 400
        
        # Iniciar examen
        access_record = exam_manager.start_exam(inscriptos_id)
        
        if access_record:
            return jsonify({
                'status': 'success', 
                'access_id': access_record.id  # Esto debería funcionar ahora
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'No se pudo iniciar el examen'
            }), 500
    
    except Exception as e:
        logger.error(f"Error starting exam: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'Error interno: {str(e)}'
        }), 500
        
# Ruta para enviar examen
@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    logger.info("Submit exam request received")
    
    try:
        # Obtener datos JSON de manera segura
        data = request.get_json()
        
        # Validar que se recibieron datos
        if not data:
            logger.error("No data received in submit_exam")
            return jsonify({
                'status': 'error', 
                'message': 'No se recibieron datos de envío'
            }), 400
        
        # Extraer github_link y access_id
        github_link = data.get('github_link')
        access_id = data.get('access_id')
        
        # Validar campos
        if not github_link:
            logger.error("Missing GitHub link")
            return jsonify({
                'status': 'error', 
                'message': 'Falta el enlace de GitHub'
            }), 400
        
        if not access_id:
            logger.error("Missing access_id")
            return jsonify({
                'status': 'error', 
                'message': 'Falta el ID de acceso'
            }), 400
        
        # Instanciar ExamManager
        exam_manager = ExamManager()
        
        # Intentar enviar el examen
        result = exam_manager.submit_exam(access_id, github_link)
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Examen enviado exitosamente'
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'No se pudo enviar el examen'
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in submit_exam: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'Error interno: {str(e)}'
        }), 500

# Manejo del tiempo
@app.route('/check_exam_status', methods=['POST'])
def check_exam_status():
    """Verificar si el examen puede continuar"""
    try:
        data = request.json
        access_id = data.get('access_id')
        
        if not access_id:
            return jsonify({
                'can_continue': False,
                'message': 'ID de acceso no proporcionado'
            }), 400
        
        exam_manager = ExamManager()
        
        # Verificar si el registro de acceso existe y es válido
        session = exam_manager.db.get_connection()
        try:
            access_record = session.query(Acceso).filter_by(id=access_id).first()
            
            if not access_record:
                return jsonify({
                    'can_continue': False,
                    'message': 'Registro de acceso no encontrado'
                }), 400
            
            # Verificar si ya se envió el examen
            if access_record.hora:
                return jsonify({
                    'can_continue': False,
                    'message': 'El examen ya ha sido enviado'
                }), 400
            
            # Añadir logging para debug
            logger.info(f"Access Record: {access_record}")
            logger.info(f"Access Record idins: {access_record.idins}")
            
            # Verificar inscriptos
            inscriptos = session.query(Inscriptos).filter_by(id=access_record.idins).first()
            
            if not inscriptos:
                logger.error(f"No se encontró inscripción para idins: {access_record.idins}")
                return jsonify({
                    'can_continue': False,
                    'message': 'Información de inscripción no encontrada'
                }), 400
            
            logger.info(f"Inscriptos: {inscriptos}")
            logger.info(f"Inscriptos idtectun: {inscriptos.idtectun}")
            
            # Verificar turnos
            turnos = session.query(Turnos).filter_by(idtec=inscriptos.idtectun).first()
            
            if not turnos:
                logger.error(f"No se encontró turno para idtectun: {inscriptos.idtectun}")
                return jsonify({
                    'can_continue': False,
                    'message': 'Información de turno no encontrada'
                }), 400
            
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.now() - access_record.acceso
            
            if tiempo_transcurrido.total_seconds() > (turnos.tiempo * 60):
                return jsonify({
                    'can_continue': False,
                    'message': 'Tiempo máximo de examen excedido'
                }), 400
            
            return jsonify({
                'can_continue': True
            })
        
        except Exception as e:
            logger.error(f"Error en check_exam_status: {str(e)}", exc_info=True)
            return jsonify({
                'can_continue': False,
                'message': 'Error al verificar el estado del examen'
            }), 500
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error checking exam status: {str(e)}", exc_info=True)
        return jsonify({
            'can_continue': False,
            'message': 'Error interno del servidor'
        }), 500
                
# Add a catch-all route for client-side routing
@app.route('/<path:path>')
def catch_all(path):
    logger.info(f"Catching route: {path}")
    # Check if the requested template exists
    template_path = os.path.join(PROJECT_ROOT, 'template', f'{path}.html')
    
    if os.path.exists(template_path):
        return render_template(f'{path}.html')
    
    # If no specific template, default to index
    return render_template('index.html')

# Manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {request.url}")
    return render_template('error.html', 
                           error_title='Página No Encontrada', 
                           error_message='La página solicitada no existe'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    return render_template('error.html', 
                           error_title='Error Interno del Servidor', 
                           error_message='Ocurrió un error inesperado'), 500



if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY  # Add a secret key for flash messages
    app.run(debug=True)