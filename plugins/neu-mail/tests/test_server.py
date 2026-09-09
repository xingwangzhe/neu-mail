import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('server',P/'scripts/server.py'); s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class Tests(unittest.TestCase):
 def test_tls_modes(self):
  strict=s.tls_context({})
  self.assertTrue(strict.check_hostname)
  self.assertEqual(strict.verify_mode,s.ssl.CERT_REQUIRED)
  compatible=s.tls_context({'allow_hostname_mismatch':True})
  self.assertFalse(compatible.check_hostname)
  self.assertEqual(compatible.verify_mode,s.ssl.CERT_REQUIRED)
  with self.assertRaises(ValueError): s.tls_context({'allow_hostname_mismatch':'false'})

 def test_status_accepts_string_capabilities(self):
  from contextlib import contextmanager
  class Client:
   capabilities=('IMAP4REV1', b'ID')
  @contextmanager
  def connect(): yield Client()
  with patch.object(s,'connection',connect), patch.object(s,'tls_status',return_value={}):
   self.assertEqual(s.run('neu_mail_status',{})['capabilities'],['IMAP4REV1','ID'])
 def test_folder(self):
  self.assertEqual(s.parse_folder(b'(\\Sent) "/" "Sent Items"')['id'],'Sent Items')
  self.assertEqual(s.decode_folder('&ZeVnLIqe-'),'日本語')
 def test_quote(self):
  with self.assertRaises(ValueError): s.quote('INBOX\r\nLOGOUT')
 def test_read_preserves_state(self):
  class Client:
   def select(self,f,readonly):
    assert readonly is True
    return 'OK',[b'1']
   def response(self,_): return 'UIDVALIDITY',[b'123']
   def uid(self,cmd,uid,query):
    assert cmd=='FETCH'
    if query=='(RFC822.SIZE)': return 'OK',[b'1 (RFC822.SIZE 90)']
    assert 'BODY.PEEK[]' in query
    return 'OK',[(b'1',b'Subject: Test\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nHello')]
  from contextlib import contextmanager
  @contextmanager
  def connect(): yield Client()
  with patch.object(s,'connection',connect):
   result=s.run('neu_mail_read',{'folder':'INBOX','uid':'1','uidvalidity':'123'})
   self.assertEqual(result['body'][0]['content'],'Hello')
   with self.assertRaises(ValueError): s.run('neu_mail_read',{'folder':'INBOX','uid':'1','uidvalidity':'122'})
 def test_mcp(self):
  requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'}]
  out=subprocess.run([sys.executable,str(P/'scripts/server.py')],input='\n'.join(map(json.dumps,requests))+'\n',capture_output=True,text=True,check=True)
  lines=list(map(json.loads,out.stdout.splitlines()))
  self.assertEqual(len(lines),2);self.assertEqual(len(lines[1]['result']['tools']),4)
if __name__=='__main__': unittest.main()
