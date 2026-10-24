import React, { useState, useEffect } from 'react';
import { ArrowRight, ArrowLeft, RotateCcw, AlertTriangle, CheckCircle2 } from 'lucide-react';

/* INSTRUÇÕES PARA O DESENVOLVEDOR:
  1. Salve a foto real da ferida na pasta do projeto (ex: public/ ou src/assets/).
  2. Certifique-se de que o nome do arquivo seja 'image.png' (ou altere o caminho na variável abaixo).
*/
const CAMINHO_DA_FOTO = './image.png'; 

export default function GuiaCurativo() {
  const [step, setStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  // Reinicia a animação ao trocar de passo
  useEffect(() => {
    setIsPlaying(false);
    setTimeout(() => setIsPlaying(true), 50);
  }, [step]);

  const steps = [
    {
      title: "Passo 1: Lavar a Ferida",
      instrucoes: [
        "Jogue o Soro Fisiológico desenhando a letra Z sobre o machucado.",
        "Limpe a pele em volta puxando a sujeira para LONGE da parte escura.",
        "Seque APENAS a pele boa. NÃO seque a parte do machucado!"
      ],
      alerta: "Não esfregue a parte escura e nem a bolha d'água para não piorar o machucado."
    },
    {
      title: "Passo 2: Proteger em Volta",
      instrucoes: [
        "Passe um creme de proteção (óxido de zinco) apenas na pele boa, ao redor do machucado.",
        "A distância máxima do creme é de 2 dedos (2cm) da borda."
      ],
      alerta: "O creme funciona como um muro que impede a pele boa de assar ou machucar com o líquido da ferida."
    },
    {
      title: "Passo 3: Se usar POMADA",
      instrucoes: [
        "Coloque a pomada bem devagar APENAS no centro (na parte escura).",
        "Cubra com gazes secas até ficar na mesma altura da pele boa.",
        "Passe a atadura para prender tudo no lugar."
      ],
      alerta: "Nunca passe a pomada fora do centro da ferida. Não aperte o machucado."
    },
    {
      title: "Passo 4: Se usar PLACA",
      instrucoes: [
        "Se a placa puder ser cortada: corte no tamanho exato da parte escura.",
        "Se NÃO puder cortar: dobre as pontinhas para dentro.",
        "Coloque gazes por cima e passe a atadura."
      ],
      alerta: "A placa curativa NÃO deve encostar na pele boa, apenas na parte do machucado."
    }
  ];

  const nextStep = () => setStep((prev) => Math.min(prev + 1, steps.length - 1));
  const prevStep = () => setStep((prev) => Math.max(prev - 0, 0));
  const replayAnim = () => { setIsPlaying(false); setTimeout(() => setIsPlaying(true), 50); };

  return (
    <div className="min-h-screen bg-neutral-100 text-slate-900 font-sans flex flex-col">
      <style>{`
        @keyframes drawZ {
          0% { stroke-dashoffset: 900; opacity: 1; filter: drop-shadow(0 2px 2px rgba(0,150,255,0.5)); }
          70% { stroke-dashoffset: 0; opacity: 1; }
          90% { opacity: 0; }
          100% { stroke-dashoffset: 0; opacity: 0; }
        }
        @keyframes fadeInSlow { from { opacity: 0; } to { opacity: 0.95; } }
        @keyframes dropGel {
          0% { transform: scale(0.8) translateY(-20px); opacity: 0; }
          100% { transform: scale(1) translateY(0); opacity: 0.85; }
        }
        @keyframes placeGauze {
          0% { transform: translateY(-50px) rotate(-3deg); opacity: 0; }
          100% { transform: translateY(0) rotate(0deg); opacity: 0.98; }
        }
        @keyframes wrapBandage {
          0% { clip-path: polygon(0 0, 0 0, 0 100%, 0 100%); opacity: 0; }
          100% { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%); opacity: 1; }
        }
        
        .anim-z-spray { stroke-dasharray: 900; animation: drawZ 4s ease-in-out infinite; }
        .anim-fade { animation: fadeInSlow 1.5s forwards; opacity: 0; }
        .anim-gel { animation: dropGel 2s cubic-bezier(0.1, 0.8, 0.2, 1) forwards; opacity: 0; transform-origin: center;}
        .anim-gauze { animation: placeGauze 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards 1s; opacity: 0; }
        .anim-gauze-delay { animation: placeGauze 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards 0.5s; opacity: 0; }
        .anim-bandage-1 { animation: wrapBandage 1.5s ease-in-out forwards 2.5s; opacity: 0; }
        .anim-bandage-2 { animation: wrapBandage 1.5s ease-in-out forwards 3.2s; opacity: 0; }
      `}</style>

      {/* Cabeçalho Acessível e Simples */}
      <header className="bg-blue-800 text-white p-5 shadow-lg z-10 border-b-4 border-blue-400">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h1 className="text-3xl md:text-5xl font-black flex items-center gap-4">
            <span className="bg-white text-blue-800 p-2 rounded-2xl shadow-md text-3xl">🩹</span> 
            Guia Fácil de Curativo
          </h1>
          <div className="bg-blue-900 px-6 py-3 rounded-2xl font-black text-2xl border-2 border-blue-300 text-white shadow-inner">
            PASSO {step + 1} DE {steps.length}
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col lg:flex-row gap-8 mt-2">
        
        {/* LADO ESQUERDO: Imagem e Animações */}
        <div className="w-full lg:w-1/2 flex flex-col gap-4">
          
          <div className="bg-slate-200 rounded-[2rem] shadow-xl overflow-hidden relative flex items-center justify-center border-4 border-slate-300 min-h-[500px] lg:min-h-[600px]">
            
            {/* Botão de Repetir */}
            <button 
              onClick={replayAnim}
              className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm text-slate-800 px-5 py-3 rounded-2xl font-black text-lg shadow-lg flex items-center gap-2 hover:bg-white active:scale-95 border-2 border-slate-200 z-30 transition-all"
            >
              <RotateCcw size={24} strokeWidth={3} /> REPETIR
            </button>

            {/* SVG com as marcações exatas para a foto fornecida */}
            <svg viewBox="0 0 400 500" className="w-full h-full absolute inset-0 z-20">
              <defs>
                {/* Textura da gaze (curativo) */}
                <pattern id="gauze-pattern" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
                  <rect width="12" height="12" fill="#ffffff" />
                  <path d="M 12 0 L 0 0 0 12" fill="none" stroke="#e0e0e0" strokeWidth="2"/>
                  <path d="M 12 6 L 0 6 M 6 0 L 6 12" fill="none" stroke="#f5f5f5" strokeWidth="1"/>
                </pattern>

                {/* Formato externo: Contorno do creme (pasta sólida em volta) */}
                <path id="wound-contour" d="M140,230 C190,190 250,210 270,260 C290,320 280,370 210,390 C140,410 100,360 100,300 C100,260 120,240 140,230 Z" />
                
                {/* Formato interno: Apenas a crosta escura da ferida na foto */}
                <path id="wound-center" d="M150,265 C190,255 240,265 245,305 C250,345 230,365 190,365 C140,365 130,320 135,285 C138,275 145,268 150,265 Z" />
              </defs>

              {/* IMAGEM REAL CARREGADA DO SERVIDOR */}
              {/* Fallback de fundo escuro caso a imagem demore a carregar */}
              <rect width="400" height="500" fill="#1e293b" />
              
              <image 
                href={CAMINHO_DA_FOTO} 
                width="400" 
                height="500" 
                preserveAspectRatio="xMidYMid slice" 
              />

              {/* --- ANIMAÇÕES --- */}
              {step === 0 && isPlaying && (
                <g>
                  {/* Jato de Soro (Água limpa caindo em Z) */}
                  <path 
                    d="M90,100 L310,140 L110,240 L290,300 L90,400" 
                    stroke="#00ccff" 
                    strokeWidth="18" 
                    fill="none" 
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="anim-z-spray"
                  />
                  <circle cx="90" cy="100" r="14" fill="#0088ff" className="anim-z-spray" style={{ animationDuration: '4s' }}/>
                </g>
              )}

              {step >= 1 && (
                <g>
                  {/* Creme Branco SÓLIDO (sem sombra, parecendo pasta d'água) */}
                  <use 
                    href="#wound-contour" 
                    stroke="#f4f4f5" 
                    strokeWidth="20" 
                    fill="none" 
                    opacity="0.95" 
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className={step === 1 && isPlaying ? "anim-fade" : ""}
                  />
                </g>
              )}

              {step === 2 && isPlaying && (
                <g>
                  {/* Pomada preenchendo APENAS a crosta escura */}
                  <use href="#wound-center" fill="#38bdf8" opacity="0.85" className="anim-gel" />
                  
                  {/* Gazes brancas */}
                  <rect x="90" y="200" width="220" height="220" rx="20" fill="url(#gauze-pattern)" stroke="#ffffff" strokeWidth="8" className="anim-gauze drop-shadow-xl" />
                  
                  {/* Atadura cruzada */}
                  <path d="M-50,220 L450,250 L450,340 L-50,310 Z" fill="#f8f9fa" className="anim-bandage-1 drop-shadow-md" />
                  <path d="M-50,300 L450,330 L450,420 L-50,390 Z" fill="#f1f5f9" className="anim-bandage-2 drop-shadow-md" />
                </g>
              )}

              {step === 3 && isPlaying && (
                <g>
                  {/* Placa Amarelada (apenas no machucado escuro) */}
                  <use href="#wound-center" fill="#fef3c7" stroke="#fbbf24" strokeWidth="6" opacity="0.98" className="anim-gel" />
                  
                  {/* Gazes finas */}
                  <rect x="100" y="210" width="200" height="200" rx="15" fill="url(#gauze-pattern)" stroke="#ffffff" strokeWidth="4" className="anim-gauze-delay drop-shadow-md" />
                  
                  {/* Atadura cruzada */}
                  <path d="M-50,220 L450,250 L450,340 L-50,310 Z" fill="#f8f9fa" className="anim-bandage-1 drop-shadow-md" />
                  <path d="M-50,300 L450,330 L450,420 L-50,390 Z" fill="#f1f5f9" className="anim-bandage-2 drop-shadow-md" />
                </g>
              )}
            </svg>
          </div>
        </div>

        {/* LADO DIREITO: Textos Grandes e Fáceis */}
        <div className="w-full lg:w-1/2 flex flex-col justify-between gap-6">
          
          <div className="bg-white rounded-[2rem] shadow-xl border-2 border-slate-200 p-6 md:p-10 flex flex-col gap-6 flex-1">
            <h2 className="text-3xl md:text-5xl font-black text-slate-800 border-b-4 border-slate-200 pb-6 leading-tight">
              {steps[step].title}
            </h2>
            
            <ul className="space-y-6 mt-2">
              {steps[step].instrucoes.map((texto, i) => (
                <li key={i} className="flex gap-5 items-start text-2xl md:text-3xl text-slate-700 leading-snug font-bold">
                  <CheckCircle2 className="text-blue-600 mt-1 flex-shrink-0" size={40} strokeWidth={3} />
                  <span>{texto}</span>
                </li>
              ))}
            </ul>
            
            <div className="bg-amber-100 rounded-3xl p-6 md:p-8 border-l-[12px] border-amber-500 mt-auto flex items-start gap-5 shadow-sm">
              <AlertTriangle className="text-amber-600 flex-shrink-0 mt-1" size={52} strokeWidth={2.5} />
              <div>
                <p className="text-amber-900 font-black text-2xl md:text-3xl uppercase tracking-wider mb-2">Muito Importante</p>
                <p className="text-amber-900 text-xl md:text-2xl font-bold leading-snug">{steps[step].alerta}</p>
              </div>
            </div>
          </div>

          {/* Botões Grandes e Fáceis de Apertar */}
          <div className="grid grid-cols-2 gap-4 md:gap-6 mt-2">
            <button 
              onClick={prevStep}
              disabled={step === 0}
              className={`flex flex-col items-center justify-center py-6 md:py-8 rounded-[2rem] font-black text-2xl md:text-4xl uppercase transition-all ${
                step === 0 
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed border-4 border-slate-300' 
                  : 'bg-white text-slate-800 hover:bg-slate-50 active:scale-95 shadow-[0_8px_0_0_#cbd5e1] hover:translate-y-1 border-4 border-slate-300'
              }`}
            >
              <ArrowLeft size={48} className="mb-2" strokeWidth={3} /> Voltar
            </button>

            <button 
              onClick={nextStep}
              disabled={step === steps.length - 1}
              className={`flex flex-col items-center justify-center py-6 md:py-8 rounded-[2rem] font-black text-2xl md:text-4xl uppercase transition-all ${
                step === steps.length - 1
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed border-4 border-slate-300'
                  : 'bg-blue-600 text-white hover:bg-blue-500 active:scale-95 shadow-[0_8px_0_0_#1d4ed8] hover:translate-y-1 border-4 border-blue-700'
              }`}
            >
              <ArrowRight size={48} className="mb-2" strokeWidth={3} /> Próximo
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}