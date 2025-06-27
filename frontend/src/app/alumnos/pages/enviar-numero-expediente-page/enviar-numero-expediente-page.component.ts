import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'enviar-numero-expediente',
  imports: [],
  templateUrl: './enviar-numero-expediente-page.component.html',
})
export class EnviarNumeroExpedienteComponent {

  router = inject(Router);

  goToNuevoAlumno(id: string) {
    this.router.navigate([`/nuevo-alumno/${id}`])
  }
}
