# src/exam_manager.py
import datetime
from sqlalchemy import and_
from .database import DatabaseConnection
from .models import Alumno, Inscriptos, Tecnicatura, Turnos, Examen, Acceso
from .email_sender import send_exam_submission_email

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

    def start_exam(self, student_data):
        """Record exam access"""
        session = self.db.get_connection()
        try:
            new_access = Acceso(
                idins=student_data['inscriptos'].id,
                timestamp=datetime.datetime.now()
            )
            session.add(new_access)
            session.commit()
            return new_access
        finally:
            session.close()

    def submit_exam(self, access_id, github_link):
        """Submit exam and send confirmation email"""
        session = self.db.get_connection()
        try:
            access_record = session.query(Acceso).filter_by(id=access_id).first()
            if access_record:
                access_record.hora = datetime.datetime.now()
                access_record.link = github_link
                session.commit()

                # Get student email
                inscriptos = session.query(Inscriptos).filter_by(id=access_record.idins).first()
                
                # Send email
                send_exam_submission_email(
                    inscriptos.email, 
                    access_record.hora, 
                    github_link
                )

                return True
            return False
        finally:
            session.close()

    def get_exam_instructions(self, exam_id):
        """Retrieve exam README instructions"""
        session = self.db.get_connection()
        try:
            exam = session.query(Examen).filter_by(id=exam_id).first()
            return exam.exalink if exam else None
        finally:
            session.close()