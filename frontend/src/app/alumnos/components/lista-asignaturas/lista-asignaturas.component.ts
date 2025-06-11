import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, Validators } from '@angular/forms';
import {rxResource} from '@angular/core/rxjs-interop';
import { FilterByTextPipe } from '@/alumnos/pipes/filter-by-text.pipe';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'lista-asignaturas',
  imports: [ FormsModule, FilterByTextPipe],
  templateUrl: './lista-asignaturas.component.html',
})
export class ListaAsignaturasComponent {
  
  fb = inject(FormBuilder)
  alumnosService = inject(AlumnosService)
  activatedRoute = inject(ActivatedRoute)

  alumnoId = this.activatedRoute.snapshot.params['id']

  searchText = signal<string>('')
  selectedAsignatura = signal<string| null>(null)


  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas()
    }
  })

  asignaturaForm = this.fb.group({
    asignatura: ['', [Validators.required]]
  })

  onAsignaturaClick(asignatura: string) {
    this.selectedAsignatura.set(asignatura)
    this.searchText.set(asignatura)
    this.alumnosService.getProbabilidadAcceso(this.alumnoId, asignatura)
    this.alumnosService.getAfinidadAsignatura(this.alumnoId, asignatura)
  }
}
