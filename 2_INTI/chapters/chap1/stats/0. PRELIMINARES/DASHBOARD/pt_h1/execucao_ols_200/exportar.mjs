import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const destination=path.join(here,'..','RESULTADOS_DASH_H1.xlsx');
const payload=JSON.parse(await fs.readFile(path.join(here,'excel_payload.json'),'utf8'));
const wb=Workbook.create();
for (const [name,values] of Object.entries(payload)) {
  const sh=wb.worksheets.add(name);
  const rows=values.length,cols=values[0].length;
  const all=sh.getRangeByIndexes(0,0,rows,cols);
  all.values=values;
  all.format.font={name:'Arial',size:11,color:'#243247'};
  all.format.verticalAlignment='top';
  all.format.wrapText=true;
  all.format.columnWidth=24;
  sh.showGridLines=false;
  sh.freezePanes.freezeRows(1);
  const header=sh.getRangeByIndexes(0,0,1,cols);
  header.format={fill:'#203D56',font:{name:'Arial',size:11,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:48,verticalAlignment:'center'};
  const table=sh.tables.add(sh.getRangeByIndexes(0,0,rows,cols),true,'Tabela'+name.normalize('NFD').replace(/[\u0300-\u036f]/g,''));
  table.showFilterButton=true;
  if(name==='Resultados') {
    sh.tabColor='#203D56';
    sh.getRange('A:A').format.columnWidth=39;
    sh.getRange('B:B').format.columnWidth=116;
    sh.getRange('C:C').format.columnWidth=17;
    sh.getRange(`C2:C${rows}`).setNumberFormat('0.00000000');
    for(let i=1;i<rows;i++) {
      sh.getRangeByIndexes(i,0,1,cols).format.rowHeight=Math.max(34,Math.ceil(values[i][1].length/100)*16+8);
    }
  } else if(name==='Detalhes') {
    sh.getRange('A:A').format.columnWidth=39;
    sh.getRange('B:B').format.columnWidth=112;
    sh.getRange('C:C').format.columnWidth=14;
    for(const col of ['E','F','R','S','T','U','Y','Z','AA','AD','AE','AF','AG','AI','AL','AM','AN']) sh.getRange(`${col}:${col}`).format.columnWidth=80;
    sh.getRange(`I2:J${rows}`).setNumberFormat('0.00000000');
    sh.getRange(`K2:Q${rows}`).setNumberFormat('0');
    for(let i=1;i<rows;i++) {
      let lines=1;
      for(let j=0;j<cols;j++) {
        const width=j===1?98:([4,5,17,18,19,20,24,25,26,29,30,31,32,34,37,38,39].includes(j)?70:21);
        lines=Math.max(lines,Math.ceil(String(values[i][j]??'').length/width));
      }
      sh.getRangeByIndexes(i,0,1,cols).format.rowHeight=Math.min(400,Math.max(90,lines*15+10));
    }
  } else if(name==='Coeficientes') {
    sh.getRange('A:A').format.columnWidth=18;
    sh.getRange('B:B').format.columnWidth=105;
    sh.getRange('C:H').format.columnWidth=25;
    sh.getRange('I:I').format.columnWidth=54;
    sh.getRangeByIndexes(1,2,rows-1,6).setNumberFormat('0.0000000000;[Red]-0.0000000000;0.0000000000');
    sh.getRange(`F2:F${rows}`).setNumberFormat('0.00000000E+00');
    sh.getRangeByIndexes(1,0,rows-1,cols).format.rowHeight=46;
  } else {
    sh.tabColor='#8B9BA8';
    sh.getRange('A:A').format.columnWidth=26;
    sh.getRange('B:B').format.columnWidth=57;
    sh.getRange('C:C').format.columnWidth=145;
    sh.getRange('D:D').format.columnWidth=80;
    for(let i=1;i<rows;i++) {
      const lines=Math.max(...values[i].map((x,j)=>String(x).split('\n').reduce((sum,line)=>sum+Math.max(1,Math.ceil(line.length/[23,50,128,70][j])),0)));
      sh.getRangeByIndexes(i,0,1,cols).format.rowHeight=Math.min(409,Math.max(40,lines*15+10));
    }
  }
}
wb.recalculate();
await fs.mkdir(path.join(here,'previews'),{recursive:true});
for(const [name,range] of [['Resultados','A1:C5'],['Detalhes','A1:D3'],['Coeficientes','A1:D5'],['Metodologia','A1:C4']]) {
  const preview=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(here,'previews',name+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
try {
  await fs.access(destination);
  const stamp=new Date().toISOString().replace(/[:.]/g,'-');
  await fs.copyFile(destination,path.join(here,'..',`RESULTADOS_DASH_H1_backup_${stamp}.xlsx`));
} catch(e) {if(e.code!=='ENOENT') throw e;}
const out=await SpreadsheetFile.exportXlsx(wb);
await out.save(destination);
console.log('Excel salvo: '+destination);
