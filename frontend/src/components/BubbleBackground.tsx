import { useEffect, useRef } from "react";

export default function BubbleBackground() {
  const bubbleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = bubbleRef.current;
    if (!container) return;
    if (container.childNodes.length > 0) return; // No reiniciar burbujas
    const bubbles: HTMLDivElement[] = [];
    for (let i = 0; i < 18; i++) {
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.style.left = `${Math.random() * 100}%`;
      bubble.style.animationDuration = `${14 + Math.random() * 10}s`;
      bubble.style.opacity = `${0.3 + Math.random() * 0.5}`;
      bubble.style.width = bubble.style.height = `${18 + Math.random() * 32}px`;
      // Posición vertical aleatoria (de 0% a 80% de la pantalla)
      const startY = Math.random() * 80; // vh
      bubble.style.bottom = `calc(${startY}vh - 60px)`;
      bubbles.push(bubble);
      container.appendChild(bubble);
    }
    // No limpiar burbujas al desmontar para que persistan
  }, []);

  return (
    <>
      <div ref={bubbleRef} className="absolute inset-0 pointer-events-none z-0" />
      <style>{`
        .bubble {
          position: absolute;
          bottom: -60px;
          border-radius: 9999px;
          background: linear-gradient(135deg, #c4b5fd 60%, #a78bfa 100%);
          filter: blur(1px);
          animation: floatBubble linear infinite;
        }
        .dark .bubble {
          background: linear-gradient(135deg, #312e81 60%, #6d28d9 100%);
        }
        @keyframes floatBubble {
          0% { transform: translateY(0) scale(1); }
          80% { opacity: 1; }
          100% { transform: translateY(-110vh) scale(1.1); opacity: 0.2; }
        }
      `}</style>
    </>
  );
}
