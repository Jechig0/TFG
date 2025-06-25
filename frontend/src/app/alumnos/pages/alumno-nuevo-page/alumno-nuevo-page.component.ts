import { Component, computed, signal } from '@angular/core';
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";
import { FormsModule } from '@angular/forms';
import { NgClass, NgFor } from '@angular/common';

@Component({
  selector: 'alumno-nuevo-page',
  imports: [ListaAsignaturasComponent, FormsModule, NgClass],
  templateUrl: './alumno-nuevo-page.component.html',
})
export class AlumnoNuevoPageComponent { 
  alumnos = signal<[string, number][]>([]);
  nuevaAsignatura = '';
  nuevaNota: number | null = null;

  agregarFila() {
    if (this.nuevaAsignatura.trim() && this.nuevaNota !== null) {
      this.alumnos.update((actual) => [
        ...actual,
        [this.nuevaAsignatura.trim(), +this.nuevaNota!],
      ]);
      this.nuevaAsignatura = '';
      this.nuevaNota = null;
    }
  }

  mediaAlumno = computed(() => {
    const lista = this.alumnos();
    if (lista.length === 0) return 0;
    const suma = lista.reduce((acc, [, nota]) => acc + nota, 0);
    return (suma / lista.length).toFixed(2);
  });
}
