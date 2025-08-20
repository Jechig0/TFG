import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, effect , computed, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, Validators } from '@angular/forms';
import {rxResource} from '@angular/core/rxjs-interop';
import { FilterByTextPipe } from '@/alumnos/pipes/filter-by-text.pipe';
import { ActivatedRoute } from '@angular/router';
import { PercentPipe } from '@angular/common';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'lista-asignaturas',
  imports: [FormsModule, FilterByTextPipe, PercentPipe],
  templateUrl: './lista-asignaturas.component.html',
})
export class ListaAsignaturasComponent {
  
  fb = inject(FormBuilder)
  alumnosService = inject(AlumnosService)
  activatedRoute = inject(ActivatedRoute)

  alumnoId = this.activatedRoute.snapshot.params['id']

  searchText = signal<string>('')
  selectedAsignatura = signal<string| null>(null)
  probabilidadAccesoSignal = signal<number | null> (null)
  afinidadAsignaturaSignal = signal<number| null> (null)
  isLoading= signal<boolean>(false)


  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas(this.alumnoId)
    }
  })

  async onAsignaturaClick(asignatura: string) {
  this.selectedAsignatura.set(asignatura);
  this.searchText.set(asignatura);

  this.isLoading.set(true);

  await Promise.all([
    this.probabilidadAcceso(asignatura),
    this.afinidadAsignatura(asignatura),
  ]);

  this.isLoading.set(false);
  }

  async probabilidadAcceso(asignatura: string) {
  this.probabilidadAccesoSignal.set(null);
  let probabilidad = await firstValueFrom(
    this.alumnosService.getProbabilidadAcceso(this.alumnoId, asignatura)
  );
  this.probabilidadAccesoSignal.set(probabilidad);
}


  async afinidadAsignatura(asignatura:string){
    this.afinidadAsignaturaSignal.set(null)
    const afinidad = await firstValueFrom(
      this.alumnosService.getAfinidadAsignatura(this.alumnoId, asignatura)
    );
    console.log('afinidad', afinidad)
    this.afinidadAsignaturaSignal.set(afinidad)
  }

}
