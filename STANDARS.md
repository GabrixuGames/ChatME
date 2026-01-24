# standards.md - Estándares Técnicos

## Nomenclatura

### Variables y Funciones
- **JavaScript/TypeScript**: camelCase
```javascript
  const userName = "John";
  function getUserData() {}
```
- **Python**: snake_case
```python
  user_name = "John"
  def get_user_data():
```
- **Constantes**: UPPER_SNAKE_CASE
```javascript
  const MAX_RETRY_ATTEMPTS = 3;
```
- **Clases/Componentes**: PascalCase
```javascript
  class UserProfile {}
  const UserCard = () => {}
```

### Archivos
- Componentes React: PascalCase (`UserProfile.jsx`)
- Utilidades: camelCase (`dateUtils.js`)
- Estilos: kebab-case (`user-profile.css`)
- Tests: mismo nombre + `.test` o `.spec`

### Git
- Branches: `feature/`, `bugfix/`, `hotfix/`, `release/`
  - Ejemplo: `feature/user-authentication`
- Commits: formato conventional commits
```
  feat: add user login functionality
  fix: resolve button alignment issue
  docs: update API documentation
  refactor: optimize database queries
  test: add unit tests for auth module
```

## Estructura de Proyecto

### Frontend (React/Vue)
```
src/
├── components/
│   ├── common/          # Componentes reutilizables
│   ├── layout/          # Layout components
│   └── features/        # Feature-specific components
├── pages/               # Page components
├── hooks/               # Custom hooks
├── utils/               # Funciones helper
├── services/            # API calls
├── store/               # State management
├── styles/              # Global styles
└── assets/              # Images, fonts, etc.
```

### Backend (Node/Python)
```
src/
├── controllers/         # Request handlers
├── models/              # Data models
├── services/            # Business logic
├── routes/              # API routes
├── middleware/          # Custom middleware
├── utils/               # Helper functions
├── config/              # Configuration files
└── tests/               # Test files
```

## Código

### Comentarios
```javascript
// ✅ BIEN: Explica el "por qué"
// Usamos debounce para evitar múltiples llamadas a la API
const debouncedSearch = debounce(search, 300);

// ❌ MAL: Explica el "qué" (obvio del código)
// Declara variable name
const name = "John";
```

### Funciones
- Máximo 50 líneas por función
- Una responsabilidad por función
- Nombres descriptivos (verbos para acciones)
```javascript
// ✅ BIEN
function calculateTotalPrice(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ MAL
function calc(x) {
  return x.reduce((a, b) => a + b.p, 0);
}
```

### Manejo de Errores
```javascript
// ✅ Frontend
try {
  const data = await fetchUserData(userId);
  return data;
} catch (error) {
  console.error('Error fetching user:', error);
  toast.error('Failed to load user data');
  return null;
}

// ✅ Backend
app.post('/api/users', async (req, res) => {
  try {
    const user = await createUser(req.body);
    res.status(201).json(user);
  } catch (error) {
    logger.error('Error creating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

### Async/Await vs Promises
- Preferir async/await sobre .then()
- Usar Promise.all() para operaciones paralelas
```javascript
// ✅ BIEN
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts()
]);

// ❌ Evitar (cuando sea posible)
fetchUsers().then(users => {
  fetchPosts().then(posts => {
    // ...
  });
});
```

## Estilos (CSS/SCSS)

### Metodología
- Usar BEM o CSS Modules
- Mobile-first approach
```css
/* BEM */
.user-card {}
.user-card__header {}
.user-card__header--highlighted {}

/* CSS Modules */
.container {}
.title {}
.button {}
```

### Variables
```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-error: #dc3545;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  
  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
}
```

## APIs

### REST Endpoints
```
GET    /api/users          # Lista todos
GET    /api/users/:id      # Obtiene uno
POST   /api/users          # Crea nuevo
PUT    /api/users/:id      # Actualiza completo
PATCH  /api/users/:id      # Actualiza parcial
DELETE /api/users/:id      # Elimina
```

### Respuestas
```javascript
// Success (200, 201)
{
  "data": { ... },
  "message": "User created successfully"
}

// Error (400, 404, 500)
{
  "error": "Validation failed",
  "details": ["Email is required", "Password too short"]
}
```

### Status Codes
- `200` OK - Operación exitosa
- `201` Created - Recurso creado
- `204` No Content - Eliminación exitosa
- `400` Bad Request - Error de validación
- `401` Unauthorized - No autenticado
- `403` Forbidden - No autorizado
- `404` Not Found - Recurso no encontrado
- `500` Internal Server Error - Error del servidor

## Testing

### Cobertura Mínima
- Funciones críticas: 100%
- Servicios/APIs: 80%
- Componentes: 70%
- Utilidades: 90%

### Tipos de Tests
```javascript
// Unit Test
describe('calculateTotal', () => {
  it('should sum array of numbers', () => {
    expect(calculateTotal([1, 2, 3])).toBe(6);
  });
});

// Integration Test
describe('User API', () => {
  it('should create and retrieve user', async () => {
    const user = await createUser({ name: 'John' });
    const retrieved = await getUser(user.id);
    expect(retrieved.name).toBe('John');
  });
});
```

## Seguridad

### Frontend
- Sanitizar inputs de usuario
- Validar datos antes de enviar
- No almacenar datos sensibles en localStorage
- Usar HTTPS siempre

### Backend
- Validar y sanitizar todos los inputs
- Usar prepared statements (SQL injection)
- Implementar rate limiting
- Hashear passwords (bcrypt, scrypt)
- Usar variables de entorno para secretos
```javascript
// ✅ BIEN
const hashedPassword = await bcrypt.hash(password, 10);

// ❌ MAL
const password = req.body.password; // Sin validación
db.query(`SELECT * FROM users WHERE id = ${userId}`); // SQL injection
```

## Performance

### Frontend
- Lazy loading de componentes
- Optimizar imágenes (WebP, lazy loading)
- Code splitting
- Memoización donde corresponda
```javascript
// React
const MemoizedComponent = React.memo(ExpensiveComponent);
const memoizedValue = useMemo(() => computeExpensive(a, b), [a, b]);
```

### Backend
- Implementar caching (Redis)
- Paginación en queries grandes
- Índices en base de datos
- Optimizar N+1 queries
```javascript
// ✅ BIEN: Una query con join
const users = await User.findAll({ include: [Posts] });

// ❌ MAL: N+1 queries
const users = await User.findAll();
users.forEach(async user => {
  user.posts = await Post.findAll({ where: { userId: user.id }});
});
```

## Accesibilidad (a11y)

### HTML Semántico
```html
<!-- ✅ BIEN -->
<nav>
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>

<!-- ❌ MAL -->
<div class="nav">
  <div class="link">Home</div>
</div>
```

### ARIA Labels
```jsx
<button aria-label="Close dialog" onClick={onClose}>
  <CloseIcon />
</button>

<input 
  type="text" 
  aria-describedby="email-help"
  aria-invalid={errors.email ? "true" : "false"}
/>
```

### Contraste y Tamaño
- Ratio de contraste mínimo: 4.5:1 (texto normal)
- Ratio de contraste mínimo: 3:1 (texto grande)
- Tamaño mínimo de elementos interactivos: 44x44px

## Versionado

### Semantic Versioning (SemVer)
```
MAJOR.MINOR.PATCH
1.0.0 → 1.0.1 (patch: bugfix)
1.0.1 → 1.1.0 (minor: nueva feature)
1.1.0 → 2.0.0 (major: breaking change)
```

### Changelog
```markdown
## [1.2.0] - 2024-01-24
### Added
- User profile page
- Email notifications

### Changed
- Improved dashboard performance

### Fixed
- Login redirect issue
```

## Documentación de Código

### JSDoc (JavaScript/TypeScript)
```javascript
/**
 * Calcula el precio total incluyendo impuestos
 * @param {number} price - Precio base
 * @param {number} taxRate - Tasa de impuesto (0.1 = 10%)
 * @returns {number} Precio total con impuestos
 * @throws {Error} Si el precio es negativo
 */
function calculateTotalPrice(price, taxRate) {
  if (price < 0) throw new Error('Price cannot be negative');
  return price * (1 + taxRate);
}
```

### Docstrings (Python)
```python
def calculate_total_price(price: float, tax_rate: float) -> float:
    """
    Calcula el precio total incluyendo impuestos.
    
    Args:
        price: Precio base
        tax_rate: Tasa de impuesto (0.1 = 10%)
    
    Returns:
        Precio total con impuestos
    
    Raises:
        ValueError: Si el precio es negativo
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    return price * (1 + tax_rate)
```
