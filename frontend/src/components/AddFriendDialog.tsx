import React, { useState, useEffect } from "react";
import axios from "axios";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { UserPlus, Search } from "lucide-react";
import { useFriends } from "@/contexts/FriendsContext";
import { useAuth } from "@/contexts/AuthContext";

export const AddFriendDialog: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { sendRequest } = useFriends();
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

  useEffect(() => {
    if (search.length < 3) {
      setResults([]);
      setError("");
      return;
    }
    setLoading(true);
    setError("");
    const timeout = setTimeout(async () => {
      try {
        console.log('🔍 Buscando usuarios con query:', search);
        console.log('🔑 Token disponible:', !!token);
        const res = await axios.get(`${API_URL}/friends/search?query=${encodeURIComponent(search)}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        console.log('✅ Resultados de búsqueda:', res.data);
        setResults(res.data.users || []);
        if (!res.data.users || res.data.users.length === 0) {
          setError("No se encontraron usuarios con ese nombre.");
        } else {
          setError("");
        }
      } catch (err: any) {
        console.error('❌ Error en búsqueda:', err.response?.data || err.message);
        setResults([]);
        setError(err.response?.data?.error || "Error al buscar usuarios. Verifica tu conexión.");
      } finally {
        setLoading(false);
      }
    }, 400);
    return () => clearTimeout(timeout);
  }, [search, API_URL]);

  const handleSendRequest = async (userId: string) => {
    await sendRequest(userId);
    setOpen(false);
    setSearch("");
    setResults([]);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-1 py-0.5 px-2 h-7 min-h-0 w-32 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-900 border border-green-200 rounded shadow-none text-xs"
        >
          <UserPlus className="h-3 w-3" /> Añadir amigo
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Buscar usuario</DialogTitle>
          <DialogDescription>Escribe el nombre para buscar y enviar solicitud de amistad.</DialogDescription>
        </DialogHeader>
        <div className="flex items-center gap-2 mt-2">
          <input
            type="text"
            className="border px-2 py-1 flex-1 rounded bg-background text-foreground placeholder:text-muted-foreground"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar usuario..."
            autoFocus
          />
          <Search className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="mt-4">
          {loading && <div className="text-sm text-muted-foreground">Buscando...</div>}
          {!loading && error && <div className="text-sm text-destructive">{error}</div>}
          {!loading && results.length > 0 && (
            <ul className="space-y-2">
              {results.map(user => (
                <li key={user.id} className="flex items-center justify-between px-2 py-1 bg-muted rounded">
                  <div className="flex items-center min-w-0 flex-1">
                    {user.profile_pic ? (
                      <img src={user.profile_pic} alt={user.username} className="w-7 h-7 rounded-full object-cover mr-2 border border-sidebar-border" />
                    ) : (
                      <div className="w-7 h-7 rounded-full bg-sidebar-accent text-white flex items-center justify-center mr-2 border border-sidebar-border">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className="truncate text-foreground text-left font-semibold">{user.username}</span>
                  </div>
                  <Button
                    size="sm"
                    className="ml-2 bg-sidebar-accent text-white transition-transform duration-150 hover:scale-105"
                    onClick={() => handleSendRequest(user.id)}
                  >
                    Enviar solicitud
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <DialogClose asChild>
          <Button variant="ghost" className="mt-4 w-full">Cerrar</Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
};
