import { NgClass } from '@angular/common';
import { Component, input } from '@angular/core';

@Component({
  selector: 'tabla-notas',
  imports: [NgClass],
  templateUrl: './tabla-notas.component.html',
})
export class TablaNotasComponent { 
  alumnos = input.required<[string, number][]>()
}
