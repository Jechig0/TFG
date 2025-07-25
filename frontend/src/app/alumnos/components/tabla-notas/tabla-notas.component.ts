import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { NgClass, PercentPipe } from '@angular/common';
import { Component, inject, input } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'tabla-notas',
  imports: [NgClass],
  templateUrl: './tabla-notas.component.html',
})
export class TablaNotasComponent { 
  alumnos = input.required<[string, number][]>()
  mediaAlumno = input.required<String>()
}
