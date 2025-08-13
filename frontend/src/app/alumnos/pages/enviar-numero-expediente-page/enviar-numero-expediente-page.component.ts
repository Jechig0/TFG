import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import Swal from 'sweetalert2';
import { AlumnosService } from '@/alumnos/services/alumnos.service';

@Component({
  selector: 'enviar-numero-expediente',
  templateUrl: './enviar-numero-expediente-page.component.html',
})
export class EnviarNumeroExpedienteComponent {

  router = inject(Router);
  http = inject(HttpClient);
  alumnosService = inject(AlumnosService)

  validarYRedirigir(codigo: string, dni: string) {
    const codigoLimpio = codigo.trim();
    const dniLimpio = dni.trim().toUpperCase();

    // Validar código alumno
    if (!/^\d{9}$/.test(codigoLimpio)) {
      Swal.fire({
        icon: 'error',
        title: 'Código inválido',
        text: 'El código debe tener exactamente 9 dígitos numéricos.',
      });
      return;
    }

    // Validar DNI (4 números + 1 letra)
    if (!/^\d{4}[A-Z]$/.test(dniLimpio)) {
      Swal.fire({
        icon: 'error',
        title: 'DNI inválido',
        text: 'Debes introducir los 4 últimos números y la letra en mayúscula (ej: 1234A).',
      });
      return;
    }

    // Mostrar animación de carga
    Swal.fire({
      title: 'Verificando datos...',
      text: 'Por favor, espera un momento.',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    // Consulta al backend
    this.alumnosService.getAlumnoById(codigoLimpio).subscribe({
      next: (res) => {
        Swal.close(); // Cerrar animación

        this.alumnosService.verificarAlumno(codigoLimpio, dniLimpio).subscribe({
          next: (existe) => {
            if (res && res.length > 0 && existe.existe) {
              this.router.navigate([`/alumno/${codigoLimpio}`]);
        }   else {
              this.router.navigate([`/nuevo-alumno/${codigoLimpio}`]);
        }
          }
        })

      },
      error: () => {
        Swal.close(); // Cerrar animación
        // Si no encuentra registros, ir a nuevo alumno
        this.router.navigate([`/nuevo-alumno/${codigoLimpio}`]);
      }
    });
  }
}
