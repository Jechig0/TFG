import { inject } from "@angular/core";
import { CanMatchFn, Route, Router, UrlSegment, UrlTree } from "@angular/router";




export const AuthenticatedGuard: CanMatchFn = (
  route: Route,
  segments: UrlSegment[]
): boolean | UrlTree => {
  const router = inject(Router);
  const isAuthenticated = sessionStorage.getItem('id_alumno') || sessionStorage.getItem('isAdmin');

  if (isAuthenticated) {
    return true;
  }

  return router.parseUrl('/');
};
