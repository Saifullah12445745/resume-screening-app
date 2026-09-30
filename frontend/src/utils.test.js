import test from 'node:test';
import assert from 'node:assert/strict';
import {validateFiles,toCSV,MAX_FILE_SIZE} from './utils.js';
test('file limits and types',()=>{
 assert.equal(validateFiles([{name:'resume.PDF',size:20}]),'');
 assert.ok(validateFiles([{name:'x.exe',size:20}]));
 assert.ok(validateFiles([{name:'x.txt',size:MAX_FILE_SIZE+1}]));
 assert.ok(validateFiles([{name:'x.txt',size:0}]));
});
test('CSV protects formulas, quotes names and excludes source text',()=>{
 const csv=toCSV([{id:'1',name:'=SUM(1,2)',text:'PRIVATE',coverage:50,semantic:null,matched:['python'],missing:['docker']}],['1']);
 assert.ok(csv.includes("'=SUM(1,2)"));assert.ok(csv.includes('"Yes"'));assert.ok(!csv.includes('PRIVATE'));
});
