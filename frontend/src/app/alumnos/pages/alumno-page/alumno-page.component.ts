import { AlumnosService } from '@/alumnos/services/alumnos.service';
import {Component, inject, signal } from '@angular/core';
import {rxResource, toSignal} from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { TablaNotasComponent } from "../../components/tabla-notas/tabla-notas.component";
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";
import Swal from 'sweetalert2';
import { delay } from 'rxjs';

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
  mostrarTabla = signal<boolean>(true)

  alumnoResource = rxResource({
    request: () => ({id:this.alumnoId}),
    loader: ({request}) => {
      return this.alumnosService.getAlumnoById(request.id);
    }
  })

  mediaAlumno = toSignal(this.alumnosService.getMediaAlumno(this.alumnoId))

  actualizarExpediente() {
    this.router.navigate([`/nuevo-alumno/${this.alumnoId}`]);
  }

  borrarExpediente() {
    Swal.fire({
      title: '¿Estás seguro?',
      text: `Se eliminará el expediente del alumno ${this.alumnoId}`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, borrar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        this.alumnosService.eliminarAlumno(this.alumnoId).subscribe({
          next: () => {
            Swal.fire('Eliminado', 'El expediente ha sido borrado correctamente.', 'success');
            this.router.navigate(['/']); // Redirige al inicio
          },
          error: (err) => {
            Swal.fire('Error', err.error?.detail || 'No se pudo borrar el expediente.', 'error');
          }
        });
      }
    });
  }
}
