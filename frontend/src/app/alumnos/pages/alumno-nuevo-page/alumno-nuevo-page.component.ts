import { Component, computed, inject, signal } from '@angular/core';
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";
import { FormsModule } from '@angular/forms';
import { NgClass, NgFor } from '@angular/common';
import { SubirFicheroComponent } from "../../components/subir-fichero/subir-fichero.component";
import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'alumno-nuevo-page',
  imports: [ListaAsignaturasComponent, FormsModule, NgClass, SubirFicheroComponent],
  templateUrl: './alumno-nuevo-page.component.html',
})
export class AlumnoNuevoPageComponent { 

  activatedRoute = inject(ActivatedRoute)


  alumnos = signal<[string, number][]>([]);
  nuevaAsignatura = '';
  nuevaNota: number | null = null;
  alumnoId = this.activatedRoute.snapshot.paramMap.get('id');

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

  cargarDesdeBackend(datos: AsignaturaNota[]) {
    const nuevos = datos.map(item => [item.asignatura, +item.nota] as [string, number]);
    this.alumnos.set(nuevos);
  }
}
