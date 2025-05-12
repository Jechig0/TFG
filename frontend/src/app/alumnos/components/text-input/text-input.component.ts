import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'text-input',
  imports: [],
  templateUrl: './text-input.component.html',
})
export class TextInputComponent { 

  router = inject(Router)

  alumno = "0208F18506E41D3F29A4CAAD842FD0FA"

  goToAlumno() {
    this.router.navigate([`/alumno/${this.alumno}`])
  }
      

}
