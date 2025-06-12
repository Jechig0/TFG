import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  apiUrl = environment.apiUrl

  private http = inject(HttpClient)

  getAlumnoById(id: string): Observable<string[][]> {
    console.log('Acceso a API')
    return this.http.get<string[][]>(`${this.apiUrl}/alumno/${id}`);
  }

  getMediaAlumno(id: string): Observable<string>{
    return this.http.get<string>(`${this.apiUrl}/media/${id}`);
  }

  getAsignaturas(): Observable<string[][]>{
    return this.http.get<string[][]>(`${this.apiUrl}/asignaturas`);
  }
  
  getProbabilidadAcceso(id:string, asignatura: string): Observable<number>{
    asignatura = asignatura.replace(/\s+/g, '')
    console.log('Endpoint Probabilidad llamado')
    const url = `${this.apiUrl}/probabilidadEntrada/${id}/${asignatura}`
    console.log(url)
    return this.http.get<number>(`${this.apiUrl}/probabilidadEntrada/${id}/${asignatura}`)
  }

  getAfinidadAsignatura(id:string, asignatura: string): Observable<number>{
    return this.http.get<number>(`${this.apiUrl}/afinidad/${id}/${asignatura}`)  }
}
