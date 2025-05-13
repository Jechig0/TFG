import { AlumnosService } from '@/alumnos/services/alumnos.service';
import {Component, inject, signal } from '@angular/core';
import {rxResource, toSignal} from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { TablaNotasComponent } from "../../components/tabla-notas/tabla-notas.component";

@Component({
  selector: 'app-alumno-page',
  imports: [ TablaNotasComponent],
  templateUrl: './alumno-page.component.html',
})
export class AlumnoPageComponent { 

  alumnosService = inject(AlumnosService)
  activatedRoute = inject(ActivatedRoute)

  alumnoId = this.activatedRoute.snapshot.params['id']
  mostrarTabla = signal<boolean>(false)

  alumnoResource = rxResource({
    request: () => ({id:this.alumnoId}),
    loader: ({request}) => {
      return this.alumnosService.getAlumnoById(request.id);
    }
  })

  mediaAlumno = toSignal(this.alumnosService.getMediaAlumno(this.alumnoId))

  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas()
    }
  })

}
