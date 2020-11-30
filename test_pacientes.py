import unittest
from app import app
import io
unittest.TestLoader.sortTestMethodsUsing = None

class Testero(unittest.TestCase):
  def setUp(self):
    self.app = app
    self.client = self.app.test_client()

  def test1_agregar_paciente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      
      resp= c.post(path='/pacientes/agregar', data=dict(nombre_paciente="Paciente1", rut_paciente= "1234", mapa_imagen=(io.BytesIO(b"ASD"), "sudo.jpg" )), follow_redirects=True )
      self.assertEqual(resp.status_code,200)

  def test2_agregar_paciente_existente_rut(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/pacientes/agregar', data=dict(nombre_paciente="Paciente2RutCopiado", rut_paciente= "1234", mapa_imagen=(io.BytesIO(b"ASD"), "sudo.jpg")), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Paciente ya existe', resp.data)

  def test3_actualizar_paciente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/pacientes/actualizar/1', data=dict(nombre_paciente="Paciente1Modificado", rut_paciente= "12345", mapa_imagen=(io.BytesIO(b"ASD"), "sudo.jpg")), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Los datos del Paciente se ha actualizado con éxito'.encode(), resp.data)

  def test4_actualizar_paciente_no_existente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/pacientes/actualizar/9999', data=dict(nombre_paciente="Paciente1ModificadoNoExistente", rut_paciente= "99912345", mapa_imagen=(io.BytesIO(b"ASD"), "sudo.jpg")), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Paciente no existe', resp.data)

  def test5_eliminar_paciente_no_existente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/pacientes/eliminar', data={"id-paciente":"9999"}, follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Paciente no existe', resp.data)

  def test6_eliminar_paciente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/pacientes/eliminar', data={"id-paciente":"1"}, follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Se eliminó al Paciente correctamente'.encode(), resp.data)
      c.post(path='/pacientes/agregar', data=dict(nombre_paciente="Paciente2", rut_paciente= "987654", mapa_imagen=(io.BytesIO(b"ASD"), "sudo.jpg" ) ), follow_redirects=True )

if __name__ == '__main__':

  unittest.main()