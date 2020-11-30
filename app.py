from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session

# tesis
import numpy as np
import pandas as pd
from datetime import datetime, timedelta , date

import sys
import eltransformador as gctransform
import os
from time import time
from time import sleep
import simplejson as json
import random
from os import path
from dateutil import relativedelta

from werkzeug.utils import secure_filename

from celeron import *

from config import *
from models import *
import uuid

""" Se Define la configuración de FLASK ubicado en config.py"""
app = Flask(__name__)
app.config.from_object(Config)


#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'prueba_sensores2'
#app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'

#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#csrf = CsrfProtect(app)

#app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
#app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'

celery = make_celery(app)

#mysql = MySQL(app)
#bcrypt = Bcrypt(app)

@celery.task()
def generar_carga_caidasensor(fecha, fecha_inicio, fecha_termino, archivo , id_sensor_caida):
    df2 = gctransform.generar_carga_caida(fecha, fecha_inicio, fecha_termino,archivo )

    """ valueslist = "VALUES "
    for index, row in df2.iterrows():
        valueslist = valueslist + "('{}', {}, {}),".format(row['fecha'].strftime("%Y-%m-%d %H:%M:%S"),  row['presencia'], id_sensor_caida)
    valueslist = 'INSERT INTO datos_sensor (fecha, presencia, id_sensor) ' + valueslist[:-1] + ' ON DUPLICATE KEY UPDATE datos_sensor.presencia=values(presencia) '
    db.engine.execute(valueslist) """
     
    for index, row in df2.iterrows():
        db.engine.execute('INSERT INTO datos_sensor (fecha, presencia, id_sensor) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE datos_sensor.presencia=%s', (row['fecha'].strftime("%Y-%m-%d %H:%M:%S"),  row['presencia'], id_sensor_caida,  row['presencia']))
        
        


def verify_mapa_imagen(mapa_imagen):
    if not "." in mapa_imagen:
        return False
    ext = mapa_imagen.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False
    

@app.before_request
def before_request():

    """ if 'usuario' not in session and request.endpoint in ['monitor_logout','pacientes_inicio','pacientes_agregar','pacientes_modificar','pacientes_actualizar','paciente_dashboard','pacientes_lista_sensores','pacientes_trisensor_agregar','pacientes_caidasensor_agregar','pacientes_trisensor_modificar','pacientes_trisensor_eliminar','cargar_datos_trisensor','pacientes_caidasensor_modificar','generar_datos_caida_carga','ajax_filtrar_fechas','ajax_trisensor_presencia_fecha','ajax_detalles','monitor_cambiar_contrasena']:
        flash("No ha iniciado sesión2", "error")
        return redirect(url_for('monitor_login'))
    elif 'usuario' not in session and request.endpoint in ['admin_logout','admin_lista_monitores','admin_monitor_agregar','admin_monitor_borrar','admin_monitor_modificar','admin_monitor_resetear_contrasena' , 'admin_cambiar_contrasena']:
        flash("No ha iniciado sesión2", "error")
        return redirect(url_for('admin_login'))
    elif 'usuario' in session:
        if session["tipo"]=='monitor' and request.endpoint not in ['static','monitor_logout','pacientes_inicio','pacientes_agregar','pacientes_modificar','pacientes_actualizar','paciente_dashboard','pacientes_lista_sensores','pacientes_trisensor_agregar','pacientes_caidasensor_agregar','pacientes_trisensor_modificar','pacientes_trisensor_eliminar','cargar_datos_trisensor','pacientes_caidasensor_modificar','generar_datos_caida_carga','ajax_filtrar_fechas','ajax_trisensor_presencia_fecha','ajax_detalles','monitor_cambiar_contrasena']:
            flash("No tiene permiso para entrar", "error")
            return redirect(url_for('pacientes_inicio'))
        elif session["tipo"]=='admin' and request.endpoint not in ['static','admin_logout','admin_lista_monitores','admin_monitor_agregar','admin_monitor_borrar','admin_monitor_modificar', 'admin_monitor_resetear_contrasena','admin_cambiar_contrasena']:
            flash("No tiene permiso para entrar", "error")
            return redirect(url_for('admin_lista_monitores')) """


@app.route('/')
def index():
    return redirect(url_for("monitor_login"))


#############################################################
#############################################################
########### ADMIN ############
# Las siguientes rutas con las principales funciones del Administrador

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena'].encode('utf-8')

        admin = Admin.query.filter_by(usuario = usuario).first()

        if admin is not None and admin.verify_password(contrasena):
            session["id"] = admin.idAdmin
            session["usuario"] = usuario
            session["tipo"] = "admin"
            flash("Ha iniciado sesión correctamente", "success")
            return redirect(url_for("admin_lista_monitores"))
        else:
            flash("Uno de sus datos ingresados es incorrecto", "error")
            return redirect(url_for("admin_login"))

        return "login"
    return render_template('admin/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('id', None)
    session.pop('usuario', None)
    session.pop('tipo', None)
    flash("Se ha desconectado correctamente", "success")
    return redirect(url_for("admin_login"))

    
@app.route('/admin/lista_monitores')
def admin_lista_monitores():
    lista_monitores = Monitor.query.all()
    title = "Monitores"
    return render_template('admin/lista_monitores.html', title=title, lista_monitores=lista_monitores)

@app.route('/admin/monitor/agregar', methods=['GET', 'POST'])
def admin_monitor_agregar():

    if request.method == 'POST':
        nombre_monitor = request.form['nombre_monitor']
        usuario_monitor = request.form['usuario_monitor']
        #contrasena = bcrypt.generate_password_hash('emonitor')

        if nombre_monitor and usuario_monitor:
            monitor_aux = Monitor.query.filter_by(usuario = usuario_monitor).first()
            if not monitor_aux:
                nuevo_monitor = Monitor(nombre_monitor,  usuario_monitor , 'emonitor')

                db.session.add(nuevo_monitor)
                db.session.commit()

                flash("Se ha agregado monitor correctamente", "success")
                return redirect(url_for("admin_lista_monitores"))
            else:
                flash("Usuario monitor ya existe", "error")
                return redirect(url_for("admin_lista_monitores"))
        else:
            flash("No ha ingresado correctamente los datos en el formulario", "error")
            return redirect(url_for("admin_lista_monitores"))

    title = "Agregar Monitor"
    return render_template('admin/agregar_monitor.html', title=title)

@app.route('/admin/monitor/eliminar', methods=['POST'])
def admin_monitor_borrar():

    if request.method == 'POST':
        id_monitor = request.form['id-monitor']
        monitor_aux= Monitor.query.get(id_monitor)
        if monitor_aux:
            db.session.delete(monitor_aux)
            db.session.commit()
            flash("Se ha eliminado Monitor correctamente", "success")
            return redirect(url_for("admin_lista_monitores"))
        else:
            flash("Monitor no existe", "error")
            return redirect(url_for("admin_lista_monitores"))

@app.route('/admin/monitor/modificar/<int:idMonitor>', methods=['GET','POST'])
def admin_monitor_modificar(idMonitor=None):

    if request.method == 'POST':
        id_monitor = format(idMonitor)
        monitor_aux= Monitor.query.get(id_monitor)
        if monitor_aux:
            nombre_monitor = request.form['nombre_monitor']
            usuario_monitor = request.form['usuario_monitor']
            if not nombre_monitor or not usuario_monitor:
                flash("No ha rellenado todos los campos", "error")
                return redirect(url_for("admin_lista_monitores"))

            #monitor_aux2 = Monitor.query.filter_by(usuario = usuario_monitor).first()
            monitor_aux2 = Monitor.query.filter(Monitor.usuario == usuario_monitor, Monitor.idMonitor!= id_monitor).first()
            if not monitor_aux2  :
                monitor_aux.nombre = nombre_monitor
                monitor_aux.usuario = usuario_monitor
                db.session.commit()
                flash("Monitor actualizado correctamente", "success")
                return redirect(url_for("admin_lista_monitores"))
            else:
                flash("El usuario del monitor ya existe", "error")
                return redirect(url_for("admin_lista_monitores"))
        else:
            flash("Monitor no existe", "error")
            return redirect(url_for("admin_lista_monitores"))

    id_monitor = format(idMonitor)
    monitor = Monitor.query.get(id_monitor)
    if monitor is not None:
        title = "Modificar Monitor"
        return render_template('admin/modificar_monitor.html', title=title, monitor=monitor)
    else:
        flash("Monitor no existe", "error")
        return redirect(url_for("admin_lista_monitores"))
    
@app.route('/admin/monitor/resetear_contrasena/<int:idMonitor>')
def admin_monitor_resetear_contrasena(idMonitor=None):

    id_monitor = format(idMonitor)
    monitor_aux= Monitor.query.get(id_monitor)
    if monitor_aux:
        monitor_aux.contrasena = monitor_aux.new_password("emonitor")
        db.session.commit()
        flash("Contraseña de Monitor reseteada correctamente", "success")
        return redirect(url_for("admin_lista_monitores"))
    else:
        flash("Monitor no existe", "error")
        return redirect(url_for("admin_lista_monitores"))

@app.route('/admin/cambiar_contrasena', methods=['GET', 'POST'])
def admin_cambiar_contrasena():
    if request.method == 'POST':
        contrasena_nueva = request.form['contrasena_nueva']
        repite_contrasena_nueva = request.form['repite_contrasena_nueva']
        admin = Admin.query.get(session['id'])
        if admin:
            if contrasena_nueva==repite_contrasena_nueva:
                admin.contrasena = admin.new_password(contrasena_nueva)
                db.session.commit()
                flash("Su contraseña ha sido cambiada correctamente", "success")
                return redirect(url_for("admin_lista_monitores"))
            else:
                flash("Contraseñas deben ser iguales", "error")
                return redirect(url_for("admin_lista_monitores"))
        else:
            flash("Monitor no existe", "error")
            return redirect(url_for("admin_lista_monitores"))

    return render_template('admin/admin_cambiar_contrasena.html')

#############################################################
#############################################################
############ MONITOR ############

@app.route('/monitor/login', methods=['GET', 'POST'])
def monitor_login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        monitor = Monitor.query.filter_by(usuario = usuario).first()

        if monitor is not None and monitor.verify_password(contrasena):
            session["id"] = monitor.idMonitor
            session["usuario"] = usuario
            session["tipo"] = "monitor"
            flash("Ha iniciado sesión correctamente", "success")
            return redirect(url_for("pacientes_inicio"))
        else:
            flash("Uno de sus datos ingresados es incorrecto", "error")
            return redirect(url_for("monitor_login"))
    title = "Bienvenido a EHM - Iniciar Sesión Monitores"
    return render_template('monitor/login.html' , title = title)


@app.route('/monitor/cambiar_contrasena', methods=['GET', 'POST'])
def monitor_cambiar_contrasena():
    if request.method == 'POST':
        contrasena_nueva = request.form['contrasena_nueva']
        repite_contrasena_nueva = request.form['repite_contrasena_nueva']
        monitor = Monitor.query.get(session['id'])
        if monitor is not None:
            if contrasena_nueva==repite_contrasena_nueva:
                monitor.contrasena = monitor.new_password(contrasena_nueva)
                db.session.commit()
                flash("Su contraseña ha sido cambiada correctamente", "success")
                return redirect(url_for("pacientes_inicio"))
            else:
                flash("Contraseñas deben ser iguales", "error")
                return redirect(url_for("monitor_cambiar_contrasena"))
        else:
            flash("Monitor no existe", "error")
            return redirect(url_for("monitor_cambiar_contrasena"))
    title = "Monitor - Cambiar contraseña"
    return render_template('cambiar_contrasena.html' , title=title)

@app.route('/monitor/logout', methods=['GET', 'POST'])
def monitor_logout():
    session.pop('id', None)
    session.pop('usuario', None)
    session.pop('tipo', None)
    flash("Se ha desconectado correctamente", "success")
    return redirect(url_for("monitor_login"))

#############################################################
#############################################################

@app.route('/pacientes/')
def pacientes_inicio():

    id_monitor = session['id']
    lista_pacientes = Paciente.query.with_entities(Paciente.idPaciente, Paciente.nombre, Paciente.rut).filter_by(id_monitor = id_monitor).all()

    title = "Listado de Pacientes - Monitor"
    return render_template('lista_pacientes.html', title=title, lista_pacientes=lista_pacientes)

@app.route('/pacientes/agregar', methods=['GET', 'POST'])
def pacientes_agregar():

    if request.method == 'POST':
        nombre_paciente = request.form['nombre_paciente']
        rut_paciente = request.form['rut_paciente']
        id_monitor = session['id']
        mapa_imagen = request.files['mapa_imagen']
        
        if nombre_paciente and rut_paciente :
            paciente_aux= Paciente.query.filter_by(rut = rut_paciente).first()
            if not paciente_aux:
                if not request.files['mapa_imagen'].filename=="":
                    if verify_mapa_imagen(mapa_imagen.filename):
                        nombre_imagen= secure_filename( str(uuid.uuid4() )+ "."+mapa_imagen.filename.rsplit(".", 1)[1].upper())
                        mapa_imagen.save(os.path.join(app.config["IMAGE_UPLOADS"],nombre_imagen ) )
                    else:
                        flash("La imagen debe ser JPG o JPEG", "error")
                        return redirect(url_for("pacientes_inicio"))
                else:
                    nombre_imagen= None
                paciente = Paciente(nombre_paciente, rut_paciente,id_monitor , nombre_imagen)
                db.session.add(paciente)
                db.session.commit()

                flash("Paciente agregado con éxito", "success")
                return redirect(url_for("pacientes_inicio"))
                
            else:
                flash("Paciente ya existe", "error")
                return redirect(url_for("pacientes_inicio"))
        else:
            flash("No ha ingresado todos sus datos", "error")
            return redirect(url_for("pacientes_inicio"))

    title = "Agregar Paciente - Monitor"
    return render_template('agregar_paciente.html', title=title)

@app.route('/pacientes/eliminar', methods=['POST'])
def pacientes_borrar():

    if request.method == 'POST':
        id_paciente = request.form['id-paciente']
        paciente = Paciente.query.get(id_paciente)
        if paciente:
            db.session.delete(paciente)
            db.session.commit()
            flash("Se eliminó al Paciente correctamente", "success")
            return redirect(url_for("pacientes_inicio"))
        else:
            flash("Paciente no existe", "error")
            return redirect(url_for("pacientes_inicio"))

@app.route('/pacientes/modificar/<int:id>')
def pacientes_modificar(id=None):

    id_paciente = format(id)
    paciente = Paciente.query.with_entities(Paciente.idPaciente, Paciente.nombre, Paciente.rut , Paciente.mapa_hogar).filter_by(idPaciente = id_paciente).first()
    title = "Modificar Paciente - Monitor"
    return render_template('modificar_paciente.html', title=title, paciente=paciente)

@app.route('/pacientes/actualizar/<int:id>', methods=['POST'])
def pacientes_actualizar(id=None):
    id_paciente = format(id)
    if request.method == 'POST':
        paciente_aux= Paciente.query.get(id_paciente)
        if paciente_aux:
            paciente = Paciente.query.get(id_paciente)
            nombre_paciente = request.form['nombre_paciente']
            #rut_paciente = request.form['rut_paciente']

            if not nombre_paciente:
                flash("No puede haber nombre en blanco", "error")
                return redirect(url_for("pacientes_inicio"))


            if not request.files['mapa_imagen'].filename=="":
                mapa_imagen = request.files['mapa_imagen']
                if verify_mapa_imagen(mapa_imagen.filename):
                    if paciente.mapa_hogar is not None :
                        os.remove(os.path.join(app.config["IMAGE_UPLOADS"],paciente.mapa_hogar ))
                        nombre_imagen= secure_filename( str(uuid.uuid4() )+ "."+paciente.mapa_hogar.rsplit(".", 1)[1].upper())
                    else:
                        nombre_imagen= secure_filename( str(uuid.uuid4() )+ "."+mapa_imagen.filename.rsplit(".", 1)[1].upper())
                    mapa_imagen.save(os.path.join(app.config["IMAGE_UPLOADS"],nombre_imagen ) )
                    paciente.mapa_hogar= nombre_imagen
                else:
                    flash("La imagen debe ser JPG o JPEG", "error")
                    return redirect(url_for("pacientes_inicio"))
            
            paciente.nombre = nombre_paciente
            db.session.commit()
            flash("Los datos del Paciente se ha actualizado con éxito", "success")
            return redirect(url_for("pacientes_inicio"))
        else:
            flash("Paciente no existe", "error")
            return redirect(url_for("pacientes_inicio"))

##############################################################
##############################################################
########### DASHBOARD ##########

@app.route('/pacientes/dashboard/<int:idPaciente>')
def paciente_dashboard(idPaciente=None):

    id_paciente = format(idPaciente)
    fecha_actual_dashboard = date.today()
    fecha_inicial_dashboard= fecha_actual_dashboard - relativedelta.relativedelta(months=3)
    paciente = Paciente.query.get(id_paciente)
    title = "Dashboard Paciente " + paciente.nombre + " - Monitor"
    return render_template('dashboard_paciente.html', title=title, id_paciente=id_paciente, fecha_inicial_dashboard=fecha_inicial_dashboard, fecha_actual_dashboard=fecha_actual_dashboard , paciente=paciente )

##############################################################
##############################################################

@app.route('/pacientes/<int:idPaciente>/sensores')
def pacientes_lista_sensores(idPaciente=None):

    id_paciente = format(idPaciente)
    sensores_trisensor = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.estado, Sensor.disponible).filter_by(id_paciente = id_paciente, tipo_sensor='trisensor').all()
    sensores_caida = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.estado, Sensor.disponible).filter_by(id_paciente = id_paciente, tipo_sensor='caidasensor').all()

    title = "Listado de Sensores - Monitor"
    return render_template('lista_sensores.html', title=title, sensores_trisensor=sensores_trisensor, sensores_caida=sensores_caida, id_paciente=id_paciente)



##############################################################
@app.route('/pacientes/<int:idPaciente>/sensores/agregar_trisensor', methods=['GET', 'POST'])
def pacientes_trisensor_agregar(idPaciente=None):

    id_paciente = format(idPaciente)
    if request.method == 'POST':

        ubicacion = request.form['ubicacion']
        apodo_ubicacion = request.form['apodo_ubicacion']
        estado_sensor = request.form['estado_sensor']
        if ubicacion and apodo_ubicacion and estado_sensor:
            sensor = Sensor(ubicacion,apodo_ubicacion ,estado_sensor, "trisensor", id_paciente)
            db.session.add(sensor)
            db.session.commit()


            flash("Se ha agregado Trisensor correctamente", "success")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha ingresado todos los datos", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
    title = "Agregar Trisensor - Monitor"
    return render_template('agregar_trisensor.html', title=title, id_paciente=id_paciente)


@app.route('/trisensor/modificar/<int:idSensorTrisensor>', methods=['GET', 'POST'])
def pacientes_trisensor_modificar(idSensorTrisensor=None):

    id_sensor_trisensor = format(idSensorTrisensor)

    if request.method == 'POST':
        ubicacion = request.form['ubicacion']
        apodo_ubicacion = request.form['apodo_ubicacion']
        estado_sensor = request.form['estado_sensor']
        id_paciente = request.form['id_paciente']

        if ubicacion and apodo_ubicacion and estado_sensor and id_paciente:    
            trisensor = Sensor.query.get(id_sensor_trisensor)
            trisensor.ubicacion = ubicacion
            trisensor.apodo_ubicacion = apodo_ubicacion
            trisensor.estado = estado_sensor
            db.session.commit()

            flash("Se ha actualizado Trisensor correctamente ", "success")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha ingresado todos los datos", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))

    trisensor = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.id_paciente, Sensor.estado, Sensor.apodo_ubicacion).filter_by(idSensor = id_sensor_trisensor, tipo_sensor="trisensor").first()
    title = "Modificar Trisensor - Monitor"
    return render_template('modificar_trisensor.html', title=title, trisensor=trisensor)

@app.route('/trisensor/eliminar', methods=['POST'])
def pacientes_trisensor_eliminar():

    if request.method == 'POST':
        id_sensor_trisensor = request.form['id-sensor-trisensor']
        id_paciente = request.form['id-paciente']

        trisensor = Sensor.query.get(id_sensor_trisensor)
        db.session.delete(trisensor)
        db.session.commit()

        flash("Se ha eliminado Trisensor correctamente", "success")
        return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))


@app.route('/trisensor/cargar_datos', methods=['POST'])
@app.route('/trisensor/cargar_datos/<int:idSensorTrisensor>/<int:idPaciente>', methods=['GET'])
def cargar_datos_trisensor(idSensorTrisensor="null", idPaciente="null"):

    if request.method == 'POST':
        
        id_sensor = request.form['id_sensor']
        id_paciente = request.form['id-paciente']

        file = request.files['archivo']
        if file and id_sensor and id_paciente:
            tiempo_inicial = time()
            df_tri = pd.read_csv(file)
            df_tri = df_tri[["movimiento", "fecha_recibido", "id_ubicacion"]]
            trisensor_1_aux = []

            trisensor = Sensor.query.get(id_sensor)
            trisensor.disponible = 0
            db.session.commit()

            for i, j in df_tri.iterrows():
                helper = []
                fecha_recibido = datetime.strptime(j['fecha_recibido'], '%Y-%m-%d %H:%M:%S.%f')
                #ubicacion = j['id_ubicacion']
                movimiento = j['movimiento']
                db.engine.execute('INSERT INTO datos_sensor (fecha, presencia,  id_sensor) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE datos_sensor.presencia=%s', (fecha_recibido.strftime("%Y-%m-%d %H:%M:%S"), movimiento, id_sensor, movimiento))


            tiempo_final = time()
            tiempo_ejecucion = tiempo_final - tiempo_inicial

            flash("Datos del trisensor cargados correctamente. Tiempo de ejecución: " + str(tiempo_ejecucion), "success")
            
            trisensor = Sensor.query.get(id_sensor)
            trisensor.disponible = 1
            db.session.commit()

            print("Carga Ok!")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha rellenado todos los campos ", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))

    id_sensor_trisensor = format(idSensorTrisensor)
    id_paciente = format(idPaciente)

    paciente = Paciente.query.get(id_paciente)
    sensor = Sensor.query.filter_by(idSensor= id_sensor_trisensor, id_paciente = id_paciente, tipo_sensor="trisensor").first()
    
    if paciente is not None and sensor is not None:
        title = "Cargar Datos Trisensor"
        return render_template('cargar_datos_trisensor.html', title=title, id_sensor_trisensor=id_sensor_trisensor, id_paciente=id_paciente)
    else:
        flash("No existe paciente o sensor ", "error")
        return redirect(url_for("pacientes_inicio"))

###############################################################################################

@app.route('/pacientes/<int:idPaciente>/sensores/agregar_caidasensor', methods=['GET', 'POST'])
def pacientes_caidasensor_agregar(idPaciente=None):

    id_paciente = format(idPaciente)
    if request.method == 'POST':

        ubicacion = request.form['ubicacion']
        apodo_ubicacion = request.form['apodo_ubicacion']
        estado_sensor = request.form['estado_sensor']
        if ubicacion and apodo_ubicacion and estado_sensor:
            sensor = Sensor(ubicacion,apodo_ubicacion ,estado_sensor, "caidasensor", id_paciente)
            db.session.add(sensor)
            db.session.commit()

            flash("Se agrego Sensor de Caída correctamente ", "success")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha ingresado todos los datos", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))

    title = "Agregar Sensor de Caída - Monitor"
    return render_template('agregar_caidasensor.html', title=title, id_paciente=id_paciente)

@app.route('/sensor_caida/modificar/<int:idSensorCaida>', methods=['GET', 'POST'])
def pacientes_caidasensor_modificar(idSensorCaida=None):

    id_sensor_caida = format(idSensorCaida)

    if request.method == 'POST':
        ubicacion = request.form['ubicacion']
        apodo_ubicacion = request.form['apodo_ubicacion']
        id_paciente = request.form['id_paciente']
        estado_sensor = request.form['estado_sensor']
        if ubicacion and apodo_ubicacion and estado_sensor and id_paciente:
            caidasensor = Sensor.query.get(id_sensor_caida)
            caidasensor.ubicacion = ubicacion
            caidasensor.apodo_ubicacion = apodo_ubicacion
            caidasensor.estado = estado_sensor
            db.session.commit()

            flash("Se ha actualizado el Sensor de Caída correctamente", "success")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha ingresado todos los datos", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
    caidasensor = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.id_paciente, Sensor.estado, Sensor.apodo_ubicacion).filter_by(idSensor = id_sensor_caida, tipo_sensor="caidasensor").first()
    title = "Modificar Sensor de Caída - Monitor"
    return render_template('modificar_caidasensor.html', title=title, caidasensor=caidasensor)


@app.route('/sensor_caida/eliminar', methods=['POST'])
def pacientes_caidasensor_eliminar():

    if request.method == 'POST':
        id_sensor_caida = request.form['id-sensor-caida']
        id_paciente = request.form['id-paciente']

        caidasensor = Sensor.query.get(id_sensor_caida)
        db.session.delete(caidasensor)
        db.session.commit()

        flash("Se ha eliminado el Sensor de Caída correctamente ", "success")
        return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))


@app.route('/sensor_caida/generar_carga', methods=['POST'])
@app.route('/sensor_caida/generar_carga/<int:idSensorCaida>/<int:idPaciente>', methods=['GET'])
def generar_datos_caida_carga(idSensorCaida="null", idPaciente="null"):

    if request.method == 'POST':

        
        id_sensor_caida = request.form['id_sensor']
        id_paciente = request.form['id-paciente']
        fecha = request.form['fecha']
        hora_inicio = request.form['hora_inicio']

        if id_sensor_caida and id_paciente and fecha and hora_inicio:
            tiempo_inicial = time()
            """ caidasensor = Sensor.query.get(id_sensor_caida)
            caidasensor.disponible = 0
            db.session.commit() """
            #print(id_sensor_caida)
            print("sudocu")
            fecha_inicio = fecha+' '+hora_inicio+':00:00'
            fecha_termino = fecha+' '+hora_inicio+':59:59'
            filer = request.files['archivo']
            if not os.path.exists("momentaneo"):
                os.mkdir("momentaneo")
            nom = str(uuid.uuid4() )
            filer.save(os.path.join('momentaneo', nom ))
            directorio = os.path.join('momentaneo', nom )

            df2 = generar_carga_caidasensor.delay(fecha, fecha_inicio, fecha_termino, nom, id_sensor_caida)
            """ caidasensor = Sensor.query.get(id_sensor_caida)
            caidasensor.disponible = 1
            db.session.commit() """

            tiempo_final = time()
            tiempo_ejecucion = tiempo_final - tiempo_inicial
            flash("Datos del sensor caida cargados correctamente. Tiempo de Ejecución: " +str(tiempo_ejecucion), "success")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
        else:
            flash("No ha llenado todos los campos", "error")
            return redirect(url_for("pacientes_lista_sensores", idPaciente=id_paciente))
    id_sensor_caida = format(idSensorCaida)
    id_paciente = format(idPaciente)

    paciente = Paciente.query.get(id_paciente)
    sensor_caida = Sensor.query.filter_by(idSensor= id_sensor_caida, id_paciente = id_paciente, tipo_sensor="caidasensor").first()
    
    if paciente is not None and sensor_caida is not None:
        title = "Generar y carga de Datos Sensor de Caída - Monitor"
        return render_template('generar_datos_caida_carga.html', title=title, id_sensor_caida=id_sensor_caida, idPaciente=idPaciente)
    else:
        flash("No existe paciente o sensor ", "error")
        return redirect(url_for("pacientes_inicio"))


############################################################################################
############################################################################################
#########################################################################

# FILTRO FECHAS TODOS SENSORES POR PERSONA
@app.route('/ajax/filtrar_fechas', methods=['POST'])
def ajax_filtrar_fechas():

    fecha_inicio = request.form['fechaInicio']
    fecha_fin = request.form['fechaFin']
    id_paciente = request.form['idPaciente']

    ids_sensores = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.apodo_ubicacion).filter_by(id_paciente = id_paciente, tipo_sensor="trisensor").all()
    #print(ids_sensores)
    res_final_trisensor= []
    for id_trisensor in ids_sensores:

        if(int(id_trisensor[0]) > 0):

            # MADRUGADA
            res_madrugada = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "00:00:00" and "05:59:59" and id_sensor=%s GROUP by date(fecha)  ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_trisensor[0],))
            res_madrugada = res_madrugada.fetchall()
            cnt_res1 = len(res_madrugada)
            if cnt_res1 > 0:
                b = ( (np.array(res_madrugada)[:,1]) *6)/np.array(res_madrugada)[:,2]
                madrugada = {"media": round(np.mean(b), 2), "mediana": round(np.median(b),2), "DE": round(np.std(b), 2) , "max": round(np.max(b) ,2) , "min": round(np.min(b),2) }
            else:
                madrugada = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"} 

            #MANANA
            res_manana = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "06:00:00" and "11:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_trisensor[0],))
            res_manana = res_manana.fetchall()
            cnt_res2 = len(res_manana)

            if cnt_res2 > 0:
                b = ( (np.array(res_manana)[:,1]) *6)/np.array(res_manana)[:,2]
                manana = {"media": round(np.mean(b), 2), "mediana": round(np.median(b),2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                manana = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            # TARDE
            res_tarde = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "12:00:00" and "17:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_trisensor[0],))
            res_tarde = res_tarde.fetchall()
            cnt_res3 = len(res_tarde)
            if cnt_res3 > 0:
                b = ( (np.array(res_tarde)[:,1]) *6)/np.array(res_tarde)[:,2]
                tarde = {"media": round(np.mean(b), 2), "mediana": round(np.median(b), 2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                tarde = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            # NOCHE
            res_noche = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "18:00:00" and "23:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_trisensor[0],))
            res_noche = res_noche.fetchall()
            cnt_res4 = len(res_noche)
            if cnt_res4 > 0:
                b = ( (np.array(res_noche)[:,1]) *6)/np.array(res_noche)[:,2]
                noche = {"media": round(np.mean(b), 2), "mediana": round(np.median(b),2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                noche = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            if cnt_res1>0 or cnt_res2>0 or cnt_res3>0 or cnt_res4>0:
                res_final_trisensor.append({"tipo":"trisensor", "id_trisensor": id_trisensor[0], "ubicacion": id_trisensor[1], "apodo_ubicacion": id_trisensor[2]  ,  "madrugada": madrugada, "manana": manana, "tarde": tarde, "noche": noche})

            #res_final = json.dumps(resultado3, use_decimal=True, default=str)
            #print(res_final_trisensor) 
        else:
            res_final_trisensor= "{}"

    ids_sesores_caida = Sensor.query.with_entities(Sensor.idSensor, Sensor.ubicacion, Sensor.apodo_ubicacion).filter_by(id_paciente = id_paciente, tipo_sensor="caidasensor").all()

    #print(ids_sesores_caida)
    res_final_caidasensor = []
    for id_caidasensor in ids_sesores_caida:
        if(int(id_caidasensor[0]) > 0):
            #Madrugada
            res_madrugada = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "00:00:00" and "05:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_caidasensor[0],))
            res_madrugada = res_madrugada.fetchall()
            cnt_res1 = len(res_madrugada)

            if cnt_res1 > 0:
                b = ( (np.array(res_madrugada)[:,1]) *6)/np.array(res_madrugada)[:,2]
                madrugada = {"media": round(np.mean(b), 2), "mediana": round(np.median(b),2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                madrugada = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            # MANANA

            res_manana = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "06:00:00" and "11:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha))', (fecha_inicio, fecha_fin ,id_caidasensor[0],))
            res_manana = res_manana.fetchall()
            cnt_res2 = len(res_manana)

            if cnt_res2 > 0:
                b = ( (np.array(res_manana)[:,1]) *6)/np.array(res_manana)[:,2]
                manana = {"media": round(np.mean(b), 2), "mediana": round(np.median(b) , 2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                manana = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            # TARDE
            res_tarde = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "12:00:00" and "17:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha))', (fecha_inicio, fecha_fin ,id_caidasensor[0],))
            res_tarde = res_tarde.fetchall()
            cnt_res3 = len(res_tarde)

            if cnt_res3 > 0:
                b = ( (np.array(res_tarde)[:,1]) *6)/np.array(res_tarde)[:,2]
                tarde = {"media": round(np.mean(b), 2), "mediana": round(np.median(b),2), "DE": round(np.std(b), 2), "max":round(np.max(b) ,2) , "min": round(np.min(b),2)}
            else:
                tarde = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            # NOCHE
            res_noche = db.engine.execute('SELECT date(fecha), cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "18:00:00" and "23:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (date(fecha)) ', (fecha_inicio, fecha_fin ,id_caidasensor[0],))
            res_noche = res_noche.fetchall()
            cnt_res4 = len(res_noche)

            if cnt_res4 > 0:
                b = ( (np.array(res_noche)[:,1]) *6)/np.array(res_noche)[:,2]
                noche = {"media": round(np.mean(b), 2), "mediana": round(np.median(b), 2), "DE": round(np.std(b), 2), "max": round(np.max(b) ,2) , "min":  round(np.min(b),2)}
            else:
                noche = {"media": "0", "mediana": "0", "DE": "0" , "max":"0", "min":"0"}

            if cnt_res1>0 or cnt_res2>0 or cnt_res3>0 or cnt_res4>0:
                res_final_caidasensor.append({"tipo":"caidasensor", "id_caidasensor": id_caidasensor[0], "ubicacion":id_caidasensor[1], "apodo_ubicacion":id_caidasensor[2], "madrugada": madrugada, "manana": manana, "tarde": tarde, "noche": noche})

            #res_final = json.dumps(resultado3, use_decimal=True, default=str)
            
        else:
            res_final_caidasensor= "{}"
    return json.dumps( res_final_trisensor+res_final_caidasensor)


# DETALLES GRAFICO 
@app.route('/ajax/graficar/presencia_fecha/', methods=['POST'])
def ajax_trisensor_presencia_fecha():
    id_sensor = request.form['id_sensor']
    fechaInicio = request.form['fechaInicio']
    fechaFin = request.form['fechaFin']

    # MADRUGADA
    res_madrugada = db.engine.execute('SELECT date(fecha) as fecha, cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "00:00:00" and "05:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (fecha) ', (fechaInicio, fechaFin, id_sensor,))
    res_madrugada = res_madrugada.fetchall()
    cnt_res = len(res_madrugada)

    if cnt_res>0:
        c = (((np.array(res_madrugada)[:,1]) *6)/(np.array(res_madrugada)[:,2]) ).astype(np.float)
        c = np.around(c,2)
        fechas = (np.datetime_as_string(np.array(res_madrugada)[:,0].astype('datetime64[D]')))
        
        res_madrugada = np.stack( (  fechas ,  c ), axis=1).tolist()
    else:
        res_madrugada = []
    #b =   json.dumps( d.tolist() , use_decimal=True, default=str)

    # MANANA
    res_manana = db.engine.execute('SELECT date(fecha) as fecha, cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "06:00:00" and "11:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (fecha)', (fechaInicio, fechaFin,id_sensor,))
    res_manana = res_manana.fetchall()
    cnt_res = len(res_manana)

    if cnt_res>0:
        c = (((np.array(res_manana)[:,1]) *6)/np.array(res_manana)[:,2] ).astype(np.float)
        c = np.around(c,2)
        fechas = (np.datetime_as_string(np.array(res_manana)[:,0].astype('datetime64[D]')))
        res_manana2 = np.stack( (  fechas ,  c ), axis=1)
        res_manana = np.stack( (  fechas ,  c ), axis=1).tolist()
        print(res_manana2)
    else:
        res_manana=[]
    #b =   json.dumps( d.tolist() , use_decimal=True, default=str)

    # TARDE
    res_tarde = db.engine.execute('SELECT date(fecha) as fecha, cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "12:00:00" and "17:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (fecha) ', (fechaInicio, fechaFin,id_sensor,))
    res_tarde = res_tarde.fetchall()
    cnt_res = len(res_tarde)

    if cnt_res>0:
        c = (((np.array(res_tarde)[:,1]) *6)/np.array(res_tarde)[:,2] ).astype(np.float)
        c = np.around(c,2)
        fechas = (np.datetime_as_string(np.array(res_tarde)[:,0].astype('datetime64[D]')))
        
        res_tarde = np.stack( (  fechas ,  c ), axis=1).tolist()
    else:
        res_tarde=[]
    #b =   json.dumps( d.tolist() , use_decimal=True, default=str)

    # NOCHE
    res_noche = db.engine.execute('SELECT date(fecha) as fecha, cast(sum(if(presencia=1,1,0)) as UNSIGNED) as cantidad_unos , count(presencia) as cantidad_datos  FROM datos_sensor WHERE DATE(fecha) BETWEEN %s and %s and TIME(fecha) BETWEEN "18:00:00" and "23:59:59" and id_sensor=%s GROUP by date(fecha) ORDER BY (fecha) ', (fechaInicio, fechaFin,id_sensor,))
    res_noche = res_noche.fetchall()
    cnt_res = len(res_noche)

    if cnt_res>0:
        c = (((np.array(res_noche)[:,1]) *6)/np.array(res_noche)[:,2] ).astype(np.float)
        c = np.around(c,2)
        fechas = (np.datetime_as_string(np.array(res_noche)[:,0].astype('datetime64[D]')))
        
        res_noche = np.stack( (  fechas ,  c ), axis=1).tolist()
    else:
        res_noche = []
    #b =   json.dumps( d.tolist() , use_decimal=True, default=str)


    return {"madrugada": res_madrugada, "manana":res_manana , "tarde":res_tarde, "noche": res_noche }
    #return res_final


@app.route('/ajax/detalles', methods=['POST'])
def ajax_detalles():
    id_sensor = request.form['id_sensor']
    fechaInicio = request.form['fechaInicio']
    fechaFin = request.form['fechaFin']
    parte_dia = request.form['parte_dia']

    if parte_dia == "1":
        resultado = db.engine.execute('SELECT * FROM datos_sensor WHERE id_sensor=%s AND TIME(fecha) BETWEEN "00:00:00" AND "05:59:59" AND DATE(fecha) BETWEEN %s AND %s ', (id_sensor,fechaInicio,fechaFin ) )
        resultado = resultado.fetchall()
    elif parte_dia == "2":
        resultado = db.engine.execute('SELECT * FROM datos_sensor WHERE id_sensor=%s AND TIME(fecha) BETWEEN "06:00:00" AND "11:59:59" AND DATE(fecha) BETWEEN %s AND %s ', (id_sensor,fechaInicio,fechaFin) )
        resultado = resultado.fetchall()
    elif parte_dia == "3":
        resultado = db.engine.execute('SELECT * FROM datos_sensor WHERE id_sensor=%s AND TIME(fecha) BETWEEN "12:00:00" AND "17:59:59" AND DATE(fecha) BETWEEN %s AND %s ', (id_sensor,fechaInicio,fechaFin ) )
        resultado = resultado.fetchall()
    elif parte_dia == "4":
        resultado = db.engine.execute('SELECT * FROM datos_sensor WHERE id_sensor=%s AND TIME(fecha) BETWEEN "18:00:00" AND "23:59:59" AND DATE(fecha) BETWEEN %s AND %s ', (id_sensor,fechaInicio,fechaFin ) )
        resultado = resultado.fetchall()

    #res_final = json.dumps(resultado, use_decimal=True, default=str)
    res_final=[]
    for row in resultado:
        res_final.append(dict(row).copy())
    #print(res_final)
    res_final = json.dumps(res_final,  use_decimal=True, default=str)
    return res_final


db.init_app(app)

if __name__ == "__main__":
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        admin = Admin.query.get(1)
        if not admin:
            admin=Admin("monitorAdmin","monitorAdmin")
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0', port=8000)
    #app.run()
    #serve( app, host='0.0.0.0', port=8000, threads= 600)
    #app.run(debug=True, port=8000, use_reloader=True )