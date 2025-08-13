import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable, of, tap } from 'rxjs';
import { AsignaturaNota } from '../interfaces/pdfresponse.interface';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  apiUrl = environment.apiUrl

  private http = inject(HttpClient)

  alumnos = signal<Record<string, [string, number][]>>({});
  mediaAlumnos = signal<Record<string, string>>({});


  getAlumnoById(id: string): Observable<[string, number][]> {
  const cache = this.alumnos();
  if (cache[id]) {
    console.log('Cache hit for alumno:', id);
    return of(cache[id]); // Devuelve lo cacheado
  }

  return this.http.get<[string, number][]>(`${this.apiUrl}/alumno/${id}`).pipe(
    map((data) => {
      const resultado = data.map(([asignatura, nota]) => [asignatura, +nota] as [string, number]);
      this.alumnos.update(prev => ({ ...prev, [id]: resultado }));
      return resultado;
    })
    );
  }

  getMediaAlumno(id: string): Observable<string>{
    const cache = this.mediaAlumnos();
    if (cache[id]) {
      console.log('Cache hit for mediaAlumno:', id);
      return of(cache[id]);
  }
    return this.http.get<string>(`${this.apiUrl}/alumno/${id}/media/`).pipe(
      map((media) => {
      this.mediaAlumnos.update(prev => ({ ...prev, [id]: media }));
      return media;
    })
  );
  }

  verificarAlumno(id: string, dni:string): Observable<{existe: boolean}>{
    return this.http.post<{existe: boolean}>(`${this.apiUrl}/verificar`, {
    id_alumno: id,
    dni: dni
  });

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

  enviarInformePdf(id:string ,file: FormData): Observable<AsignaturaNota[]> {
    return this.http.post<AsignaturaNota[]>(`${this.apiUrl}/alumno/${id}/subir-informe`, file)
  }
}
