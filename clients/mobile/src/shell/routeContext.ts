/** MOB-01 ADR-2 : contexte Metro isolé de l’orchestration, sans seconde entrée app. */
export const shellRoutes = (require as unknown as { context: (dir: string) => never }).context('../routes');
