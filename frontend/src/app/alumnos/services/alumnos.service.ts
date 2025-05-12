import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  private apiUrl = 'http://localhost:8000'

  private http = inject(HttpClient)

  getAlumnoById(id: string) {
    console.log('Acceso a API')
    return this.http.get(`${this.apiUrl}/alumno/${id}`);
  }
  
}
