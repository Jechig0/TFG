import { inject } from "@angular/core";
import { CanMatchFn, Route, Router, UrlSegment, UrlTree } from "@angular/router";



// Guardia que verifica si el usuario es administrador antes de permitir el acceso a ciertas rutas.
export const isAdminGuard: CanMatchFn = (
  route: Route,
  segments: UrlSegment[]
): boolean | UrlTree => {
  const router = inject(Router);
  const isAdmin = sessionStorage.getItem('isAdmin');

  if (isAdmin === 'true') {
    return true;
  }

  // Redirige a inicio devolviendo un UrlTree
  return router.parseUrl('/');
};
