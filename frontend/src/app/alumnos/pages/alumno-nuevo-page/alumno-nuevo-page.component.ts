import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ListaAsignaturasComponent } from "../../components/lista-asignaturas/lista-asignaturas.component";
import { FormsModule } from '@angular/forms';
import { NgClass, NgFor } from '@angular/common';
import { SubirFicheroComponent } from "../../components/subir-fichero/subir-fichero.component";
import { AsignaturaNota } from '@/alumnos/interfaces/pdfresponse.interface';
import { ActivatedRoute } from '@angular/router';
import { rxResource } from '@angular/core/rxjs-interop';
import { AlumnosService } from '@/alumnos/services/alumnos.service';

@Component({
  selector: 'alumno-nuevo-page',
  imports: [ListaAsignaturasComponent, FormsModule, NgClass, SubirFicheroComponent],
  templateUrl: './alumno-nuevo-page.component.html',
})
export class AlumnoNuevoPageComponent  { 

  activatedRoute = inject(ActivatedRoute)
  alumnosService = inject(AlumnosService);


  alumnos = signal<[string, number][]>([]);
  // nuevaAsignatura = '';
  // nuevaNota: number | null = null;
  alumnoId = this.activatedRoute.snapshot.paramMap.get('id');

  // alumnoResource = rxResource({
  //   request: () => ({id:this.alumnoId}),
  //   loader: ({request}) => {
  //     return this.alumnosService.getAlumnoById(request.id!);
  //   },
  // })

  // ngOnInit(): void {
  //   this.alumnoResource.reload();
  //   console.log('Alumno Nuevo Page - ngOnInit');
  //   if (this.alumnoResource.hasValue()) {
  //     const alumno = this.alumnoResource.value;
  //     console.log('Alumno Nuevo Page', alumno);
  //     this.alumnos.set(alumno().map(item => [item[0], +item[1]] as [string, number]));
  //   }
  // }

  // agregarFila() {
  //   if (this.nuevaAsignatura.trim() && this.nuevaNota !== null) {
  //     this.alumnos.update((actual) => [
  //       ...actual,
  //       [this.nuevaAsignatura.trim(), +this.nuevaNota!],
  //     ]);
  //     this.nuevaAsignatura = '';
  //     this.nuevaNota = null;
  //   }
  // }

  cargarDesdeBackend(datos: AsignaturaNota[]) {
    const nuevos = datos.map(item => [item.asignatura, +item.nota] as [string, number]);
    this.alumnos.set(nuevos);
  }
}
