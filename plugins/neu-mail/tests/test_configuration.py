import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
configure=load('configure')
server=load('server')

class ConfigurationTests(unittest.TestCase):
    @unittest.skipUnless(os.name=='posix','POSIX credential storage')
    def test_private_atomic_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config/account.json'
            value={'host':'mail.example.edu','username':'student@example.edu','password':'TEST_ONLY_NOT_A_REAL_SECRET'}
            configure.save_account(path,value)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)
            with patch.object(server,'CONFIG',path):
                self.assertEqual(server.config(),value)
                path.chmod(0o644)
                with self.assertRaises(ValueError):server.config()
            self.assertEqual(list(path.parent.glob('.neu-mail-*')),[])

    @unittest.skipUnless(os.name=='posix','POSIX symlink handling')
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'original';target.write_text('unchanged')
            link=Path(tmp)/'account.json';link.symlink_to(target)
            with self.assertRaises(ValueError):configure.save_account(link,{})
            self.assertEqual(target.read_text(),'unchanged')

    def test_schema_rejected_before_network(self):
        with patch.object(server,'connection') as connect:
            for name,args in [('unknown',{}),('neu_mail_status',{'password':'irrelevant'}),('neu_mail_list_messages',{'limit':True}),('neu_mail_read',{})]:
                with self.assertRaises(ValueError):server.run(name,args)
            connect.assert_not_called()

    def test_errors_do_not_echo_server_text(self):
        marker='PRIVATE_SERVER_CONTENT'
        for exc in [ValueError(marker),server.imaplib.IMAP4.error(marker),OSError(marker)]:
            self.assertNotIn(marker,server.error_message(exc))

if __name__=='__main__':unittest.main()
