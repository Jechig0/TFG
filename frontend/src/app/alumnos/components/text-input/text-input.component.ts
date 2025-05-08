import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, inject } from '@angular/core';

@Component({
  selector: 'text-input',
  imports: [],
  templateUrl: './text-input.component.html',
})
export class TextInputComponent { 

  resultado:any

  alumnosService = inject(AlumnosService)
  alumno = "0208F18506E41D3F29A4CAAD842FD0FA"
  consultarAlumno() {
    this.alumnosService.enviarCodigoAlumno(this.alumno).subscribe({
      next: (res) => {
        this.resultado = res;
      },
      error: (err) => {
        console.error(err);
      }
    });
  }
}
