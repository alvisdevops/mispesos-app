# MisPesos Frontend

Dashboard web para gestión de gastos personales con autenticación de Telegram.

## Características

- **Autenticación con Telegram**: Login seguro usando Telegram Login Widget
- **Dashboard Interactivo**: Visualizaciones con gráficos de gastos por categoría, método de pago y tendencias diarias
- **Gestión de Transacciones**: Lista completa con filtros avanzados, edición y eliminación
- **Creación Manual**: Formulario para agregar transacciones directamente desde el web
- **Vista Multi-usuario (Admin)**: Visualización y análisis de datos de todos los usuarios
- **Responsive Design**: Interfaz adaptable a diferentes dispositivos

## Stack Tecnológico

- **React 18** - Framework UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **TanStack Query (React Query)** - Gestión de estado del servidor
- **Recharts** - Gráficos y visualizaciones
- **Tailwind CSS** - Estilos utility-first
- **React Router v6** - Navegación
- **Axios** - Cliente HTTP

## Desarrollo Local

### Requisitos

- Node.js 18+ y npm
- Backend de MisPesos corriendo en `http://localhost:8000`

### Instalación

```bash
cd frontend
npm install
```

### Configuración

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Configura las variables:

```env
VITE_API_URL=http://localhost:8000
VITE_TELEGRAM_BOT_NAME=MisPesosBot
VITE_ADMIN_USER_ID=123456789  # Opcional: tu Telegram User ID para acceso admin
```

### Iniciar servidor de desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

### Build para producción

```bash
npm run build
```

Los archivos compilados estarán en `dist/`

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── auth/           # TelegramLogin, ProtectedRoute
│   │   ├── dashboard/      # StatsCard, CategoryChart, DailyChart
│   │   ├── transactions/   # TransactionList, TransactionFilters, TransactionForm
│   │   ├── layout/         # Header, Sidebar, Layout
│   │   └── common/         # Componentes compartidos
│   ├── pages/              # Páginas principales
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Transactions.tsx
│   │   ├── NewTransaction.tsx
│   │   └── AdminView.tsx
│   ├── services/           # Servicios API
│   │   ├── api.ts          # Cliente Axios configurado
│   │   ├── transactions.ts # Servicios de transacciones
│   │   └── categories.ts   # Servicios de categorías
│   ├── contexts/           # React Contexts
│   │   └── AuthContext.tsx # Contexto de autenticación
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── App.tsx             # Componente raíz
│   └── main.tsx            # Entry point
├── Dockerfile              # Imagen para producción
├── nginx.conf              # Configuración Nginx
└── package.json
```

## Despliegue con Docker

### Build de la imagen

```bash
docker build -t mispesos-frontend \
  --build-arg VITE_API_URL=http://localhost:8000 \
  --build-arg VITE_TELEGRAM_BOT_NAME=MisPesosBot \
  --build-arg VITE_ADMIN_USER_ID=123456789 \
  .
```

### Ejecutar contenedor

```bash
docker run -d \
  -p 80:80 \
  --name mispesos-frontend \
  mispesos-frontend
```

### Con Docker Compose

El frontend ya está incluido en `docker-compose.yml` del proyecto principal:

```bash
# Desde el root del proyecto
docker compose up -d frontend
```

## Características por Página

### Login (`/login`)
- Autenticación con Telegram Login Widget
- Redirección automática si ya está autenticado
- Link directo al bot de Telegram

### Dashboard (`/dashboard`)
- Tarjetas de estadísticas: gastos semanales, mensuales, promedio diario
- Gráfico de pastel: gastos por categoría
- Gráfico de barras: gastos por método de pago
- Gráfico de tendencia: gastos diarios (últimos 14 días)

### Transacciones (`/transactions`)
- Lista completa de transacciones
- Filtros: fecha, categoría, método de pago, búsqueda de texto
- Acciones: validar, editar, eliminar transacciones
- Indicadores de estado (validado/pendiente)

### Nueva Transacción (`/new-transaction`)
- Formulario completo para crear transacciones manualmente
- Campos: monto, descripción, categoría, método de pago, fecha/hora, ubicación
- Validación de formulario

### Vista Admin (`/admin`)
- Estadísticas de todos los usuarios
- Tarjetas por usuario con totales y contadores
- Filtrado por usuario específico
- Vista agregada de todas las transacciones

## Autenticación

La autenticación se maneja mediante:

1. **Telegram Login Widget**: El usuario se autentica con su cuenta de Telegram
2. **LocalStorage**: Los datos del usuario se guardan localmente
3. **HTTP Headers**: El `telegram_user_id` se envía en cada request al backend
4. **Protected Routes**: Rutas protegidas que redirigen al login si no hay autenticación

## API Integration

El frontend consume la API REST del backend en `/api/v1`:

- `GET /api/v1/transactions` - Listar transacciones
- `POST /api/v1/transactions` - Crear transacción
- `PUT /api/v1/transactions/:id` - Actualizar transacción
- `DELETE /api/v1/transactions/:id` - Eliminar transacción
- `POST /api/v1/transactions/:id/validate` - Validar transacción
- `GET /api/v1/transactions/summary/:period` - Resumen por período
- `GET /api/v1/categories` - Listar categorías

## Notas de Desarrollo

### CORS
El backend debe permitir requests desde el origin del frontend. En desarrollo: `http://localhost:3000`

### Proxy API
Vite está configurado para hacer proxy de `/api` al backend, evitando problemas de CORS en desarrollo.

### React Query
Usamos TanStack Query para:
- Caché automático de datos
- Revalidación en background
- Manejo de estados de loading/error
- Invalidación de caché después de mutaciones

### Tailwind CSS
Usamos Tailwind para estilos con una paleta de colores personalizada (`primary-*`) en `tailwind.config.js`.

## Troubleshooting

### "Network Error" al hacer requests
- Verifica que el backend esté corriendo
- Revisa la variable `VITE_API_URL` en `.env`
- Chequea que CORS esté habilitado en el backend

### Telegram Login no funciona
- Verifica que `VITE_TELEGRAM_BOT_NAME` sea correcto
- Asegúrate de que el bot esté activo en Telegram
- Revisa la consola del navegador para errores

### No puedo acceder a la vista Admin
- Configura `VITE_ADMIN_USER_ID` con tu Telegram User ID
- Reinicia el servidor de desarrollo después de cambiar `.env`

## Licencia

Parte del proyecto MisPesos - Sistema de Gestión Financiera Personal
