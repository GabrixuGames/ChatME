# workflow.md - Flujo de Trabajo del Equipo

## 1. Inicio de Proyecto
1. **PM** recibe requisitos y crea brief del proyecto
2. **PM** define alcance, prioridades y timeline
3. **Designer** propone wireframes y mockups iniciales
4. **FullstackDev** revisa viabilidad técnica
5. Reunión de kick-off con todos los agentes

## 2. Fase de Diseño
1. **Designer** crea diseño detallado (UI/UX)
2. **FrontendSenior** revisa accesibilidad y factibilidad
3. **Designer** ajusta según feedback
4. **PM** aprueba diseño final

## 3. Fase de Desarrollo

### Backend
1. **BackendSenior** define arquitectura y estructura de datos
2. **BackendJunior** implementa endpoints y lógica
3. **BackendSenior** revisa código y optimiza
4. **QA** realiza tests de API

### Frontend
1. **FrontendSenior** define estructura de componentes
2. **FrontendJunior** implementa UI según diseño
3. **FrontendSenior** revisa y optimiza performance
4. **QA** realiza tests de interfaz

### Integración
1. **FullstackDev** coordina integración frontend-backend
2. **FullstackDev** resuelve problemas de comunicación entre capas
3. **QA** realiza tests de integración end-to-end

## 4. Fase de Testing
1. **QA** ejecuta plan de pruebas completo
2. **QA** reporta bugs a los desarrolladores correspondientes
3. Desarrolladores corrigen issues
4. **QA** valida correcciones
5. Ciclo se repite hasta aprobación

## 5. Fase de Documentación
1. **DocWriter** documenta APIs y endpoints
2. **DocWriter** crea guías de usuario
3. **DocWriter** genera README y docs técnicas
4. **PM** revisa que la documentación esté completa

## 6. Fase de Despliegue
1. **DevOps** prepara entorno de staging
2. **QA** valida en staging
3. **DevOps** configura CI/CD pipeline
4. **DevOps** despliega a producción
5. **PM** monitorea lanzamiento
6. **DevOps** configura monitoreo y alertas

## 7. Mantenimiento Post-Lanzamiento
1. **DevOps** monitorea métricas y logs
2. **QA** valida reportes de usuarios
3. Desarrolladores aplican hotfixes si es necesario
4. **PM** prioriza nuevas features/mejoras

## Ciclos de Revisión

### Daily
- Quick sync de avances entre agentes activos
- Identificación de blockers

### Semanal
- **PM** revisa progreso general
- **Seniors** revisan código de juniors
- **QA** reporta estado de testing

### Por Feature
- Code review obligatorio por senior correspondiente
- Aprobación de **PM** antes de merge
- Validación de **QA** antes de considerar completado

## Gestión de Cambios
1. Cambios menores: aprobación de senior del área
2. Cambios mayores: aprobación de **PM** y **FullstackDev**
3. Cambios de arquitectura: reunión con todos los seniors
4. Todos los cambios deben documentarse

## Resolución de Conflictos
1. Desarrolladores intentan resolver técnicamente
2. Si persiste, escala a **FullstackDev**
3. Si impacta scope/timeline, escala a **PM**
4. **PM** tiene decisión final en caso de empate
