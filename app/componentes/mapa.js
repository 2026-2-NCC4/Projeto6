export default function(component) {
  const {data, parentElement, setTriggerValue} = component;
  const root = parentElement.querySelector('.fs-map');
  if (!root || !data) return;
  const $ = (s) => root.querySelector(s);
  const controller = new AbortController();
  const listen = (el, event, fn) => el.addEventListener(event, fn, {signal:controller.signal});
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const frames = new Map();
  let active = 'margem';
  let discount = Number(data.hipoteses.desconto);
  let cost = Number(data.hipoteses.custo);
  const applied = {discount, cost};
  const valid = v => typeof v === 'number' && Number.isFinite(v);
  const num = (v,digits=2) => {
    const text=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(v);
    return /^-0(?:,0+)?$/.test(text)?text.slice(1):text;
  };
  const short = v => !valid(v) ? 'Indisponível' : 'R$ '+num(v/(Math.abs(v)>=1e9?1e9:1e6))+(Math.abs(v)>=1e9?' bi':' mi');
  const millions = v => valid(v) ? num(v/1e6) : 'Indisponível';
  const signed = v => (v>0?'+':'')+num(v);
  const original = data.valores;
  const names = {receita:'Receita',custos:'Custos',margem:'Margem após custos',resultado:'Resultado líquido',caixa:'Geração de caixa'};
  const order = Object.keys(names);
  const descriptions = {
    receita:'Receita média da população selecionada. O desconto reduz somente esta referência, mantendo o volume constante.',
    custos:'Custos apresentados em módulo. A simulação aplica a variação sobre o custo assinado da base.',
    margem:'Parcela da receita que sobra após os custos. Exclui tributos e demais despesas; não equivale ao lucro líquido.',
    resultado:'Resultado líquido informado na DRE. Reúne outras parcelas contábeis e permanece na referência durante esta simulação.',
    caixa:'Geração de caixa informada no fluxo financeiro. Não equivale a lucro ou EBITDA e permanece na referência durante esta simulação.'
  };
  const formulas = {
    receita:'Receita simulada = receita × (1 − desconto).',
    custos:'Custo simulado = custo assinado × (1 + variação). O cartão exibe o módulo.',
    margem:'Margem = receita simulada + custo assinado simulado.',
    resultado:'Fonte: DRE · Resultado Líquido. A linha mostra as médias anuais do recorte.',
    caixa:'Fonte: FLU · Geração de Caixa. Valores negativos indicam saída líquida de caixa na projeção.'
  };
  function values() {
    if(!canSimulate) return {...original};
    const r = valid(original.receita) ? original.receita*(1-discount/100) : null;
    const c = valid(original.custos) ? original.custos*(1+cost/100) : null;
    return {receita:r,custos:c,margem:valid(r)&&valid(c)?r+c:null,resultado:original.resultado,caixa:original.caixa};
  }
  function displayValue(key,v) {return key==='custos' && valid(v) ? -v : v;}
  function animate(el, value, format, immediate=false) {
    if(frames.has(el)) cancelAnimationFrame(frames.get(el));
    const old = Number(el.dataset.current);
    el.dataset.current = String(value);
    if(reduced || immediate || !valid(value) || !Number.isFinite(old) || !el.textContent) {
      el.textContent = format(value); return;
    }
    const start = performance.now();
    function step(t) {
      const x = Math.min(1,(t-start)/190);
      el.textContent = format(old+(value-old)*(1-Math.pow(1-x,3)));
      if(x<1)frames.set(el,requestAnimationFrame(step));else frames.delete(el);
    }
    frames.set(el,requestAnimationFrame(step));
  }
  function chart() {
    const raw = data.series[active].map(v=>displayValue(active,v));
    const validValues = raw.filter(valid);
    const svg = $('.trend');
    if(!validValues.length){svg.replaceChildren();svg.setAttribute('aria-label','Série indisponível');return;}
    const low = Math.min(...validValues), high = Math.max(...validValues);
    const pad = (high-low)*.15 || Math.max(Math.abs(high)*.05,1);
    const min=low-pad, max=high+pad;
    const x=i=>10+(raw.length>1?i/(raw.length-1):.5)*280;
    const y=v=>80-(v-min)/(max-min)*64;
    let path='',drawing=false;
    raw.forEach((v,i)=>{if(valid(v)){path+=(drawing?' L':' M')+x(i).toFixed(2)+' '+y(v).toFixed(2);drawing=true;}else drawing=false;});
    const selected = data.anos.indexOf(data.ano);
    const zero = min<=0 && max>=0 ? `<path d="M10 ${y(0)}H290" stroke="#a8beca" stroke-dasharray="3 4"/>` : '';
    const circle = valid(raw[selected]) ? `<circle cx="${x(selected)}" cy="${y(raw[selected])}" r="4.5" fill="#007bb6" stroke="white" stroke-width="2"/>` : '';
    // HTML de origem estática; as coordenadas interpoladas são somente números finitos.
    svg.innerHTML = `<path d="M10 86H290" stroke="#dbe6ed"/>${zero}<path d="${path}" fill="none" stroke="#007bb6" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>${circle}`;
    svg.setAttribute('aria-label',`Referência de ${names[active]}, Anos ${data.anos[0]} a ${data.anos.at(-1)}, em milhões de reais. Ano ${data.ano}: ${millions(raw[selected])}.`);
    $('.first-year').textContent='Ano '+data.anos[0];
    $('.last-year').textContent='Ano '+data.anos.at(-1);
  }
  function render(selectionChanged=false) {
    const v=values();
    const changed = discount!==0 || cost!==0;
    const pending = discount!==applied.discount || cost!==applied.cost;
    const related = {margem:['receita','custos','margem'],receita:['receita','margem'],custos:['custos','margem'],resultado:['resultado'],caixa:['caixa']}[active];
    root.querySelectorAll('[data-node]').forEach(node=>{
      const k=node.dataset.node;
      node.classList.toggle('selected',k===active);
      node.classList.toggle('is-muted',!related.includes(k));
      node.setAttribute('aria-pressed',String(k===active));
      node.querySelector('.node-tag').textContent=k===active?'EM FOCO':String(order.indexOf(k)+1).padStart(2,'0');
      animate(node.querySelector('.node-value'),displayValue(k,v[k]),short);
      node.setAttribute('aria-label',names[k]+', '+short(displayValue(k,v[k]))+'. Explorar indicador.');
      if(['receita','custos'].includes(k)) node.querySelector('.node-kind').textContent=changed?'Hipótese simulada':(k==='custos'?'Referência · em módulo':'Referência');
      if(k==='margem')node.querySelector('.node-kind').textContent=changed?'Hipótese · receita − custos':'Receita − custos';
    });
    $('.detail-title').textContent=names[active];
    $('.detail-number').textContent=String(order.indexOf(active)+1).padStart(2,'0')+' / 05';
    animate($('.detail-value'),displayValue(active,v[active]),millions,selectionChanged);
    $('.detail-description').textContent=descriptions[active];
    $('.formula-note').textContent=formulas[active];
    if(['resultado','caixa'].includes(active)) {
      $('.change-value').textContent='Referência preservada';
      $('.change-label').textContent='não recalculada pela simulação';
    } else {
      const delta=displayValue(active,v[active])-displayValue(active,original[active]);
      $('.change-value').textContent=valid(delta)?signed(delta/1e6)+' mi':'';
      $('.change-label').textContent='em relação à referência';
    }
    $('.discount-output').textContent=num(discount,1)+'%';
    $('.cost-output').textContent=(cost>0?'+':'')+num(cost,1)+'%';
    $('.preview-status').textContent=pending?'Prévia · não aplicada':(changed?'Hipótese aplicada':'Referência');
    $('.preview-status').classList.toggle('pending',pending);
    $('.apply').disabled = !pending || !canSimulate;
    $('.live-note').textContent=valid(v.margem)?`Margem de ${short(original.margem)} para ${short(v.margem)}.`:'Simulação indisponível para esta referência.';
    $('.formula-edge').style.stroke=['margem','receita','custos'].includes(active)?'#007bb6':'#cad8e0';
    chart();
  }
  const canSimulate=valid(original.receita)&&original.receita>=0&&valid(original.custos)&&original.custos<=0;
  $('.context').textContent=`Ano ${data.ano} · ${num(data.cenarios,0)} ${data.populacao==='sem_copias'?'trajetórias únicas':'cenários'} · médias anuais`;
  $('.source-label').textContent=data.modo==='ficticio'?'Dados fictícios · demonstração':(data.modo==='sem_origem'?'Origem sem conferência E1':'Projeções CTI');
  $('.terminal-note').textContent=data.ano===12?'Ano 12 · encerramento; comparar com cautela.':'';
  root.querySelectorAll('[data-node]').forEach(node=>{
    listen(node,'click',()=>{active=node.dataset.node;render(true);$('.screen-reader').textContent=names[active]+'. '+$('.detail-value').textContent+' milhões de reais. '+descriptions[active];});
  });
  $('.discount').value=String(discount);$('.cost').value=String(cost);
  $('.discount').disabled=!canSimulate;$('.cost').disabled=!canSimulate;
  listen($('.discount'),'input',e=>{discount=Number(e.target.value);render();});
  listen($('.cost'),'input',e=>{cost=Number(e.target.value);render();});
  listen($('.reset'),'click',()=>{discount=0;cost=0;$('.discount').value='0';$('.cost').value='0';render();});
  listen($('.apply'),'click',()=>{
    if(!canSimulate)return;
    $('.apply').disabled=true;
    setTriggerValue('aplicar',{ano:data.ano,populacao:data.populacao,desconto:discount,custo:cost});
  });
  const presentationButton=$('.presentation');
  let wasPresenting=false;
  const presenting=()=>root.matches(':fullscreen')||root.classList.contains('wide');
  function presentationLabel() {
    const enabled=presenting();
    presentationButton.querySelector('span').textContent=enabled?'Sair':'Apresentar';
    presentationButton.setAttribute('aria-label',enabled?'Sair do modo de apresentação':'Ampliar mapa para apresentação');
    presentationButton.setAttribute('aria-expanded',String(enabled));
    if(enabled){root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');}
    else {root.removeAttribute('role');root.removeAttribute('aria-modal');}
    if(wasPresenting&&!enabled)presentationButton.focus({preventScroll:true});
    wasPresenting=enabled;
  }
  listen(presentationButton,'click',async()=>{
    if(root.matches(':fullscreen'))await document.exitFullscreen();
    else if(root.classList.contains('wide'))root.classList.remove('wide');
    else if(root.requestFullscreen){try{await root.requestFullscreen();}catch{root.classList.add('wide');}}
    else root.classList.add('wide');
    presentationLabel();
  });
  listen(document,'fullscreenchange',presentationLabel);
  listen(document,'keydown',async e=>{
    if(e.key!=='Escape'||!presenting())return;
    e.preventDefault();
    if(root.matches(':fullscreen')){
      try{await document.exitFullscreen();}catch{/* O navegador pode ter saído pelo comando nativo. */}
    }
    root.classList.remove('wide');presentationLabel();
  });
  listen(root,'keydown',e=>{
    if(e.key!=='Tab'||!presenting())return;
    const controls=[...root.querySelectorAll('button:not(:disabled),input:not(:disabled)')];
    const first=controls[0],last=controls.at(-1);
    const activeElement=root.getRootNode().activeElement;
    if(e.shiftKey&&activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey&&activeElement===last){e.preventDefault();first.focus();}
  });
  presentationLabel();
  render(true);
  return ()=>{controller.abort();root.classList.remove('wide');frames.forEach(id=>cancelAnimationFrame(id));};
}
