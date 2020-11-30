from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy.dialects.mysql import TINYINT

#from flask_marshmallow import Marshmallow
db= SQLAlchemy()
#ma= Marshmallow()

class Admin(db.Model):
  __tablename__= 'admin'
  idAdmin = db.Column(db.Integer, primary_key = True)
  usuario = db.Column(db.String(45), unique=True)
  contrasena = db.Column(db.String(255), nullable=False)
  def __init__(self,usuario,contrasena):
    self.usuario = usuario
    self.contrasena = self.__create_password(contrasena)

  def __create_password(self, password):
      return generate_password_hash(password).decode('utf-8')
  def new_password(self, password):
    return generate_password_hash(password).decode('utf-8')
  def verify_password(self, contrasena):
      return check_password_hash(self.contrasena , contrasena)

class Monitor(db.Model):
  __tablename__= 'monitores'
  idMonitor = db.Column(db.Integer, primary_key = True)
  nombre = db.Column(db.String(45), nullable=False)
  usuario = db.Column(db.String(45), unique=True, nullable=False)
  contrasena = db.Column(db.String(255), nullable=False)

  pacientes= db.relationship("Paciente" , cascade="all,delete", passive_deletes=True)
  def __init__(self, nombre, usuario, contrasena):
    self.nombre = nombre
    self.usuario = usuario
    self.contrasena = self.__create_password(contrasena)

  def __create_password(self, password):
    return generate_password_hash(password).decode('utf-8')
  def new_password(self, password):
    return generate_password_hash(password).decode('utf-8')
  def verify_password(self, contrasena):
    return check_password_hash(self.contrasena , contrasena)


class Paciente(db.Model):
  __tablename__= 'pacientes'
  idPaciente = db.Column(db.Integer, primary_key = True)
  nombre = db.Column(db.String(45), nullable=False)
  rut = db.Column(db.String(45), unique=True, nullable=False)
  mapa_hogar = db.Column(db.String(255), unique=True)
  id_monitor = db.Column(db.Integer , db.ForeignKey('monitores.idMonitor', ondelete="cascade", onupdate="cascade") , nullable=False )

  sensores = db.relationship("Sensor", cascade="all,delete", passive_deletes=True)
  def __init__(self, nombre, rut, id_monitor, mapa_hogar):
    self.nombre=nombre
    self.rut = rut
    self.id_monitor = id_monitor
    self.mapa_hogar=mapa_hogar

class Sensor(db.Model):
  __tablename__= 'sensores'
  idSensor = db.Column(db.Integer, primary_key = True)
  ubicacion= db.Column(db.Integer, nullable=False)
  apodo_ubicacion= db.Column(db.String(90), nullable=False)
  estado = db.Column(db.Enum('activo', 'desactivado'), nullable=False)
  tipo_sensor = db.Column(db.Enum('trisensor', 'caidasensor'), nullable=False)
  disponible= db.Column(TINYINT(unsigned=True), default=1, nullable=False)
  id_paciente = db.Column(db.Integer , db.ForeignKey('pacientes.idPaciente', ondelete="cascade", onupdate="cascade"), nullable=False )

  datos= db.relationship("DatoSensor", cascade="all,delete", passive_deletes=True)
  def __init__(self, ubicacion, apodo_ubicacion, estado, tipo_sensor, id_paciente):
    self.ubicacion = ubicacion
    self.apodo_ubicacion=apodo_ubicacion
    self.estado=estado
    self.tipo_sensor = tipo_sensor
    self.id_paciente = id_paciente

class DatoSensor(db.Model):
  __tablename__= 'datos_sensor'
  __table_args__= (
    db.UniqueConstraint('fecha', 'id_sensor', name='dato_sensor_unique_index'),
  )
  idDato = db.Column(db.Integer, primary_key = True)
  fecha= db.Column(db.DateTime, nullable=False)
  presencia = db.Column(TINYINT(unsigned=True), nullable=False)
  id_sensor = db.Column(db.Integer , db.ForeignKey('sensores.idSensor', ondelete="cascade", onupdate="cascade") , nullable=False)
  def __init__(self,fecha,presencia,id_sensor_trisensor):
    self.fecha=fecha
    self.presencia=presencia
    self.id_sensor_trisensor=id_sensor_trisensor
  
""" class Datos_sensorSchema(ma.Schema):
  class Meta:
    fields= ('idDato', 'fecha', 'presencia','id_sensor')

dato_sensor_schema = Datos_sensorSchema()
datos_sensor_schema = Datos_sensorSchema(many=True) """