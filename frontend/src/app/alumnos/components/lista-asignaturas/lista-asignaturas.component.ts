import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, inject } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import {rxResource, toSignal} from '@angular/core/rxjs-interop';
import { NgClass } from '@angular/common';
import { FilterByTextPipe } from '@/alumnos/pipes/filter-by-text.pipe';

@Component({
  selector: 'lista-asignaturas',
  imports: [ReactiveFormsModule, FormsModule, FilterByTextPipe],
  templateUrl: './lista-asignaturas.component.html',
})
export class ListaAsignaturasComponent {
  
  fb = inject(FormBuilder)
  alumnosService = inject(AlumnosService)

  searchText: string = '';


  asignaturaResource = rxResource({
    loader: () => {
      return this.alumnosService.getAsignaturas()
    }
  })

  asignaturaForm = this.fb.group({
    asignatura: ['', [Validators.required]]
  })

  onSubmit() {
    throw new Error('Method not implemented.');
  } 
}
