import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'enviar-numero-expediente',
  imports: [],
  templateUrl: './enviar-numero-expediente-page.component.html',
})
export class EnviarNumeroExpedienteComponent {

  router = inject(Router);

  error = '';  // Para mostrar mensaje de error

  goToNuevoAlumno(id: string) {
    const idLimpio = id.trim();

    if (!/^\d{9}$/.test(idLimpio)) {
      this.error = 'El código debe tener exactamente 9 dígitos numéricos.';
      return;
    }

    this.error = '';
    this.router.navigate([`/nuevo-alumno/${idLimpio}`]);
  }
}
