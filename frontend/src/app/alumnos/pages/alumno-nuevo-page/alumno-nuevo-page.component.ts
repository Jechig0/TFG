import { AfterViewInit, Component, inject, signal } from '@angular/core';
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { SubirFicheroComponent } from "../../components/subir-fichero/subir-fichero.component";
import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { ActivatedRoute } from '@angular/router';
import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { TablaNotasComponent } from "@/alumnos/components/tabla-notas/tabla-notas.component";

@Component({
  selector: 'alumno-nuevo-page',
  imports: [ListaAsignaturasComponent, FormsModule, SubirFicheroComponent, TablaNotasComponent],
  templateUrl: './alumno-nuevo-page.component.html',
})
export class AlumnoNuevoPageComponent implements AfterViewInit { 

  activatedRoute = inject(ActivatedRoute)
  alumnosService = inject(AlumnosService);


  alumnos = signal<[string, number][]>([]);
  // nuevaAsignatura = '';
  // nuevaNota: number | null = null;
  alumnoId = this.activatedRoute.snapshot.paramMap.get('id');

  ngAfterViewInit(): void {
  const almacenado = sessionStorage.getItem(`pdf-datos-${this.alumnoId}`);
  if (almacenado) {
    try {
      const datos: AsignaturaNota[] = JSON.parse(almacenado);
      this.cargarDesdeBackend(datos);
    } catch {
      console.warn('Datos inválidos en sessionStorage.');
    }
  }
}
  cargarDesdeBackend(datos: AsignaturaNota[]) {
    const nuevos = datos.map(item => [item.asignatura, +item.nota] as [string, number]);
    this.alumnos.set(nuevos);
  }
}
