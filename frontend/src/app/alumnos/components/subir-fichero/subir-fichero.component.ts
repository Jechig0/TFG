import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, EventEmitter, inject, Input, Output } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import Swal from 'sweetalert2';



@Component({
  selector: 'subir-fichero',
  imports: [],
  templateUrl: './subir-fichero.component.html',
})
export class SubirFicheroComponent {

  activatedRoute = inject(ActivatedRoute);
  alumnosService = inject(AlumnosService);

  alumnoId = this.activatedRoute.snapshot.paramMap.get('id');


  @Output() datosExtraidos = new EventEmitter<AsignaturaNota[]>();

 
  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      const formData = new FormData();
      formData.append('file', file);

      this.alumnosService.enviarInformePdf(this.alumnoId!, formData).subscribe({
        next: (response) => {
          // Guardar en sessionStorage
          sessionStorage.setItem(`pdf-datos-${this.alumnoId}`, JSON.stringify(response));
          // Emitir para mostrar
          this.datosExtraidos.emit(response);
        },
        error: (err) => {
          // Si el backend mandó "detail", úsalo en el mensaje
          const mensaje = err?.error?.detail || 'Error al procesar el PDF.';
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje,
            confirmButtonColor: '#d33'
          });
        }
      });
    }
  }
}
