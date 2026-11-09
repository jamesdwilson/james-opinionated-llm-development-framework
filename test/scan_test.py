import unittest, tempfile, pathlib, subprocess, json, base64, io, zipfile, gzip
SCAN=pathlib.Path('scripts/bugsink/scan.py').resolve()
class ScanTest(unittest.TestCase):
 def scan(self,data,name='report.html'):
  with tempfile.TemporaryDirectory() as root:
   pathlib.Path(root,name).write_bytes(data)
   p=subprocess.run(['/usr/bin/python3',str(SCAN),root],input='["synthetic-canary-value"]',text=True,capture_output=True)
   return p.returncode,json.loads(p.stdout)
 def test_encodings(self):
  secret=b'synthetic-canary-value'; z=io.BytesIO()
  with zipfile.ZipFile(z,'w') as f:f.writestr('nested.gz',gzip.compress(secret))
  for data in [base64.b64encode(secret),b'"'+b''.join(('\\u%04x'%c).encode() for c in secret)+b'"',b'data:application/zip;base64,'+base64.b64encode(z.getvalue()),gzip.compress(secret)]:
   with self.subTest(data=len(data)):self.assertEqual(self.scan(data)[0],1)
 def test_tmp_not_exempt(self):
  with tempfile.TemporaryDirectory() as root:
   p=pathlib.Path(root,'.tmp');p.mkdir();(p/'copy').write_text('synthetic-canary-value')
   r=subprocess.run(['/usr/bin/python3',str(SCAN),root],input='["synthetic-canary-value"]',text=True,capture_output=True);self.assertEqual(r.returncode,1)
 def test_clean_and_bounds(self):
  self.assertEqual(self.scan(b'ordinary evidence')[0],0)
  self.assertEqual(self.scan(gzip.compress(b'x'*17000000))[0],1)
if __name__=='__main__':unittest.main()
