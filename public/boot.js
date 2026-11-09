import { installMonitoring } from './monitoring.js';
const config=await (await fetch('/monitoring-config',{credentials:'omit'})).json();
installMonitoring(config);
await import('./app.js');
if(config.testCanary && new URLSearchParams(location.search).get('canary')==='1') {
  document.querySelector('#notice').textContent='The test error was contained. You can continue creating tasks.';
  setTimeout(()=>{const error=new Error('Isolated lab canary');error.name='LabCanaryError';throw error;},0);
}
