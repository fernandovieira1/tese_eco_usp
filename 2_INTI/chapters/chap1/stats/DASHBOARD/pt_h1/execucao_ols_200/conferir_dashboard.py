from reproduzir import *
from streamlit.testing.v1 import AppTest

def main():
    checks=[]
    for mid in ['M001','M072','M101','M172']:
        target=json.loads((HERE/(mid+'.json')).read_text(encoding='utf-8'))
        spec=target['plan']['spec']
        at=AppTest.from_file(str(APP/'app.py'),default_timeout=90).run()
        at.radio(key='page').set_value('Laboratório OLS').run()
        at.selectbox(key='model_y').set_value(spec['y']).run()
        at.multiselect(key='model_xs').set_value(spec['xs']).run()
        at.selectbox(key='model_fe').set_value('none')
        at.selectbox(key='model_cov').set_value('cluster_entity')
        at.checkbox(key='model_require_y').check()
        for c in [spec['y'],*spec['xs']]:
            at.selectbox(key='transform_'+c).set_value(spec.get('transforms',{}).get(c,'level'))
            if c!=spec['y']:
                at.number_input(key='lag_'+c).set_value(spec.get('lags',{}).get(c,0))
        at.run()
        at.button(key='fit_ols').click().run()
        assert not at.exception, str([e.message for e in at.exception])
        assert not at.error, str([e.value for e in at.error])
        model=at.session_state['ols_model']; s=model['summary']
        assert s['N']==target['summary']['N']
        assert abs(s['R2']-target['summary']['R2'])<1e-12
        assert sample_id(model['sample'])==target['sample_id']
        coefficients=model['coefficients'].reset_index()
        delta=float(np.max(np.abs(coefficients['coef'].to_numpy()-np.array([v['coef'] for v in target['coef']]))))
        assert delta<1e-9
        checks.append({'id':mid,'method':'Streamlit AppTest executando app.py e acionando controles/Estimar OLS; sessão de teste independente do navegador localhost',
          'filters':FILTERS,'spec':model['spec'],'sample_id':sample_id(model['sample']),'N':s['N'],'R2':s['R2'],'adj':s['R2 ajustado'],
          'coef_max_abs_difference':delta,'metrics_displayed':[{ 'label':m.label,'value':m.value} for m in at.metric],
          'coefficients_displayed':at.dataframe[0].value.reset_index().to_dict('records'),
          'status':'conferido: amostra, N, R2, coeficientes, filtros, intercepto e ausência de FE idênticos'})
        dump(HERE/'conferencia_dashboard.json',clean(checks))
        print(f'{mid}: dashboard conferido, N={s["N"]}, R2={s["R2"]:.8f}',flush=True)

if __name__=='__main__': main()
