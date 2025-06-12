import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, effect , computed, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, Validators } from '@angular/forms';
import {rxResource} from '@angular/core/rxjs-interop';
import { FilterByTextPipe } from '@/alumnos/pipes/filter-by-text.pipe';
import { ActivatedRoute } from '@angular/router';
import { PercentPipe } from '@angular/common';

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
  probabilidadEntrada = signal<number | null> (null)
  afinidadAsignatura = signal<number| null> (null)
  buscando = computed<boolean>(() => this.searchText() == this.selectedAsignatura())


  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas()
    }
  })

  onAsignaturaClick(asignatura: string) {
    this.selectedAsignatura.set(asignatura)
    this.searchText.set(asignatura)
    this.alumnosService.getProbabilidadAcceso(this.alumnoId, asignatura).subscribe({
      next: (res) => this.probabilidadEntrada.set(res)
    })
    this.alumnosService.getAfinidadAsignatura(this.alumnoId, asignatura).subscribe({
      next: (afinidad) => this.afinidadAsignatura.set(afinidad)
    })
  }

  controlarBusqueda(){
    if(!this.buscando()){
      this.probabilidadEntrada.set(null)
      this.afinidadAsignatura.set(null)
    }
  }

}
