import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'text-input',
  imports: [],
  templateUrl: './text-input.component.html',
})
export class TextInputComponent { 

  router = inject(Router)

  goToAlumno(id: string) {
    this.router.navigate([`/alumno/${id}`])
  }
      

}
