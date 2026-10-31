import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)Object.defineProperty(globalThis,'crypto',{value:webcrypto});
const {checkedExamples,examplesLoader}=await import('./tranche10-examples.js');
let input='';for await(const chunk of process.stdin)input+=chunk;
const value=JSON.parse(input);
assert.equal((await checkedExamples(value)).families.length,10);
for(const key of ['G4_accepted','completed_spark','general_ATC','user_accepted']) {
  await assert.rejects(checkedExamples({...value,[key]:true}));
}
const node=()=>({textContent:'',children:[],style:{},append(x){this.children.push(x);},replaceChildren(){this.children=[];}});
const output=node(),status=node();
const guide=fs.readFileSync(value.guide.path,'utf8');
const fetcher=async path=>path.includes('/source?')?{ok:true,text:async()=>guide}:{ok:true,json:async()=>value};
await examplesLoader(output,status,fetcher,node)();
assert.match(status.textContent,/pending acceptance/);
assert(output.children.some(x=>x.children.some(y=>y.textContent===guide)));
await examplesLoader(output,status,async()=>({ok:false}),node)();
assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
await examplesLoader(output,status,async path=>path.includes('/source?')?{ok:true,text:async()=>guide+'drift'}:{ok:true,json:async()=>value},node)();
assert.equal(output.children.length,0);assert.match(status.textContent,/identity mismatch/);
console.log('Example view: exact identity, guide rendering, overclaim and failure clearing passed.');
