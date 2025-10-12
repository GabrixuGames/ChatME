import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { LogIn } from "lucide-react";

interface RegisterFormProps {
  onSubmit: (username: string, email: string, password: string) => void;
  error: string;
  isLoading: boolean;
  onBack?: () => void;
}

export default function RegisterForm({ onSubmit, error, isLoading, onBack }: RegisterFormProps) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(username, email, password);
  };

  return (
      <Card className="w-full max-w-md bg-sidebar text-white shadow-xl border-2 border-sidebar-accent rounded-xl animate-fadein">
      <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-extrabold text-center text-white">Registrarse</CardTitle>
          <CardDescription className="text-center text-sidebar-foreground opacity-80">
            Crea tu cuenta para empezar a chatear
          </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <div className="relative">
              <Input
                type="text"
                placeholder="Usuario"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                  className="pl-10 bg-white text-black focus:ring-2 focus:ring-sidebar-accent transition-all"
              />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sidebar-accent">
                  <LogIn className="h-5 w-5" />
                </span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="relative">
              <Input
                type="email"
                placeholder="Correo electrónico"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                  className="pl-10 bg-white text-black focus:ring-2 focus:ring-sidebar-accent transition-all"
              />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sidebar-accent">
                  <LogIn className="h-5 w-5" />
                </span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="relative">
              <Input
                type="password"
                placeholder="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                  className="pl-10 bg-white text-black focus:ring-2 focus:ring-sidebar-accent transition-all"
              />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sidebar-accent">
                  <LogIn className="h-5 w-5" />
                </span>
            </div>
          </div>
          {error && <div className="text-red-400 text-sm font-medium text-center">{error}</div>}
            <Button type="submit" className="w-full bg-sidebar-accent text-white font-bold text-lg py-2 rounded-lg transition-transform duration-150 hover:scale-105" disabled={isLoading}>
              {isLoading ? (
                <span className="flex items-center">
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                  Registrando...
                </span>
              ) : (
                <span className="flex items-center">
                  <LogIn className="mr-2 h-4 w-4" />
                  Registrarse
                </span>
              )}
            </Button>
            {onBack && (
              <Button
                type="button"
                className="w-full mt-2 bg-purple-100 text-purple-700 font-bold text-lg py-2 rounded-lg border border-purple-300 transition-transform duration-150 hover:scale-105"
                onClick={onBack}
              >
                Volver
              </Button>
            )}
        </form>
      </CardContent>
      <CardFooter className="flex justify-center"></CardFooter>
    </Card>
  );
}
