import unittest
from app import app
unittest.TestLoader.sortTestMethodsUsing = None

class Testero(unittest.TestCase):
  def setUp(self):
    self.app = app
    self.client = self.app.test_client()

  def test1_agregar_trisensor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      
      resp= c.post(path='/pacientes/2/sensores/agregar_trisensor', data=dict(ubicacion="1", apodo_ubicacion= "Dormitorio1", estado_sensor="activo"), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Se ha agregado Trisensor correctamente'.encode(), resp.data)

  def test2_modificar_trisensor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/trisensor/modificar/1', data=dict(ubicacion="2", apodo_ubicacion= "Dormitorio1Modificado", estado_sensor="desactivado", id_paciente=2), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Se ha actualizado Trisensor correctamente'.encode(), resp.data)


  def test3_eliminar_trisensor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='2'
        sess['usuario']='monitorTesterUsuario'
        sess['tipo']='monitor'
      resp= c.post(path='/trisensor/eliminar', data={"id-sensor-trisensor":"1", "id-paciente":2}, follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Se ha eliminado Trisensor correctamente'.encode(), resp.data)
      c.post(path='/pacientes/2/sensores/agregar_trisensor', data=dict(ubicacion="4", apodo_ubicacion= "Cocina", estado_sensor="activo"), follow_redirects=True )
if __name__ == '__main__':

  unittest.main()