import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filterByText',
  standalone: true
})
export class FilterByTextPipe implements PipeTransform {
  transform(asignaturas: string[], search: string): string[] {
    if (!search) return asignaturas;
    const lower = search.toLowerCase();
    return asignaturas.filter(asignatura =>
      asignatura.toLowerCase().includes(lower)
);

  }
}