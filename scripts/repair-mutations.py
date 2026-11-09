"""Controlled negative controls; restore every source even on failure."""
import pathlib,subprocess,json
cases=[('lifecycle','scripts/bugsink/lifecycle.mjs',"if(failure)throw failure;","if(false)throw failure;",['test/repair-lifecycle.test.mjs']),('identity','scripts/bugsink/lifecycle.mjs',"o.start=exec('/bin/ps'","o.start=exec('/bin/ps'",[]),('config','scripts/review-config.mjs'," && !Object.hasOwn(prescribed,key)"," && false",['test/review-config.test.mjs'])]
cases[1]=('identity','scripts/bugsink/lifecycle.mjs',"if(!owners.length)throw Error('Listener identity unavailable');","if(!owners.length)return {status:'absent',owners:[]};",['test/repair-lifecycle.test.mjs'])
results=[]
for name,file,old,new,tests in cases:
 p=pathlib.Path(file);original=p.read_text();assert old in original
 try:
  p.write_text(original.replace(old,new))
  with open('evidence/hostile-repair/mutation-red-'+name+'.log','w') as log:r=subprocess.run(['/opt/homebrew/bin/node','--test',*tests],stdout=log,stderr=subprocess.STDOUT)
  results.append(dict(name=name,command=['node','--test',*tests],exit=r.returncode));assert r.returncode!=0
 finally:p.write_text(original)
pathlib.Path('evidence/hostile-repair/mutation-exits.json').write_text(json.dumps(results,indent=2))
