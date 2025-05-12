import { Routes } from '@angular/router';
import { MainPageComponent } from '@alumnos/pages/main-page/main-page.component';
import { AlumnoPageComponent } from './alumnos/pages/alumno-page/alumno-page.component';

export const routes: Routes = [

    {
        path: '',
        component: MainPageComponent
    },

    {
        path:'alumno/:id',
        component: AlumnoPageComponent
    }
];
