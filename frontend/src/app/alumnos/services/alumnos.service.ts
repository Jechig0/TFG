import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { Observable } from 'rxjs';

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
  
  getProbabilidadAcceso(id:string, asignatura: string){

  }

  getAfinidadAsignatura(id:string, asignatura: string){
    
  }
}
