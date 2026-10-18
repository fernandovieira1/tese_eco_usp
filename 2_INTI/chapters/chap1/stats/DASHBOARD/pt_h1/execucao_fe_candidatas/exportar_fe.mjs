import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const output=path.join(here,'..','RESULTADOS_DASH_H1_FE.xlsx');
const payload=JSON.parse(await fs.readFile(path.join(here,'excel_fe_payload.json'),'utf8'));
const wb=Workbook.create();
const widths={
 'Resultados':[15,39,15,20,20,25,105,22,20,21,24,24,28,29,90,90,25,25,25,25,70,95],
 'Comparação':[15,39,85,110,45,26,26,26,26,26,26,26,26,26,26,26,36,18,90],
 'Absorção':[15,39,85,110,48,75,24,24,28,30,18,90],
 'Detalhes':[18,15,39,35,16,22,16,22,23,23,26,26,22,22,22,70,140,90,80,80,85,75,40,65,80,25,75,150],
 'Coeficientes':[20,15,36,105,37,28,28,28,28,28,28,105],
 'Metodologia':[28,65,145,90]
};
for (const [name,rows] of Object.entries(payload)) {
 const sh=wb.worksheets.add(name);const n=rows.length,m=rows[0].length;
 const all=sh.getRangeByIndexes(0,0,n,m);all.values=rows;
 all.format.font={name:'Arial',size:11,color:'#20334A'};
 all.format.wrapText=true;all.format.verticalAlignment='top';
 for(let j=0;j<m;j++) sh.getRangeByIndexes(0,j,n,1).format.columnWidth=widths[name][j];
 sh.showGridLines=false;sh.freezePanes.freezeRows(1);
 sh.getRangeByIndexes(0,0,1,m).format={fill:'#213E57',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:66,wrapText:true,verticalAlignment:'center'};
 const table=sh.tables.add(sh.getRangeByIndexes(0,0,n,m),true,'TabelaFE'+name.normalize('NFD').replace(/[\u0300-\u036f]/g,''));
 table.showFilterButton=true;
 for(let i=1;i<n;i++) {
  let maxLines=1;
  for(let j=0;j<m;j++) {
   const value=rows[i][j];
   if(typeof value==='string') maxLines=Math.max(maxLines,value.split('\n').reduce((acc,line)=>acc+Math.max(1,Math.ceil(line.length/(widths[name][j]*0.92))),0));
  }
  sh.getRangeByIndexes(i,0,1,m).format.rowHeight=Math.min(409,Math.max(name==='Resultados'?95:36,maxLines*16+8));
 }
 const fmt=(col,format)=>sh.getRange(`${col}2:${col}${n}`).setNumberFormat(format);
 if(name==='Resultados'){
  sh.tabColor='#213E57';for(const col of ['D','E','F','J','K','L','M','N'])fmt(col,'0.00000000');
  for(const col of ['Q','R','S','T'])fmt(col,'0.00000000E+00');
 } else if(name==='Comparação'){
  for(const col of ['F','G','H','I','J','K','L','M','N','O','P'])fmt(col,'0.00000000E+00');
 } else if(name==='Absorção'){
  for(const col of ['I','J'])fmt(col,'0.00000000E+00');
 } else if(name==='Detalhes'){
  for(const col of ['I','J','K'])fmt(col,'0.00000000');fmt('L','0.00000000E+00');
 } else if(name==='Coeficientes'){
  for(const col of ['F','G','H','I','J','K'])fmt(col,'0.00000000E+00');
 } else sh.tabColor='#8A9DAA';
}
wb.recalculate();
await fs.mkdir(path.join(here,'previews'),{recursive:true});
for(const [sheet,range] of [['Resultados','A1:G4'],['Comparação','A1:F4'],['Absorção','A1:F4'],['Detalhes','A1:H4'],['Coeficientes','A1:F5'],['Metodologia','A1:C4']]){
 const preview=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
 await fs.writeFile(path.join(here,'previews',sheet+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
try{
 await fs.access(output);
 await fs.copyFile(output,path.join(here,'RESULTADOS_DASH_H1_FE_backup_'+new Date().toISOString().replace(/[:.]/g,'-')+'.xlsx'));
}catch(e){if(e.code!=='ENOENT')throw e;}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(output);
console.log('Novo Excel salvo: '+output);
const inspectFile=output+'.inspect.ndjson';
try{await fs.rename(inspectFile,path.join(here,'export_inspect.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
