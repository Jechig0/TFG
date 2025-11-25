import { inject } from "@angular/core";
import { CanMatchFn, Route, Router, UrlSegment, UrlTree } from "@angular/router";



// Guardia que verifica si el usuario NO está autenticado antes de permitir el acceso a ciertas rutas.
export const NotAuthenticatedGuard: CanMatchFn = (
  route: Route,
  segments: UrlSegment[]
): boolean | UrlTree => {
  const router = inject(Router);
  const isAuthenticated = sessionStorage.getItem('id_alumno') || sessionStorage.getItem('isAdmin');

  if (isAuthenticated) {
    return router.parseUrl('/'); // si ya está logueado redirige a home
  }

  return true;
};
