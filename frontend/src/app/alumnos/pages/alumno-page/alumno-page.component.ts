import { AlumnosService } from '@/alumnos/services/alumnos.service';
import {Component, inject, signal } from '@angular/core';
import {rxResource, toSignal} from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { TablaNotasComponent } from "../../components/tabla-notas/tabla-notas.component";
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";

@Component({
  selector: 'app-alumno-page',
  imports: [TablaNotasComponent, ListaAsignaturasComponent],
  templateUrl: './alumno-page.component.html',
})
export class AlumnoPageComponent {

  alumnosService = inject(AlumnosService)
  activatedRoute = inject(ActivatedRoute)

  router = inject(Router)

  alumnoId = this.activatedRoute.snapshot.params['id']
  mostrarTabla = signal<boolean>(false)

  alumnoResource = rxResource({
    request: () => ({id:this.alumnoId}),
    loader: ({request}) => {
      return this.alumnosService.getAlumnoById(request.id);
    }
  })

  mediaAlumno = toSignal(this.alumnosService.getMediaAlumno(this.alumnoId))

  goToInsert() {
    this.router.navigate(['/nuevo-alumno'])
  }

}
