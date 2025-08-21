import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';
import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'main-page',
  templateUrl: './main-page.component.html',
  // styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit {
  private router = inject(Router);
  alumnoStateService = inject(AlumnoStateService)
  mensaje = '';
  textoBienvenida = 'Recomendador de Asignaturas';

  ngOnInit() {
    this.animarTexto();
  }

  animarTexto() {
    let i = 0;
    const intervalo = setInterval(() => {
      if (i < this.textoBienvenida.length) {
        this.mensaje += this.textoBienvenida[i];
        i++;
      } else {
        clearInterval(intervalo);
      }
    }, 80); // velocidad de escritura
  }

  goToIdentificacion() {
    if(this.alumnoStateService.getId() != null){
      this.router.navigate([`alumno/${this.alumnoStateService.getId()}`]);
    } else {
      this.router.navigate(['/alumno']);
    }
  }
}
