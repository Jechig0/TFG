import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, EventEmitter, inject, Input, Output } from '@angular/core';

@Component({
  selector: 'subir-fichero',
  imports: [],
  templateUrl: './subir-fichero.component.html',
})
export class SubirFicheroComponent {

  alumnosService = inject(AlumnosService);

  @Output() datosExtraidos = new EventEmitter<AsignaturaNota[]>();

 
  onFileSelected(event: any) {
    console.log(event)
    const file: File = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file, file.name);

      this.alumnosService.enviarInformePdf(formData).subscribe(
        response => {
          console.log(response);
          this.datosExtraidos.emit(response)
        },
        error => console.error(error)
      );
    }
  }
}
