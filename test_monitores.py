import unittest
from app import app
unittest.TestLoader.sortTestMethodsUsing = None

class Testero(unittest.TestCase):
  def setUp(self):
    self.app = app
    self.client = self.app.test_client()

  def test1_agregar_monitor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      
      resp= c.post(path='/admin/monitor/agregar', data=dict(nombre_monitor="monitorTester", usuario_monitor= "monitorTesterUsuario"), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Se ha agregado monitor correctamente', resp.data)

  def test2_agregar_monitor_existente_usuario(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      resp= c.post(path='/admin/monitor/agregar', data=dict(nombre_monitor="monitorTester2", usuario_monitor= "monitorTesterUsuario"), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Usuario monitor ya existe', resp.data)

  def test3_actualizar_monitor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      resp= c.post(path='/admin/monitor/modificar/1', data=dict(nombre_monitor="monitorTester2Modificado", usuario_monitor= "monitorTesterUsuarioModificado"), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Monitor actualizado correctamente'.encode(), resp.data)


  def test4_actualizar_monitor_no_existente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      resp= c.post(path='/admin/monitor/modificar/999', data=dict(nombre_monitor="monitorTester2NoExistente", usuario_monitor= "monitorTesterUsuarioNoExistente"), follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Monitor no existe', resp.data)


  def test5_eliminar_monitor_no_existente(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      resp= c.post(path='/admin/monitor/eliminar', data={'id-monitor':9999}, follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn(b'Monitor no existe', resp.data)

  def test6_eliminar_monitor(self):
    with self.client as c:
      with c.session_transaction() as sess:
        sess['id']='1'
        sess['usuario']='monitorAdmin'
        sess['tipo']='admin'
      resp= c.post(path='/admin/monitor/eliminar', data={'id-monitor':1}, follow_redirects=True )
      self.assertEqual(resp.status_code,200)
      self.assertIn('Se ha eliminado Monitor correctamente'.encode(), resp.data)
      c.post(path='/admin/monitor/agregar', data=dict(nombre_monitor="monitorTester", usuario_monitor= "monitorTesterUsuario"), follow_redirects=True )


if __name__ == '__main__':

  unittest.main()