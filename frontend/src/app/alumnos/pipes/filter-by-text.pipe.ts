import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filterByText',
  standalone: true
})
export class FilterByTextPipe implements PipeTransform {
  transform(asignaturas: string[], search: string): string[] {
    //Si no hay texto de búsqueda, devuelve todas las asignaturas
    if (!search) return asignaturas;

    //Convierte el texto de búsqueda y la asignatura a minúsculas y filtra las asignaturas usando includes para que busque coincidencias sin importar la posición en la cadena
    const lower = search.toLowerCase();
    return asignaturas.filter(asignatura =>
      asignatura.toLowerCase().includes(lower)
);

  }
}