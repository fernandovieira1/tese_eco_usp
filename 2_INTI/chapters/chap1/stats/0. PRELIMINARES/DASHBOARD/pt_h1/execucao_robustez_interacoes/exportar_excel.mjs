import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const output=path.join(here,'..','RESULTADOS_DASH_H1_FE_ROBUSTEZ.xlsx');
const payload=JSON.parse(await fs.readFile(path.join(here,'excel_payload.json'),'utf8'));
const widths={
 'Robustez':[15,39,17,27,24,29,115,27,29,30,30,18,18,24,22,28,30,27,25,30,70,120],
 'Modelos':[24,18,39,37,29,18,20,20,25,24,24,30,24,23,70,110,100,135,150,120,45,150],
 'Coeficientes':[24,18,39,29,100,120,40,28,28,28,28,28,28,28,135],
 'Diagnósticos':[24,29,18,25,35,22,33,120,90,35,40,40,35,35,35,33,70,145],
 'Absorção':[25,39,100,120,48,35,110],
 'Metodologia':[30,65,145,100]
};
const wb=Workbook.create();
for(const [name,rows] of Object.entries(payload)){
 const sh=wb.worksheets.add(name);const n=rows.length,m=rows[0].length;
 const all=sh.getRangeByIndexes(0,0,n,m);all.values=rows;
 all.format.font={name:'Arial',size:11,color:'#243347'};all.format.wrapText=true;all.format.verticalAlignment='top';
 for(let j=0;j<m;j++)sh.getRangeByIndexes(0,j,n,1).format.columnWidth=widths[name][j];
 sh.getRangeByIndexes(0,0,1,m).format={fill:'#213E57',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:72,wrapText:true,verticalAlignment:'center'};
 sh.showGridLines=false;sh.freezePanes.freezeRows(1);
 const table=sh.tables.add(sh.getRangeByIndexes(0,0,n,m),true,'TabelaRobustez'+name.normalize('NFD').replace(/[\u0300-\u036f]/g,''));table.showFilterButton=true;
 for(let i=1;i<n;i++){
  let lines=1;
  for(let j=0;j<m;j++)if(typeof rows[i][j]==='string')lines=Math.max(lines,rows[i][j].split('\n').reduce((sum,x)=>sum+Math.max(1,Math.ceil(x.length/(widths[name][j]*0.92))),0));
  sh.getRangeByIndexes(i,0,1,m).format.rowHeight=Math.min(409,Math.max(name==='Robustez'?112:36,lines*16+8));
 }
 const fmt=(col,pattern)=>sh.getRange(`${col}2:${col}${n}`).setNumberFormat(pattern);
 if(name==='Robustez'){
  sh.tabColor='#213E57';for(const c of ['D','H','I','J','K'])fmt(c,'0.00000000E+00');
  for(const c of ['E','F'])fmt(c,'0.000000');for(const c of ['P','Q','R','S','T'])fmt(c,'0.00000000');
 }else if(name==='Modelos')for(const c of ['J','K','L'])fmt(c,'0.00000000');
 else if(name==='Coeficientes')for(const c of ['H','I','J','K','L','M','N'])fmt(c,'0.00000000E+00');
 else if(name==='Diagnósticos')for(const c of ['J','K','N','O'])fmt(c,'0.00000000E+00');
 else if(name==='Absorção')fmt('F','0.00000000E+00');
 else sh.tabColor='#8C9DA8';
}
wb.recalculate();await fs.mkdir(path.join(here,'previews'),{recursive:true});
for(const [sheet,range] of [['Robustez','A1:G5'],['Modelos','A1:F4'],['Coeficientes','A1:E4'],['Diagnósticos','A1:G4'],['Absorção','A1:E4'],['Metodologia','A1:C4']]){
 const preview=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
 await fs.writeFile(path.join(here,'previews',sheet+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
try{
 await fs.access(output);
 await fs.copyFile(output,path.join(here,'backup_'+new Date().toISOString().replace(/[:.]/g,'-')+'.xlsx'));
}catch(e){if(e.code!=='ENOENT')throw e;}
const result=await SpreadsheetFile.exportXlsx(wb);await result.save(output);
try{await fs.rename(output+'.inspect.ndjson',path.join(here,'export_inspect.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
console.log('Nova planilha salva: '+output);
