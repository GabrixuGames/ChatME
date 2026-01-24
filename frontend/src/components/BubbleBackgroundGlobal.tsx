import { useEffect, useRef } from "react";

let bubblesInitialized = false;

export default function BubbleBackgroundGlobal() {
  const bubbleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = bubbleRef.current;
    if (!container || bubblesInitialized) return;
    bubblesInitialized = true;
    const bubbles: HTMLDivElement[] = [];
    for (let i = 0; i < 18; i++) {
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.style.left = `${Math.random() * 100}%`;
      bubble.style.animationDuration = `${14 + Math.random() * 10}s`;
      bubble.style.opacity = `${0.3 + Math.random() * 0.5}`;
      bubble.style.width = bubble.style.height = `${18 + Math.random() * 32}px`;
      bubbles.push(bubble);
      container.appendChild(bubble);
    }
    // Las burbujas persisten mientras el componente esté montado
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
        @keyframes floatBubble {
          0% { transform: translateY(0) scale(1); }
          80% { opacity: 1; }
          100% { transform: translateY(-110vh) scale(1.1); opacity: 0.2; }
        }
      `}</style>
    </>
  );
}
