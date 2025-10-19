import { Routes } from '@angular/router';
import { isAdminGuard } from './alumnos/guards/is-admin.guard';
import { AuthenticatedGuard } from './alumnos/guards/authenticated.guard';
import { NotAuthenticatedGuard } from './alumnos/guards/not-authenticated.guard';

export const routes: Routes = [

    {
        path: '',
        loadComponent: () => import('./alumnos/pages/main-page/main-page.component').then(m => m.MainPageComponent)
    },

    {
        path:'alumno/:id',
        canMatch: [AuthenticatedGuard],
        loadComponent: () => import('./alumnos/pages/alumno-page/alumno-page.component').then(m => m.AlumnoPageComponent)
    },

    {
        path: 'alumno',
        loadComponent: () => import('./alumnos/pages/enviar-numero-expediente-page/enviar-numero-expediente-page.component').then(m => m.EnviarNumeroExpedienteComponent)
    },

    {
        path:'nuevo-alumno/:id',
        loadComponent: () => import('./alumnos/pages/alumno-nuevo-page/alumno-nuevo-page.component').then(m => m.AlumnoNuevoPageComponent)
    },

    {
        path: 'admin/login',
        canMatch: [NotAuthenticatedGuard],
        loadComponent: () => import('./auth/pages/admin-login-page/admin-login-page.component').then(m => m.AdminLoginPageComponent)
    },

    {
        path: 'admin',
        canMatch: [isAdminGuard],
        loadComponent: () => import('./auth/pages/admin-page/admin-page.component').then(m => m.AdminPageComponent)
    },

    {
        path: 'faq',
        loadComponent: () => import('./alumnos/pages/faq-page/faq-page.component').then(m => m.FaqPageComponent)
    },

    {
        path:'**',
        redirectTo: ''
    }
];
