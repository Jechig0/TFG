import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  private apiUrl = 'http://localhost:8000'

  private http = inject(HttpClient)

  enviarCodigoAlumno(codigo: string) {
    console.log({codigo},)
    return this.http.post(this.apiUrl, { codigo_alumno: codigo });
  }
  
}
