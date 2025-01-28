# src/exam_manager.py
import datetime
from sqlalchemy import and_
from .database import DatabaseConnection
from .models import Alumno, Inscriptos, Tecnicatura, Turnos, Examen, Acceso
from .email_sender import send_exam_submission_email
from src.logging_config import setup_logging
import logging

# Setup logging
logger = setup_logging()

class ExamManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def validate_dni(self, dni):
        """Validate and find student details based on DNI"""
        session = self.db.get_connection()
        try:
            alumno = session.query(Alumno).filter_by(dni=dni).first()
            if not alumno:
                return None

            # Find related inscriptos
            inscriptos = session.query(Inscriptos).filter_by(iddni=alumno.id).first()
            if not inscriptos:
                return None

            # Find tecnicatura
            tecnicatura = session.query(Tecnicatura).filter_by(id=inscriptos.idtectun).first()

            # Find turnos
            turnos = session.query(Turnos).filter(
                and_(
                    Turnos.idtec == inscriptos.idtectun,
                    Turnos.regular == inscriptos.regular
                )
            ).first()

            return {
                'alumno': alumno,
                'inscriptos': inscriptos,
                'tecnicatura': tecnicatura,
                'turnos': turnos
            }
        finally:
            session.close()

    def check_exam_eligibility(self, dni):
        """Check if student can take the exam"""
        session = self.db.get_connection()
        try:
            student_data = self.validate_dni(dni)
            if not student_data:
                return {'eligible': False, 'message': 'No existe DNI inscripto para RENDIR EXAMENES FINALES EN CASA'}

            current_time = datetime.datetime.now()
            turnos = student_data['turnos']

            # Check exam date range
            if turnos.f_desde <= current_time <= turnos.f_hasta:
                # Check if already took the exam
                existing_access = session.query(Acceso).filter_by(
                    idins=student_data['inscriptos'].id
                ).first()

                if existing_access:
                    return {
                        'eligible': False, 
                        'message': 'Ya ha ocupado su cupón de EXAMEN'
                    }

                return {
                    'eligible': True,
                    'student_data': student_data,
                    'exam_time_limit': turnos.tiempo
                }
            else:
                return {
                    'eligible': False, 
                    'message': 'Fuera del rango de fechas para tomar el examen'
                }
        finally:
            session.close()

    def start_exam(self, inscriptos_id):
        """Record exam access"""
        session = self.db.get_connection()
        try:
            # Convertir a int si es necesario
            inscriptos_id = int(inscriptos_id)
            
            # Verificar si ya existe un registro de acceso
            existing_access = session.query(Acceso).filter_by(idins=inscriptos_id).first()
            
            if existing_access:
                logger.warning(f"Acceso ya registrado para inscriptos_id: {inscriptos_id}")
                # Crear una copia de los datos antes de cerrar la sesión
                access_data = {
                    'id': existing_access.id,
                    'idins': existing_access.idins,
                    'timestamp': existing_access.timestamp
                }
                session.close()
                
                # Recrear un objeto similar al original
                new_access = Acceso()
                new_access.id = access_data['id']
                new_access.idins = access_data['idins']
                new_access.timestamp = access_data['timestamp']
                return new_access
            
            # Crear nuevo registro de acceso
            new_access = Acceso(
                idins=inscriptos_id,
                acceso=datetime.datetime.now()
            )
            
            session.add(new_access)
            session.commit()
            
            # Obtener el ID antes de cerrar la sesión
            access_id = new_access.id
            
            logger.info(f"Nuevo acceso registrado para inscriptos_id: {inscriptos_id}, ID: {access_id}")
            
            # Crear un objeto desconectado para devolver
            disconnected_access = Acceso()
            disconnected_access.id = access_id
            disconnected_access.idins = inscriptos_id
            disconnected_access.acceso = new_access.acceso
            
            # Cerrar la sesión
            session.close()
            
            return disconnected_access
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error registrando acceso: {str(e)}", exc_info=True)
            session.close()
            raise
                    
    def submit_exam(self, access_id, github_link):
        """Submit exam and update access record"""
        session = self.db.get_connection()
        try:
            # Convertir access_id a int si es necesario
            access_id = int(access_id)
            
            # Buscar registro de acceso
            access_record = session.query(Acceso).filter_by(id=access_id).first()
            
            # Validar que el registro exista
            if not access_record:
                logger.error(f"No access record found for access_id: {access_id}")
                session.close()
                return False
            
            # Actualizar registro con hora actual y enlace de GitHub
            access_record.hora = datetime.datetime.now()
            access_record.link = github_link
            
            # Confirmar cambios
            session.commit()
            
            # Obtener información del estudiante
            inscriptos = session.query(Inscriptos).filter_by(id=access_record.idins).first()
            
            # Enviar correo de confirmación
            if inscriptos and inscriptos.email:
                try:
                    send_exam_submission_email(
                        inscriptos.email, 
                        access_record.hora, 
                        github_link
                    )
                except Exception as email_error:
                    logger.error(f"Error sending confirmation email: {str(email_error)}")
            
            logger.info(f"Exam submitted successfully for access_id: {access_id}")
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error in submit_exam: {str(e)}", exc_info=True)
            return False
        finally:
            session.close()
                        
    # def get_exam_instructions(self, exam_id):
    #    """Retrieve exam README instructions"""
    #    session = self.db.get_connection()
    #    try:
    #        exam = session.query(Examen).filter_by(id=exam_id).first()
    #        return exam.exalink if exam else None
    #    finally:
    #        session.close()
            

    def get_exam_instructions(self, exam_id):
        """Retrieve exam README instructions"""
        session = self.db.get_connection()
        try:
            # Log de depuración para ver el valor de exam_id
            logger.info(f"Buscando instrucciones de examen para ID: {exam_id}")
            
            # Buscar el exalink a través de la relación con Turnos
            exam = (
                session.query(Examen)
                .join(Turnos, Turnos.idexa == Examen.id)
                .filter(Turnos.idexa == exam_id)
                .first()
            )
            
            if not exam:
                logger.error(f"No se encontraron instrucciones para Exam ID: {exam_id}")
                return None
            
            # Log de depuración para ver el exalink recuperado
            logger.info(f"Exalink encontrado: {exam.exalink}")
            
            # Devolver el exalink
            return exam.exalink
        except Exception as e:
            logger.error(f"Error al obtener instrucciones de examen: {str(e)}", exc_info=True)
            return None
        finally:
            session.close()