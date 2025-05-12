import { AlumnosService } from '@/alumnos/services/alumnos.service';
import {Component, inject } from '@angular/core';
import {rxResource} from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-alumno-page',
  imports: [],
  templateUrl: './alumno-page.component.html',
})
export class AlumnoPageComponent { 

  alumnosService = inject(AlumnosService)
  activatedRoute = inject(ActivatedRoute)

  alumnoId = this.activatedRoute.snapshot.params['id']

  alumnoResource = rxResource({
    request: () => ({id:this.alumnoId}),
    loader: ({request}) => {
      return this.alumnosService.getAlumnoById(request.id);
    }
  })

}
