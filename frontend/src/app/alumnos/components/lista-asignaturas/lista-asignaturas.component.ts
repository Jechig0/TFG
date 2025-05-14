import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, inject } from '@angular/core';
import {rxResource, toSignal} from '@angular/core/rxjs-interop';

@Component({
  selector: 'lista-asignaturas',
  imports: [],
  templateUrl: './lista-asignaturas.component.html',
})
export class ListaAsignaturasComponent { 
  
  alumnosService = inject(AlumnosService)

  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas()
    }
  })

  datos: string[][] = [
    ["Matemáticas", "5"], ["Física", "6"], ["Matemáticas", "7"], ["Historia", "3"]
  ];
  asignaturas: string[] = [];
  opcionesFiltradas: string[] = [];
  asignaturaControl = new FormControl('');
  mostrarLista = false;

  ngOnInit() {
    this.asignaturas = Array.from(new Set(this.datos.map(d => d[0]))); // únicos
    this.asignaturaControl.valueChanges.subscribe(valor => {
      this.opcionesFiltradas = this.filtrarAsignaturas(valor || '');
    });
  }

  filtrarAsignaturas(valor: string): string[] {
    const filtro = valor.toLowerCase();
    return this.asignaturas.filter(asig => asig.toLowerCase().includes(filtro));
  }

  seleccionarAsignatura(asignatura: string) {
    console.log('Seleccionaste:', asignatura);
    this.mostrarLista = false;
    this.asignaturaControl.setValue(asignatura);
    // Aquí puedes ejecutar la lógica deseada con la asignatura
  }

  ocultarConRetraso() {
    setTimeout(() => this.mostrarLista = false, 200); // Permite hacer click antes de ocultar
  }


}
