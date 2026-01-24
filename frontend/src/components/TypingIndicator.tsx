interface TypingIndicatorProps {
  usernames: string[];
}

export function TypingIndicator({ usernames }: TypingIndicatorProps) {
  if (usernames.length === 0) return null;

  const text = usernames.length === 1 
    ? `${usernames[0]} está escribiendo...`
    : usernames.length === 2
    ? `${usernames[0]} y ${usernames[1]} están escribiendo...`
    : `${usernames[0]} y ${usernames.length - 1} más están escribiendo...`;

  return (
    <div className="px-4 py-2 text-sm text-muted-foreground italic flex items-center gap-2">
      <span>{text}</span>
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
        <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
        <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
      </div>
    </div>
  );
}
