import { inject } from "@angular/core";
import { CanMatchFn, Route, Router, UrlSegment, UrlTree } from "@angular/router";




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