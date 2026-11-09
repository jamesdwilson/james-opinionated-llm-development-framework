"""Bounded byte/encoding scan, never OCR or proof of visual secret absence.
Input values stay in memory; no matched bytes or paths are returned.
Runtime secret files are removed by orchestration BEFORE this finalized scan.
"""
import sys,json,pathlib,zipfile,re,io,gzip,base64
secrets=[s.encode() for s in json.load(sys.stdin)]
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.')
MAX=16*1024*1024; TOTAL=512*1024*1024; MEMBERS=10000; DEPTH=8
patterns=[re.compile(rb'https?://[a-f0-9]{32}(?::[^@\s]+)?@(?:127\.0\.0\.1|localhost|\[::1\])'),re.compile(rb'Bearer [a-f0-9]{40}')]
counts=dict(files=0,members=0,decoded=0,bytes=0,findings=0,limits=0,symlinks=0)
inventory=[]
def inspect(data,depth=0):
 counts['bytes']+=len(data)
 if len(data)>MAX or counts['bytes']>TOTAL or depth>DEPTH: raise ValueError()
 if any(s and s in data for s in secrets) or any(p.search(data) for p in patterns):counts['findings']+=1
 def child(value):
  counts['decoded']+=1
  if counts['decoded']>MEMBERS:raise ValueError()
  inspect(value,depth+1)
 if data.startswith(b'PK\x03\x04'):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for item in z.infolist():
    counts['members']+=1
    if counts['members']>MEMBERS or item.file_size>MAX:raise ValueError()
    if not item.is_dir():
     with z.open(item) as f:child(f.read(MAX+1))
 elif data.startswith(b'\x1f\x8b'):
  with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:child(f.read(MAX+1))
 else:
  # JSON strings and JS-style escaped strings; decode only defined escapes.
  for m in re.finditer(rb'"(?:[^"\\]|\\.)*"',data):
   if b'\\' in m[0]:
    try:
     v=json.loads(m[0]);child(v.encode())
    except (ValueError,UnicodeError):pass
  for m in re.finditer(rb'(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?',data):
   try:
    v=base64.b64decode(m[0],validate=True)
    if v and (v.startswith((b'PK',b'\x1f\x8b')) or all(c in b'\t\r\n' or 32<=c<127 for c in v)):child(v)
   except ValueError:pass
for path in sorted(root.rglob('*')):
 if any(p in ('node_modules','.git','__pycache__','npm-cache') for p in path.relative_to(root).parts):continue
 if path.is_symlink():counts['symlinks']+=1;counts['limits']+=1;continue
 if not path.is_file():continue
 counts['files']+=1
 # Only relative artifact names; generated runtime directories are prohibited here.
 inventory.append(str(path.relative_to(root)))
 try:
  with path.open('rb') as f:inspect(f.read(MAX+1))
 except Exception:counts['limits']+=1
result={**counts,'passed':counts['findings']==counts['limits']==0,'visualInspection':False,'scope':'bounded bytes, zip, gzip, base64 and JSON escapes; no OCR; unsupported binary formats not decoded','inventory':inventory}
print(json.dumps(result));sys.exit(0 if result['passed'] else 1)
