import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable, of, tap } from 'rxjs';
import { AsignaturaNota } from '../interfaces/pdfresponse.interface';
import { AlumnoStateService } from './alumno-state.service';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  apiUrl = environment.apiUrl

  private http = inject(HttpClient)
  alumnoStateService = inject(AlumnoStateService);

  // alumnos = signal<Record<string, [string, number][]>>({});
  // mediaAlumnos = signal<Record<string, string>>({});


  getAlumnoById(id: string): Observable<[string, number][]> {
  // const cache = this.alumnos();
  // if (cache[id]) {
  //   console.log('Cache hit for alumno:', id);
  //   return of(cache[id]); // Devuelve lo cacheado
  // }

  return this.http.get<[string, number][]>(`${this.apiUrl}/alumno/${id}`).pipe(
    map((data) => {
      const resultado = data.map(([asignatura, nota]) => [asignatura, +nota] as [string, number]);
      // this.alumnos.update(prev => ({ ...prev, [id]: resultado }));
      return resultado;
    })
    );
  }

  getMediaAlumno(id: string): Observable<string>{
  //   const cache = this.mediaAlumnos();
  //   if (cache[id]) {
  //     console.log('Cache hit for mediaAlumno:', id);
  //     return of(cache[id]);
  // }
    return this.http.get<string>(`${this.apiUrl}/alumno/${id}/media/`).pipe(
      map((media) => {
      // this.mediaAlumnos.update(prev => ({ ...prev, [id]: media }));
      return media;
    })
  );
  }

  verificarAlumno(id: string, dni:string): Observable<string>{
    return this.http.post<{estado: string}>(`${this.apiUrl}/alumno/verificar`, {
      id_alumno: id.trim(),
      dni: dni.trim().toUpperCase()
    }).pipe(
      map(response => response.estado)
);


  }

  getAsignaturas(id: string): Observable<string[][]>{
    return this.http.get<string[][]>(`${this.apiUrl}/asignatura/${id}`);
  }

  getProbabilidadAcceso(id:string, asignatura: string): Observable<number>{
    asignatura = asignatura.replace(/\s+/g, '')
    return this.http.get<number>(`${this.apiUrl}/alumno/probabilidadEntrada/${id}/${asignatura}`)
  }

  getAfinidadAsignatura(id:string, asignatura: string): Observable<number>{
    asignatura = asignatura.replace(/\s+/g, '')
    return this.http.get<number>(`${this.apiUrl}/alumno/afinidad/${id}/${asignatura}`)
  }

  enviarInformePdf(id: string, dni: string, file: File): Observable<AsignaturaNota[]> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dni', dni);

    return this.http.post<AsignaturaNota[]>(`${this.apiUrl}/alumno/${id}/subir-informe`, formData);
}

  eliminarAlumno(id:string): Observable<{estado: string}> {
    this.alumnoStateService.clear();
    return this.http.delete<{estado: string}>(`${this.apiUrl}/alumno/delete/${id}`);
  }
}
