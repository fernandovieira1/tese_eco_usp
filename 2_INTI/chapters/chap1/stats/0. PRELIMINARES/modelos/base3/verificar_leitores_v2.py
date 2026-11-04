"""Confronto independente OOXML/openpyxl das 864 células usadas."""
import openpyxl
import construir_base3_v2 as b

xml={r.get('A'):r for r in b.planilha_xml(b.F/'pink_sheet_monthly_20260930.xlsx') if isinstance(r.get('A'),str)}
w=openpyxl.load_workbook(b.F/'pink_sheet_monthly_20260930.xlsx',read_only=True,data_only=True)
n=0
for r in w['Monthly Prices'].values:
    if isinstance(r[0],str) and len(r[0])==7 and r[0][4]=='M' and 2000<=int(r[0][:4])<=2023:
        for index,col in [(24,'Y'),(30,'AE'),(58,'BG')]:
            assert float(r[index])==float(xml[r[0]][col]);n+=1
assert n==864
b.js('verificacao_leitores_v2.json',{'leitores':['OOXML zipfile/ElementTree independente','openpyxl '+openpyxl.__version__],'celulas_identicas':n,'janela':'2000-01 a 2023-12','series':['Soybeans','Maize','DAP']})
print('864 células coincidentes')
