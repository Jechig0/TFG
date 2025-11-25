import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';
import { Component, EventEmitter, inject, Input, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';



@Component({
  selector: 'subir-fichero',
  imports: [],
  templateUrl: './subir-fichero.component.html',
})
export class SubirFicheroComponent {

  activatedRoute = inject(ActivatedRoute);
  alumnosService = inject(AlumnosService);
  alumnoStateService = inject(AlumnoStateService);
  router = inject(Router);

  alumnoId = this.activatedRoute.snapshot.paramMap.get('id');


  @Output() datosExtraidos = new EventEmitter<AsignaturaNota[]>();


  dni = this.alumnoStateService.getDni();

  // Maneja la selección de un fichero, enviándolo al backend para su procesamiento.
  // Y redirigiendo según el resultado.
  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];

      this.alumnosService.enviarInformePdf(this.alumnoId!, this.dni!, file).subscribe({
        next: (resp) => {
          Swal.fire('Éxito', 'Expediente cargado correctamente.', 'success');
          this.datosExtraidos.emit(resp);
          this.alumnoStateService.setAlumno(this.alumnoId!, this.dni!);
          this.router.navigate([`/alumno/${this.alumnoId}`]);
        },
        error: (err) => {
          this.alumnoStateService.clear();
          Swal.fire('Error', err.error.detail || 'No se pudo procesar el PDF.', 'error');
          this.router.navigate([`/`]);
        }
      });
    }
  }
}


