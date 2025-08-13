import { Routes } from '@angular/router';

export const routes: Routes = [

    {
        path: '',
        loadComponent: () => import('./alumnos/pages/main-page/main-page.component').then(m => m.MainPageComponent)
    },

    {
        path:'alumno/:id',
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
        path:'**',
        redirectTo: ''
    }
];
